from django.db import models
from django.db.models import Avg, Count, Min, Sum
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
import pytz
timeZ_Ny = pytz.timezone('Asia/Kolkata')
from collections import deque
team_q = deque(['Team A','Team B'])
teams=(
    ("A","Team A"),
    ("B","Team B"),
)

statuses=(
    ("Pending","Delivery Pending"),
    ("WithDrawm","Rejected by Company"),
    ("Rejected","Rejected by customer"),
    ("Delivered","Delivery completed"),
)

counter=1 # server needs to be running for creating unique order_num

def check_today():
    try:
        vx=OrderIntake.objects.latest().order_time.date()
        date_today=datetime.today().date()
    except OrderIntake.DoesNotExist:
        return False
    else:
        if date_today == vx:
            return True
        else:
            return False

def get_ord_date():
    global counter
    if check_today() == True:
        counter+=1
    else:
        counter=1
    return counter
def get_team():
        t = team_q.pop()
        team_q.appendleft(t)
        return t
class RangeField(models.FloatField): # write on gfg
    description = _("Integer field with range")
    def __init__(self,min_val,max_val,*args,**kwargs): 
        self.min_val=min_val
        self.max_val=max_val
        super().__init__(*args, **kwargs)
        
    def formfield(self, **kwargs):
    
        min_value=self.min_val
        max_value=self.max_val
        return super().formfield(**{
            'min_value': min_value,
            'max_value': max_value,
            **kwargs,
        })
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
 
        kwargs['min_val']=self.min_val
        kwargs['max_val']=self.max_val

        return name, path, args, kwargs     


    def rel_db_type(self, connection):
        if connection.features.related_fields_match_type:
            return self.db_type(connection)
        else:
            return models.FloatField().db_type(connection=connection)
  

# Create your models here.
class OrderIntake(models.Model):
    order_num=models.CharField(default='OrderNumber',max_length=100,editable=False)
    order_id=models.IntegerField(default=0,null=True)
    cust_name=models.CharField(default='',max_length=60)
    cust_add=models.CharField(default='',max_length=60)
    distance=RangeField(min_val=0.1,max_val=10.1,default=0.1)
    order_time=models.DateTimeField(default=timezone.now,editable=True)
    estimated_time=models.DateTimeField(default=timezone.now,editable=True)
    # return_time=models.DateTimeField(default=timezone.now,editable=True)
    team=models.CharField(choices=teams,default='get_team',max_length=60)
    status=models.CharField(choices=statuses,default="Pending",max_length=60)
    total_price=models.FloatField(default=0.0)
    
 
    def save(self,*args,**kwargs):
        
        if self.id is None: # if its a new add          
            self.team=get_team()
            self.order_id=get_ord_date()
            self.order_num=f"{datetime.today().strftime('%d_%m_%Y')}_{self.order_id}"    
        super().save(*args,**kwargs)

    def __str__(self):
        return f'{self.order_num}'
    class Meta:
        get_latest_by = 'order_time'
@receiver(post_delete, sender=OrderIntake)
def my_handler(sender,instance, **kwargs):
    global counter
    if check_today()==True:
        counter-=1



class ItemsIntake(models.Model):
    item=models.CharField(default='',max_length=60)
    quantity=models.IntegerField(default=1)
    price=models.FloatField(default=0.0)  # total price 
    order=models.ForeignKey(OrderIntake,related_name="order_items",on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.item} in cart..'

categories=(
    ("Television","Television"),
    ("Refrigerator","Refrigerator"),

)
class Inventory(models.Model):
    category=models.CharField(choices=categories,blank=True,max_length=60)
    model_num=models.CharField(default='',max_length=60)
    avail=models.IntegerField(default=0)
    price=models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.model_num} In..'