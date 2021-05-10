from .models import Inventory,OrderIntake,ItemsIntake
from rest_framework import serializers
class OrderHistSerializer(serializers.ModelSerializer):
    class Meta:
        model= OrderIntake
        fields=['order_num','total_price','estimated_time']# status,team

class OrderSerializerForm(serializers.Serializer):
    cust_name=serializers.CharField(default="")
    cust_add=serializers.CharField(default="")
    distance=serializers.FloatField(default=0.0)

class ItemSerializerForm(serializers.Serializer):
    quatity=serializers.CharField(default="")
    item=serializers.CharField(default="")
    price=serializers.FloatField(default=0.0)

