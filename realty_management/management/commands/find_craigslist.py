from django.core.management import BaseCommand, CommandError
from realty_management.models import Unit


import requests
import lxml
from lxml import html, etree
from lxml.cssselect import CSSSelector
import time, datetime

apartment_details = []
# scrape_url = 'http://chambana.craigslist.org/search/apa'
scrape_url = 'http://chambana.craigslist.org/'
class Command(BaseCommand):
    help = 'Scrapes the sites for new dockets'
    def handle(self, *args, **options):
        self.stdout.write('\nScraping started at %s\n' % str(datetime.datetime.now()))
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
            if index > 20:
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

        # average price of all the apartments
        # prices = [float(apt['cost']) for apt in apartment_details]
        # avg_price = sum(prices)/(len(prices)+0.01)
        # print avg_price

        # avgs = Unit.objects.raw('SELECT "realty_management_unit"."num_bed", "realty_management_unit"."num_baths", AVG("realty_management_unit"."rent") AS avg FROM "realty_management_unit"')
        # print avgs[0]
        
 
now = time.gmtime(time.time())
 
def convertTime(t):
   """Converts times in format HH:MMPM into seconds from epoch (but in CST)"""
   convertedTime = time.strptime(t + ' ' + str(now.tm_mon) + ' ' + str(now.tm_mday) + ' ' + str(now.tm_year), "%I:%M%p %m %d %Y")
   return time.mktime(convertedTime)
   # This used to add 5 * 60 * 60 to compensate for CST

def populate_details(data):
    # go through links to get info
    for index, link in enumerate(list(set(data))):

        # debugging
        if index > 3:
            break

        print 'scraping ' + link
        r = requests.get(link)
        tree = lxml.html.fromstring(r.text)
        #print lxml.html.tostring(tree)
        sel = CSSSelector('p.attrgroup span')
        results = sel(tree)

        match = results[1]
        # print lxml.html.tostring(match)
        sqft = gettext(lxml.html.tostring(match))
        # print ft, ba
        #break

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



# for br ba
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
