from django.contrib import admin
from .models import Product, Category, Attribute, Option, Value

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(Option)
admin.site.register(Value)
