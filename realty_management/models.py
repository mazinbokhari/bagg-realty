from django.db import models, connection
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.mail import send_mail

MAX_SSN   = [MaxValueValidator(999999999), MinValueValidator(100000000)]
MAX_PHONE = [MaxValueValidator(9999999999), MinValueValidator(1000000000)]
MAX_NAME  = 500
MAX_ADDR  = 800


class MainTenant(models.Model):
    ssn = models.PositiveIntegerField(primary_key=True, validators=MAX_SSN)
    name = models.CharField(max_length=MAX_NAME)
    phone = PhoneNumberField()

    @classmethod
    def get_partitioned_tenants(cls):
        now = timezone.now()
        contracts = LivesIn.objects.raw('SELECT "realty_management_livesin"."id", "realty_management_livesin"."main_tenant_id", "realty_management_livesin"."unit_number_id", "realty_management_livesin"."lease_start", "realty_management_livesin"."lease_end", "realty_management_livesin"."lease_copy" FROM "realty_management_livesin"')
        return (
                    map(
                        lambda c: c.main_tenant,
                        filter(lambda c: c.lease_end >= now >= c.lease_start, contracts)
                    ),
                    map(
                        lambda c: c.main_tenant,
                        filter(lambda c: c.lease_start > now, contracts)
                    ),
                    map(
                        lambda c: c.main_tenant,
                        filter(lambda c: now > c.lease_end, contracts)
                    ),
                )

    def get_contracts(self):
        return LivesIn.objects.raw('SELECT "realty_management_livesin"."id", "realty_management_livesin"."main_tenant_id", "realty_management_livesin"."unit_number_id", "realty_management_livesin"."lease_start", "realty_management_livesin"."lease_end", "realty_management_livesin"."lease_copy" FROM "realty_management_livesin" WHERE "realty_management_livesin"."main_tenant_id" = {}'.format(self.pk))

    def __str__(self):
        return "{} - {}".format(self.name, self.ssn)


class Unit(models.Model):
    number = models.CharField(max_length=MAX_ADDR)
    property = models.ForeignKey('Property')
    rent = models.IntegerField()
    sq_ft = models.IntegerField()
    num_baths = models.IntegerField()
    num_bed = models.IntegerField()

    def get_active_contract(self):
        now = timezone.now()
        contract = LivesIn.objects.raw('SELECT "realty_management_livesin"."id", "realty_management_livesin"."main_tenant_id", "realty_management_livesin"."unit_number_id", "realty_management_livesin"."lease_start", "realty_management_livesin"."lease_end", "realty_management_livesin"."lease_copy" FROM "realty_management_livesin" WHERE "realty_management_livesin"."unit_number_id" = {} ORDER BY "realty_management_livesin"."lease_end" DESC'.format(self.pk))[:]

        class Vacant:
            class VacantTenant:
                name = "VACANT"

            main_tenant = VacantTenant
            lease_start = ""
            lease_end   = ""

        if len(contract) <= 0:
            return Vacant
        contract = contract[0]
        if contract.lease_end < now:
            return Vacant
        return contract

    def get_past_contracts(self):
        now = timezone.now()
        past = LivesIn.objects.filter(unit_number=self).order_by('-lease_end')
        return [contract for contract in past]

    def __str__(self):
        return "Unit #{} on {}".format(self.number, self.property)

    class Meta:
        unique_together = ('number', 'property')


class Property(models.Model):
    address = models.CharField(max_length=MAX_ADDR)
    city = models.CharField(max_length=MAX_ADDR)
    state = models.CharField(max_length=MAX_ADDR)
    zip_code = models.CharField(max_length=MAX_ADDR)
    owner = models.CharField(max_length=MAX_NAME)
    num_units = models.IntegerField()
    mortgage = models.FileField(null=True, blank=True, upload_to='.')
    image = models.FileField(null=True, blank=True, upload_to='.')

    def get_occupied_units(self):
        now = timezone.now()
        #contracts = LivesIn.objects.raw('SELECT * FROM "realty_management_livesin" WHERE "realty_management_livesin"."unit_number_id" IN (' + ','.join([str(u.pk) for u in self.get_owned_units()]) + ')')
        contracts = LivesIn.objects.filter(unit_number__in=self.get_owned_units())
#         for q in connection.queries:
#             print(q['sql'])
#             print('\n')

        ongoing_contracts = [c for c in contracts if c.lease_end >= now >= c.lease_start]
        return [c.unit_number for c in ongoing_contracts]
    '''
    def check_expire(self):
        todayplusthirty = datetime.now() + timedelta(days=30)
        contracts = LivesIn.objects.filter(unit_number__in=self.get_owned_units())
        for c in contracts:
            if todayplusthirty > c.lease_end:
                #end email if date is 30 before end of lease
                message = send_mail('LEASE EXPIRING SOON', '', 'baggrealty@gmail.com', ['baggrealty@gmail.com'], fail_silently=False)
    '''
    
    def get_owned_units(self):
        return Unit.objects.filter(property=self)

    def __str__(self):
        return self.address

    class Meta:
        unique_together = ('address', 'city', 'state', 'zip_code',)


class Vendor(models.Model):
    phone = PhoneNumberField(unique=True)
    company_name = models.CharField(max_length=MAX_NAME)
    address = models.CharField(max_length=MAX_ADDR)
    contact_name = models.CharField(max_length=MAX_NAME)

    def __str__(self):
        return '{}'.format(
                        self.company_name,
                )


class LivesIn(models.Model):
    main_tenant = models.ForeignKey(MainTenant)
    unit_number = models.ForeignKey(Unit)
    lease_start = models.DateTimeField()
    lease_end = models.DateTimeField()
    lease_copy = models.FileField(upload_to='.')


    class Meta:
        unique_together = ('main_tenant', 'unit_number', 'lease_end')


class Supports(models.Model):
    vendor = models.ForeignKey(Vendor)
    property = models.ForeignKey(Property)
    service = models.CharField(max_length=MAX_NAME)
    monthly_rate = models.IntegerField()

    def __str__(self):
        return '<Supports vendor={} property={} service={} monthly_rate={}>'.format(
                        self.vendor,
                        self.property,
                        self.service,
                        self.monthly_rate
                )

    class Meta:
        unique_together = ('vendor', 'property', 'service')
