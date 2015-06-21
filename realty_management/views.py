import os
from django.db import connection
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from realty_management.forms import *
from realty_management.models import *
from realty_management.path import *

models = [MainTenant, Unit, Property, Vendor, LivesIn, Supports]
forms = [MainTenantForm, UnitForm, PropertyForm, VendorForm, LivesInForm, SupportsForm]


def get_instance(model, key):
    model = next((m for m in models if m.__name__ == model), None)

    if model.__name__ == "MainTenant":
        return get_object_or_404(model, ssn=key)

    elif model.__name__ == "Unit":
        unit = key.split("/")
        number = unit[0]
        property = get_object_or_404(Property, address=unit[1])
        return get_object_or_404(model, number=number, property=property)

    elif model.__name__ == "Property":
        return get_object_or_404(model, address=key)

    elif model.__name__ == "Vendor":
        return get_object_or_404(model, company_name=key)

    elif model.__name__ == "LivesIn":
        info = key.split("/")
        tenant = get_instance("MainTenant", info[0])
        unit = get_instance("Unit", info[1] + '/' + info[2])
        return model.objects.filter(main_tenant=tenant, unit_number=unit).order_by('-lease_end')[0]

    elif model.__name__ == "Supports":
        info = key.split("/")
        vendor = get_instance("Vendor", info[0])
        property = get_instance("Property", info[1])
        service = info[2]
        return get_object_or_404(model, vendor=vendor, property=property, service=service)


def index(request):
    return render(request, 'realty_management/index.html')


def search(request):
    if request.method != 'POST':
        return

    template = 'realty_management/search/{}.html'
    model_name = request.POST['model']
    query_string = request.POST['query']
    model = next((m for m in models if m.__name__ == model_name), None)

    if model.__name__ == "MainTenant":
        query = Q()
        for word in query_string.split(' '):
            query |= Q(name__icontains=word) | Q(ssn__icontains=word) | Q(phone__icontains=word)

        tenants = model.objects.filter(query)
        tenants = [{
                    'name': t.name,
                    'ssn': t.ssn,
                    'phone': t.phone,
                    'contracts': t.get_contracts()
        } for t in tenants]

        context = {'results': tenants}
        return render(request, template.format(model_name.lower()), context)

    elif model.__name__ == "Property":
        query = Q()
        for word in query_string.split(' '):
            query |= Q(address__icontains=word)   \
                  |  Q(num_units__icontains=word) \
                  |  Q(owner__icontains=word)

        properties = model.objects.filter(query)
        context = {'objects': properties, 'model': 'Property', 'add_gone': True}
        return render(request, 'realty_management/show_all/property.html', context)

    elif model.__name__ == "Vendor":
        query = Q()
        for word in query_string.split(' '):
            query |= Q(phone__icontains=word)        \
                  |  Q(company_name__icontains=word) \
                  |  Q(address__icontains=word)      \
                  |  Q(contact_name__icontains=word)

        properties = model.objects.filter(query)
        context = {'objects': properties, 'model': 'Vendor', 'add_gone': True}
        return render(request, 'realty_management/show_all/vendor.html', context)


def show_one(request, model_name, key):
    template = model_name.lower() + '.html'
    instance = get_instance(model_name, key)

    if model_name == "Property":
        occupied_units = len(instance.get_occupied_units())
        owned_units = len(instance.get_owned_units())

        context = {
            'property': {
                'address': instance.address,
                'owner': instance.owner,
                'num_units': instance.num_units,
                'mortgage': instance.mortgage,
                'image': instance.image,
                'occupied_units': occupied_units,
                'owned_units': owned_units,
                'vacancy_rate': occupied_units / float(owned_units) if owned_units > 0 else 0
            },
            'units': [{
                'number': unit.number,
                'rent': unit.rent,
                'tenant': unit.get_active_contract().main_tenant,
                'lease_start': unit.get_active_contract().lease_start,
                'lease_end': unit.get_active_contract().lease_end,
                'tenants': [{
                    'lease_start': contract.lease_start,
                    'lease_end': contract.lease_end,
                    'tenant': contract.main_tenant
                } for contract in unit.get_past_contracts()],
                'sq_ft': unit.sq_ft,
                'baths': unit.num_baths,
                'beds': unit.num_bed
            } for unit in Unit.objects.filter(property=instance)],
            'vendors': [{
                'name': support.company_name,
                'service': support.service,
                'rate': support.monthly_rate,
                'phone': support.phone,
                'contact': support.contact_name,
                'address': support.address
            } for support in Supports.objects.raw('SELECT * FROM "realty_management_vendor" JOIN "realty_management_supports" ON "realty_management_vendor"."id" = "realty_management_supports"."vendor_id"')]
            #} for support in Supports.objects.filter(property=instance)]
        }

    return render(
                request,
                'realty_management/show_one/' + template,
                context
            )


def show_all(request, model_name):
    template = model_name.lower() + '.html'
    model = next((m for m in models if m.__name__ == model_name), None)

    if model.__name__ == "MainTenant":
        current_tenants, future_tenants, past_tenants = model.get_partitioned_tenants()

        current_tenants = sorted({t.ssn: t for t in current_tenants}.values(), lambda t, tt: cmp(t.ssn, tt.ssn))
        future_tenants = sorted({t.ssn: t for t in future_tenants}.values(), lambda t, tt: cmp(t.ssn, tt.ssn))
        past_tenants = sorted({t.ssn: t for t in past_tenants}.values(), lambda t, tt: cmp(t.ssn, tt.ssn))

        current_tenants = [{
                    'name': t.name,
                    'ssn': t.ssn,
                    'phone': t.phone,
                    'contracts': t.get_contracts()
        } for t in current_tenants]

        future_tenants = [{
                    'name': t.name,
                    'ssn': t.ssn,
                    'phone': t.phone,
                    'contracts': t.get_contracts()
        } for t in future_tenants]

        past_tenants = [{
                    'name': t.name,
                    'ssn': t.ssn,
                    'phone': t.phone,
                    'contracts': t.get_contracts()
        } for t in past_tenants]

        context = {
            'tenants': {
                'current_tenants': {
                    'title': 'Current Tenants',
                    'list': current_tenants
                },
                'future_tenants': {
                    'title': 'Future Tenants',
                    'list': future_tenants
                },
                'past_tenants': {
                    'title': 'Past Tenants',
                    'list': past_tenants
                }
            },
            'model': model_name
        }
    else:
        context = {
            'objects': [obj for obj in model.objects.all()],
            'model': model_name
        }

    return render(
                request,
                'realty_management/show_all/' + template,
                context
            )

def delete_info(request):
    model = request.POST["model"]
    key = request.POST["key"]
    instance = get_instance(model, key)
    instance.delete()
    return redirect('/add/' + request.POST['form_name'])


def modify_info(request, action, form_name, key):
    form = next((f for f in forms if f.__name__ == form_name), None)
    template = os.path.join('realty_management', 'add_info.html')

    if action == "add":
        return add_info(request, form, template, key)
    elif action == "edit":
        return edit_info(request, form, template, key)


def add_info(request, form, template, key):
    if request.method == 'POST':
        f = form(request.POST)
        if f.is_valid():
            f.save()
            context = {'success': True, 'form': form}
        else:
            context = {'success': False, 'error': 'Invalid form.', 'form': f}

    else:
        key = key.strip()
        if key:
            if form.__name__ == "UnitForm":
                context = {'form': form(initial={'property': get_instance('Property', key)})}

            elif form.__name__ == "LivesInForm":
                context = {'form': form(initial={'unit_number': get_instance('Unit', key)})}

            elif form.__name__ == "SupportsForm":
                context = {'form': form(initial={'property': get_instance('Property', key)})}

        else:
            context = {'form': form}

    return render(request, template, context)


def edit_info(request, form, template, key):
    instance = get_instance(form.__name__[:-4], key) 

    if request.method == 'POST':
        f = form(request.POST or None, instance=instance)
        if f.is_valid():
            f.save()
            context = {'success': True, 'form': form}
        else:
            context = {'success': False, 'error': 'Invalid form.', 'form': f}

    else:
        context = {'form': form(instance=instance)}

    context['edit'] = True
    context['model'] = type(instance).__name__
    context['form_name'] = form.__name__
    context['key'] = key

    return render(request, template, context)

def map(request):
    properties = Property.objects.all()
    start = "201 N Goodwin Ave Urbana IL 61801"
    end = start
    path = shortest_route(properties, start, end)
    urlstart = start.replace(" ", "+")
    urlend = end.replace(" ", "+")
    waypoints = '|'.join(path)
    url = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyBvzdk7SkZmva785N026l2k5W6Rzxd3Ucs&origin="+urlstart+"&destination="+urlend+"&waypoints="+waypoints+"&mode=driving"
    for i in range(len(path)):
        path[i] = path[i].replace("+", " ")
    context = {'url': url, 'path': path}
    return render(request, 'realty_management/map.html', context)