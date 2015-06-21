from django.contrib import admin
from realty_management.models import *

models = [MainTenant, Unit, Property, Vendor, LivesIn, Supports]

[admin.site.register(model) for model in models]

