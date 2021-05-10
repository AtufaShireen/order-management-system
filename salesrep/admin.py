from django.contrib import admin

# Register your models here.
from .models import Inventory,OrderIntake,ItemsIntake
admin.site.register([
    Inventory,OrderIntake,ItemsIntake
])