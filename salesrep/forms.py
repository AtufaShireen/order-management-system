from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm
from .models import OrderIntake,ItemsIntake
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
class RequiredFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def clean(self):
        if not form.has_changed():
            raise ValidationError([{
                'Error':ValidationError(_('Add at least one Item'),code='required')
                }])
        super().clean()
            
ItemFormset = inlineformset_factory(OrderIntake,ItemsIntake,fields=['item','quantity','price'],extra=0,can_delete=True) # 

class OrderIntakeForm(ModelForm):
    class Meta:
        model=OrderIntake
        fields=['cust_name','cust_add','distance','status'] #

    def clean(self):
        super().clean()
        tn=self.cleaned_data.get('cust_add',[]).split(',')
        if len(tn)==0:
            raise ValidationError(_('Please add complete address'),code='required')