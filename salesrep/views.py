from django.shortcuts import render,redirect
from . import models
from django.contrib import messages
from .forms import ItemFormset,OrderIntakeForm
from rest_framework.views import APIView, Response

from datetime import datetime,timedelta
from .serializers import OrderHistSerializer

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# class CustomSearchFilter(filters.FilterSet): # write on gfg
#     date = filters.DateFilter(field_name="order_time",lookup_expr="date",help_text="yyyy-mm-dd")
#     class Meta:
#         model = models.OrderIntake
        
#         fields = ['date','team','status']
    
def place_order(request,order_num):
    try:
        ordr=models.OrderIntake.objects.get(order_num=order_num)
    except models.OrderIntake.DoesNotExist:
        messages.warning(request,'Order doesnot exists')
        return redirect('salesrep:create_order')
    order_inst=models.OrderIntake.objects.get(order_num=order_num)
    team=order_inst.team
    r_time=0
    pend_q=models.OrderIntake.objects.filter(status='Pending',team=team).order_by('-created_time')
    if pend_q is not None:
        for i in pend_q:
            # if i.estimated_time>datetime.now():
            if i.distance>5:
                r_time+=timedelta(minutes=40)
            else:
                r_time+=timedelta(minutes=20)
 
    item_formset=ItemFormset(request.POST or None,instance=order_inst)
    order_form=OrderIntakeForm(request.POST or None,instance=order_inst)
    if item_formset.is_valid() and order_form.is_valid():
        order_inst=order_form.save(commit=False)
        team=order_inst.team
        if order_inst.distance<=5:
            team=order_inst.team
            order_inst.estimated_time=order_inst.order_time+ timedelta(minutes=r_time)+timedelta(minutes=40) # add dist time
        else:
            order_inst.estimated_time=order_inst.order_time+timedelta(minutes=r_time)+timedelta(minutes=60) # add dist time
        for i in item_formset:
            order_inst.total_price+=int(i.instance.price)
        order_form.save()
        order_form.save_m2m() # might not be required
        messages.success(request,"Order Placed!")
        return redirect("salesrep:order_history") 
    
    return render(request,"salesrep\place_order.html",context={"itemformset":item_formset,"order_form":order_form,"order_number":ordr.order_num})      

class OrderHistoryAPI(APIView):
    '''
    Generates PDF report for today's orders
    '''

    def get(self,request,format=None):
        date_today=datetime.today().date()
        orders=models.OrderIntake.objects.filter(order_time__date=date_today)
        template_path = 'salesrep/report.html'
        context = {'orders': orders}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = ' filename="{}.pdf"'.format(date_today)

        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(
        html, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response

def order_history(request): # geenrate report at this view
    query=models.OrderIntake.objects.all().order_by('-order_time')
    return render(request,"salesrep\order_history.html",context={"orders":query})

class OrderStatusApi(APIView):
    def get(self,request,format=None):
        '''
        Provide data={'order_num':order_num}
        '''
        order_num=request.data['order_num']
        try:
            stat=OrderIntake.objects.get(order_num=order_num).status
        except OrderIntake.DoesNotExist:
            return Response({
            'message':'Order Doesnot Exists'
            })
        return Response({
            'message':stat
        })
    def post(self,request,format=None):
        '''
        Requires data={'order_num':order_num,'status':[one from Pending,WithDrawn,Rejected,Delivered]}
        '''
        order_num=request.data['order_num']
        status=request.data['status']
        try:
            OrderIntake.objects.get(order_num=order_num).status=status
        except:
            return Response({
            'message':'Order Doesnot Exists'
        })
        else:
            return Response({
            'message':'Status Updated'
        })

class CheckInventoryAPI(APIView):
    permission_classes = []
    def get(self,request,format=None,**kwargs): # JsonResponse could be used as well
        '''
        Requires data={'model_num','quantity','order_num'}
        '''
        try:
            model_num=request.data['model_num']
            quantity=request.data['quantity']
            order_num=request.data['order_num']
        except:
            return Response({
                "message":"Include model_num,quantity and order_num"
            })
        try:
            query=models.Inventory.objects.get(model_num=model_num)
        except models.Inventory.DoesNotExist:
            return Response({
                'message':'Item Not Available'
            })
        else:
            if quantity>query.avail:
                return Response({
                    'message':'Requested quantity not availaible'
                })
            else:
                try: # to delete already added item, also add js to disable add to cart
                    c=models.ItemsIntake.objects.filter(item=model_num,order=ordr)
                    c.delete()
                except models.ItemsIntake.DoesNotExist:
                    pass
                models.ItemsIntake.objects.create(item=model_num,quantity=quantity,price=price,order=order_items__order_num)
                # add to cart in fronted over here
                return Response({
                    'message':'Added to cart' 
                })

class AddOrderApi(APIView):
    '''
    Creates an order instance and returns its order_num in response
    '''
    def post(self,request,format=None):
        try:
            ordr=models.OrderIntake.objects.create()
        except:
            return Response({'order_num':'An Error Ocurred'})
        return Response({'order_num':ordr.order_num})

def create_order(request):
    if request.method=='POST':
        ordr=models.OrderIntake.objects.create()
        return redirect('salesrep:check_inventory',order_num=ordr.order_num) # add items to cart
    else:
        return render(request,"salesrep\create_order.html",context={})
    return render(request,"salesrep\create_order.html",context={})

def check_inventory(request,order_num):
    try:
        ordr=models.OrderIntake.objects.get(order_num=order_num)
    except models.OrderIntake.DoesNotExist:
        messages.warning(request,'Order doesnot exists')
        return redirect('salesrep:create_order')
    inventories=models.Inventory.objects.all().order_by('category')
    if request.method=='POST':
        model_num=request.POST.get('modelnum')
        quantity=int(request.POST.get('quantity'))
        try:
            x = models.Inventory.objects.get(model_num=model_num)
        except models.Inventory.DoesNotExist:
            messages.warning(request,"Item is not available")
            return redirect('salesrep:check_inventory',order_num=order_num)
        else:
            # check number of availability
            if quantity>x.avail:
                messages.warning(request,f"Requested quantity not availaible")
                return redirect('salesrep:check_inventory',order_num=order_num)
            # add to Cart 
            price=x.price*quantity
            
            try: # to delete already added item, also add js to disable add to cart
                c=models.ItemsIntake.objects.filter(item=model_num,order=ordr)
                c.delete()
            except models.ItemsIntake.DoesNotExist:
                pass
            models.ItemsIntake.objects.create(item=model_num,quantity=quantity,price=price,order=ordr) # Item can be removed from Place order
            messages.success(request,f"Added {quantity} {model_num} to Cart")
            return redirect('salesrep:check_inventory',order_num=order_num)
    
    return render(request,"salesrep\inventory.html",context={'inventories':inventories,'order_num':order_num}) 
        

def delete_order(request,order_num):
    
    try:
        ordr=models.OrderIntake.objects.get(order_num=order_num)
    except models.OrderIntake.DoesNotExist:
        messages.warning(reqeuest,'Order Doesnot Exists')
        return redirect('salesrep:create_order')
    else:
        items=models.ItemsIntake.objects.filter(order__order_num=order_num)
        items.delete()
        ordr.delete()
    messages.warning(request,'Order Deleted')
    return redirect('salesrep:create_order')

class OrderAPi(APIView):
    '''
    To delete order send a delete request,get and post data is rendered through django forms.
    '''
    # TO delete order give a DELETE request, curl -X DELETE "http://127.0.0.1:8000/place_order/order_num/"
    permission_classes = []
    authentication_classes = []
    def delete(self,request,order_num,format=None):
        try:
            ordr=models.OrderIntake.objects.get(order_num=order_num)
        except models.OrderIntake.DoesNotExist:
            return Response(
                {"message":"Order Doesnot Exists"}
            )
        else:
            items=models.ItemsIntake.objects.filter(order__order_num=order_num)
            items.delete()
            ordr.delete()
        return Response(
                {"message":"Order has been Deleted"}

            )
    
    def get(self,request,order_num,format=None):
        # should be used to render serialized forms here
        pass
    def post(self,request,order_num,format=None):
        # should be used to save data of each form here
        pass