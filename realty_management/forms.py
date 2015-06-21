from django import forms
from django.forms import ModelForm, RadioSelect
from realty_management.models import *
from phonenumber_field.formfields import PhoneNumberField
from bootstrap3_datetime.widgets import DateTimePicker


class MainTenantForm(ModelForm):
    ssn = forms.IntegerField(label='SSN')
    name = forms.CharField(label='Name')
    phone = PhoneNumberField(label='Phone #')

    class Meta:
        model = MainTenant


class UnitForm(ModelForm):
    number = forms.CharField(label='Unit #', max_length=MAX_ADDR)
    property = forms.ModelChoiceField(queryset=Property.objects.all(), label='Property')
    rent = forms.IntegerField(label='Monthly Rent')
    sq_ft = forms.IntegerField(label='Square Feet')
    num_baths = forms.IntegerField(label='# Baths')
    num_bed = forms.IntegerField(label='# Beds')

    class Meta:
        model = Unit


class PropertyForm(ModelForm):
    address = forms.CharField(label='Address', max_length=MAX_ADDR)
    owner = forms.CharField(label='Owner', max_length=MAX_NAME)
    num_units = forms.IntegerField(label='# Units')
    mortgage = forms.FileField(label='Mortgage', required=False)
    image = forms.FileField(label='Image', required=False)

    class Meta:
        model = Property


class VendorForm(ModelForm):
    phone = PhoneNumberField(label='Phone #')
    company_name = forms.CharField(label='Company Name')
    address = forms.CharField(label='Address')
    contact_name = forms.CharField(label='Contact Name')

    class Meta:
        model = Vendor


class LivesInForm(ModelForm):
    main_tenant = forms.ModelChoiceField(queryset=MainTenant.objects.all(), label='Tenant')
    unit_number = forms.ModelChoiceField(queryset=Unit.objects.all(), label='Unit #')
    lease_start = forms.DateTimeField(
                        required=False,
                        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickSeconds": False}))
    lease_end = forms.DateTimeField(
                        required=False,
                        widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickSeconds": False}))
    lease_copy = forms.FileField(required=False)

    class Meta:
        model = LivesIn


class SupportsForm(ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label='Vendor')
    service = forms.CharField(label='Service')
    monthly_rate = forms.IntegerField(label='Monthly Rate')

    class Meta:
        model = Supports
