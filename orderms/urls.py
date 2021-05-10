from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', auth_views.LoginView.as_view(template_name='salesrep/login.html',redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='salesrep/logout.html'), name='logout'),
    path('',include('salesrep.urls')),
]
