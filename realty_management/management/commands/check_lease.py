from django.core.management import BaseCommand, CommandError
from realty_management.models import Property, LivesIn, Unit
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from twilio.rest import TwilioRestClient 

import requests
import lxml
from lxml import html, etree
from lxml.cssselect import CSSSelector
import time, datetime
 
# put your own credentials here 
ACCOUNT_SID = "AC5152ba3e4bd9ec69b732ecb2f840de26" 
AUTH_TOKEN = "e72ea0df11834ac6fe678d8debb4bb26" 
 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
 
apartment_details = []
# scrape_url = 'http://chambana.craigslist.org/search/apa'
scrape_url = 'http://chambana.craigslist.org/'
num_cl = 50
class Command(BaseCommand):
    def handle(self, *args, **options):
        properties = Property.objects.all()
        foundcontract = False
        bodymsg = ''
        for p in properties:
            print('checking contracts for ' + p.address)
            todayplustwenty = date.today() + timedelta(days=25)
            todayplusforty = date.today() + timedelta(days=35)
            contracts = LivesIn.objects.filter(unit_number__in=p.get_owned_units())
            for c in contracts:
                print('time right now + 25 days: ' + str(todayplustwenty))
                print('lease end time: ' + str(c.lease_end.date()))
                print('time right now + 35 days: ' + str(todayplusforty))
                if todayplustwenty < c.lease_end.date() and c.lease_end.date() < todayplusforty:
                    #end email if date is 30 before end of lease
                    foundcontract = True
                    print(p.address, c.unit_number)
                    bodymsg += 'Your property at ' + str(p.address) + ' ' + str(c.unit_number) + ' has a lease expiring on ' + str(c.lease_end.date()) + ' for tenant named: ' + ''.join([i for i in str(c.main_tenant) if not i.isdigit()]) + '\n\n\n'
                    print('----------')

        #only sends one email per day with summary of which properties are expiring
        # if foundcontract:
        mine, craigs = check_cl()
        difference = abs(float(mine)-float(craigs))
        bodymsg += 'Apartment Analysis\n'
        bodymsg += '==================\n'
        bodymsg += '(based on ' + str(num_cl) + ' most recent Craigslist listings in CU area)\n'
        if mine > craigs:
            bodymsg += 'Recommend: decrease your prices!\n'
            bodymsg += 'your prices are ' + str(difference) + ' more expensive on average per sqft\n'
        else:
            bodymsg += 'Recommend: increase your prices!\n'
            bodymsg += 'your prices are $' + str(difference) + ' less expensive on average per sqft\n'
        message = send_mail('LEASE EXPIRING SOON', bodymsg, 'baggrealty@gmail.com', ['baggrealty@gmail.com'], fail_silently=False)
        client.messages.create(
            to="2245580568", 
            from_="+16302837104", 
            body=bodymsg,  
        )

        print('========================')
        
 
now = time.gmtime(time.time())
 
def convertTime(t):
    """Converts times in format HH:MMPM into seconds from epoch (but in CST)"""
    convertedTime = time.strptime(t + ' ' + str(now.tm_mon) + ' ' + str(now.tm_mday) + ' ' + str(now.tm_year), "%I:%M%p %m %d %Y")
    return time.mktime(convertedTime)
    # This used to add 5 * 60 * 60 to compensate for CST

def gettext(source):
    '''
    <span><b>1</b>BR / <b>1</b>Ba</span> 
    '''
    # print type(source)
    if 'sup' not in source:
        return -1
    source = etree.fromstring(source)
    # print etree.tostring(source)
    etree.strip_tags(source, 'b', 'span', 'sup')
    newstr = etree.tostring(source)
    sqft = newstr[6:-10]
    return sqft

def check_cl():
    print '\nScraping started at %s\n' % str(datetime.datetime.now())
    print 'scraping site: ' + scrape_url + 'search/apa'
    r = requests.get(scrape_url + 'search/apa')
    # build the DOM Tree
    tree = lxml.html.fromstring(r.text)
    # construct a CSS Selector
    sel = CSSSelector('p.row a')
    # Apply the selector to the DOM tree.
    results = sel(tree)
    # print results
    # get the text out of all the results
    data = [str(result.get('href')) for result in results]
    data = [str(scrape_url + result) for result in data if result != 'None']
    # print data
    print '='*20

    for index, link in enumerate(list(set(data))):

        # debugging
        if index > num_cl:
            break

        print 'scraping ' + link
        r = requests.get(link)
        tree = lxml.html.fromstring(r.text)
        sel = CSSSelector('p.attrgroup span')
        results = sel(tree)
        try:
            match = results[1]
            sqft = gettext(lxml.html.tostring(match))

    
            sel = CSSSelector('span.price')
            results = sel(tree)
            match = results[0]
            price = lxml.html.tostring(match)[21:-8]
            # print 'price', price
    
            if price.isdigit() and sqft > 0:
                #print {'sqft':sqft, 'cost':int(price)}
                apartment_details.append({'sqft':sqft, 'cost':int(price)})
            else:
                print 'not a digit...'
        except:
            print 'failed'
        print '='*20

    
    cost_sum = 0
    sqft_sum = 0
    
    units = Unit.objects.all()
    for unit in units:
        cost_sum += unit.rent
        sqft_sum += unit.sq_ft
    # get avg cost per sq in
    # cost_sum = Unit.objects.raw('SELECT SUM("realty_management_unit"."rent") AS id FROM "realty_management_unit"')
    # distinct_queryset = MyModel.objects.filter(reverse_relationship__icontains='foo').distinct()

    # cost_sum = Unit.objects.aggregate(Sum('rent'))
    # sqft_sum = Unit.objects.raw('SELECT SUM("realty_management_unit"."sq_ft") AS id FROM "realty_management_unit"')
    # sqft_sum = sqft_sum[0]
    # sqft_sum = Unit.objects.aggregate(sum('sq_ft'))
    if sqft_sum != 0:
        my_avg_cost_sqft = cost_sum / float(sqft_sum)
    # print cost_sum, sqft_sum
    print 'mine: $' + str(round(cost_sum/float(sqft_sum),2)) + '/sqft'


    # ================================ craigslist ================================

    cost = sum([int(apt['cost']) for apt in apartment_details])
    sqft = sum([int(apt['sqft']) for apt in apartment_details])
    

    if sqft != 0:
        craigslist_cost_sqft = cost/float(sqft)
        print 'craigslist: $' + str(round(craigslist_cost_sqft, 2)) + '/sqft'

    my_cost_sqft = str(round(cost_sum/float(sqft_sum),2))
    cl_cost_sqft = str(round(craigslist_cost_sqft, 2))

    return my_cost_sqft, cl_cost_sqft