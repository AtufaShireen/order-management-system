from django.urls import path,include
from .views import (place_order,create_order,check_inventory,
                    order_history,CheckInventoryAPI,OrderHistoryAPI,delete_order,
                    OrderAPi,AddOrderApi,OrderStatusApi)
app_name="salesrep"
urlpatterns = [    
    path('',create_order,name='create_order'),
    path('add_inventory/<str:order_num>/',check_inventory,name='check_inventory'),
    path('place_order/<str:order_num>/',place_order,name='place_order'),
    path('delete_order/<str:order_num>/',delete_order,name='delete_order'),
    path('order_history/',order_history,name='order_history'),
    path('api/',include('rest_framework.urls')),
    path('api/check_inventory/',CheckInventoryAPI.as_view(),name='api_check_inventory'),
    path('api/check_status/',OrderStatusApi.as_view(),name='api_check_status'), 
    path('api/order_history/',OrderHistoryAPI.as_view(),name='api_order_history'), 
    path('api/add_order/',AddOrderApi.as_view(),name='api_add_order'),
    path('api/place_order/<str:order_num>/',OrderAPi.as_view(),name='api_order'),
    

    
]
