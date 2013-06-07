from requests.auth import AuthBase
from sanetime import time
from werkzeug.urls import Href
import requests, csv
import re
import numpy as np
import xlwt
from collections import defaultdict
from datetime import datetime as D

def sfdc_date_or_none(entry):
    my_date = None
    try:
        my_date = D(int(entry[0:4]), int(entry[5:7]), int(entry[8:10]))
    except:
        my_date = None
    return my_date


class SalesforceAuth(AuthBase):
    """
    Usage:
        sf = Salesforce(username=username, password=password, security_token=security_token)
    Get all active campaigns, by account:
        ac = active_campaigns(sf)
    """
    # These are from the Draper remote access app
    # CLIENT_ID = '3MVG9VmVOCGHKYBTJhT3AbJPhaPXnB8fyM.si9oRE4.j9wrsTG0oeRugr2E6kmkmzk9QNZzm8UJOKW2D.s3NF'
    # CLIENT_SECRET = '2476564724669919262'
    
    # These are from the Finance Reporting app
    CLIENT_ID = '3MVG9VmVOCGHKYBTJhT3AbJPhaFEHVTrg4R3YShGvoU.blmkKLAELKE1hWZcUwpcGpR5Td.Pjotgije3g8gYc'
    CLIENT_SECRET = '2869450356585909208'

    def __init__(self, username, password, security_token,
                 url='https://login.salesforce.com/services/oauth2/token',
                 client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.url = url
        # TODO(sday): Add some facility to switch to test.salesforce.com when
        # provided with sandbox username.
        self.username = username
        self.password = password
        self.security_token = security_token
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = None
        self.instance_url = None
        self.issued_at = None

        self.authorize()

    def authorize(self):
        r = requests.post(self.url, data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': self.password + self.security_token})

        r.raise_for_status()

        authdata = r.json()

        self.access_token = authdata['access_token']
        self.issued_at = time(int(authdata['issued_at']))
        self.instance_url = Href(authdata['instance_url'])

        # There are two other fields in this response that we are ignoring for
        #  now (thx akovacs):
        # 1. `id` - This is a url that leads to a description about the user
        #    associated with this authorization session, including email, name
        #    and username.
        # 2. `signature` - This is a base64-encoded HMAC-SHA256 that can be
        #    used to verify that the response was not tampered with. As we
        #    become larger, it probably makes sense to verify this, but for
        #    now, we'll leave it alone.
        self.id_url = authdata['id']
        self.signature = authdata['signature']

    def __call__(self, request):

        if self.access_token is None:
            self.authorize()

        request.headers['Authorization'] = 'Bearer {token}'.format(token=self.access_token)
        return request



class Salesforce(object):
    """
    A simple interface to salesforce, returning basic dict objects and
    providing transparent iteration over resources.
    """
    VERSION = "v26.0"

    def __init__(self, username, password, security_token, version=VERSION, session=requests.Session()):
        self.version = version
        self.session = session
        self.session.auth = SalesforceAuth(username, password, security_token)

    def base(self, *args, **kwargs):
        """
        Build url from base instance_url
        """
        return self.session.auth.instance_url(*args, **kwargs)

    def href(self, *args, **kwargs):
        """
        Build a url against the api endpoint.
        """
        return self.base('services', 'data', self.version, *args, **kwargs)

    def _iter_response(self, url, key):
        """
        Iterate over the response records, fetching the next urls if specified.
        """
        while True:
            r = self.session.get(url)
            # TODO(sday): Errors messages are available in json
            r.raise_for_status()
            content = r.json()
            for obj in content[key]:
                yield obj
            if 'nextRecordsUrl' not in content:
                break
            url = self.base(content['nextRecordsUrl'])

    def sobjects(self):
        """
        Retrieve information about the sobjects.
        """
        return self._iter_response(self.href('sobjects'), 'sobjects')

    def describe(self, sobject):
        r = self.session.get(self.href('sobjects', sobject, 'describe'))
        r.raise_for_status()
        return r.json()

    def query(self, q):
        return self._iter_response(self.href('query', q=q), 'records')



def bottoms_up(sf):
    book = xlwt.Workbook(encoding="utf-8")
    seller_dict = {}

    for row in sf.query("""SELECT Sc.Revenue, Sc.ScheduleDate, Sc.CurrencyIsoCode, Sc.Quantity, Sc.Type, Ow.Name, Op.Rate_Type__c, Op.Name, Op.Campaign_EVENT__c, Op.StageName, 
                            Op.BillingSchedule__c, Op.Agency__c
                            FROM OpportunityLineItemSchedule Sc, Sc.OpportunityLineItem.Opportunity Op, Op.Owner Ow
                            WHERE (not Op.StageName LIKE '% - Lost') AND Sc.ScheduleDate = THIS_YEAR 
                            ORDER BY Ow.Name"""):
        myarray = [None] * 7
        op = row['OpportunityLineItem']['Opportunity']
        try:
            opportunity = re.sub(',', '.', op['Name']).split('_')
            account = opportunity[1]
            stage = op['StageName']            
            name = re.sub(',',';', op['Owner']['Name'])
            name = re.sub('US-', '', name)

            rev = row['Revenue']
            date = row['ScheduleDate']

            
            seller = seller_dict.get(name)
            
            if not seller:
                seller_dict[name] = {account: [[date, stage, rev]]}
            else:
                op = seller_dict[name].get(account)
                if not op:
                    seller_dict[name][account] = [[date, stage, rev]]
                else:
                    seller_dict[name][account].append([date, stage, rev])
                
        except:
            pass
        
        
        
    for name, op_dict in sorted(seller_dict.iteritems()):   
        sheet = book.add_sheet(name)
        row = 0
        for op, rev_list in sorted(op_dict.iteritems()):
            col = 1
            sheet.write(row,0,op)
            for triple in rev_list:
                sheet.write(row,col,str(triple[0]))
                sheet.write(row+1,col,triple[1])
                sheet.write(row+2,col,triple[2])
                col = col + 1
                if col > 254:
                    row = row + 3
                    col = 1
            row = row + 3
        
    
    book.save("C:/Users/rthomas/Desktop/DatabaseProject/bottomsup.xls")    
    
    
    
    

def bottoms_up_first_pass(sf):
    book = xlwt.Workbook(encoding="utf-8")
    counter_dict = {}

    for row in sf.query("""SELECT Sc.Revenue, Sc.ScheduleDate, Sc.CurrencyIsoCode, Sc.Quantity, Sc.Type, Ow.Name, Op.Rate_Type__c, Op.Name, Op.Campaign_EVENT__c, Op.StageName, 
                            Op.BillingSchedule__c, Op.Agency__c
                            FROM OpportunityLineItemSchedule Sc, Sc.OpportunityLineItem.Opportunity Op, Op.Owner Ow
                            WHERE (not Op.StageName LIKE '% - Lost') AND Sc.ScheduleDate = THIS_YEAR 
                            ORDER BY Ow.Name"""):
        myarray = [None] * 7
        op = row['OpportunityLineItem']['Opportunity']
        try:
            myarray[0] = re.sub(',', '.', op['Name'])
            myarray[1] = op['Rate_Type__c']
            myarray[2] = op['Campaign_EVENT__c']
            myarray[3] = op['StageName']            
        except:
            pass
        try:
            name = re.sub(',',';', op['Owner']['Name'])
            name = re.sub('US-', '', name)
            myarray[4] = name
        except:
            pass
        myarray[5] = row['Revenue']
        myarray[6] = row['ScheduleDate']
        #mydate = sfdc_date_or_none(myarray[6])
        #myquarter = (mydate.month-1)//3
        
        counter = counter_dict.get(name, 0)
        if not counter:
            counter_dict[name] = 0
            sheet = book.add_sheet(name)
        #else:
        #    sheet = book.sheet_by_name(name)
                

        for n in range(7):
            print name, counter, n, myarray
            sheet.write(counter,n,myarray[n])

        counter_dict[name] = counter_dict[name] + 1
    
    book.save("C:/Users/rthomas/Desktop/DatabaseProject/bottomsup.xls")      
                


def write_prices2(sf):
    with open('C:/Users/rthomas/Desktop/DatabaseProject/historicalratesindustry.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Name', 'CPMRate', 'Net CPM', 'StartDate', 'EndDate', 'Budget', 'CreativeType', 'SalesStage', 'RequestType', 'Opportunity Approval Status', 
                             'Opportunity Name', 'Standard Flash CPM', 'Rich Media CPM', 'Viewability CPM', 'Brand Safety CPM', 'Geo- Country', 
                             'Flight Approval Status', 'ValueAdd Requested', 'ValueAdd Impressions', 'CurrencyIsoCode', 'Geo- States', 'Industry Acct', 'Industry Vertical', 'Rate Type'])
        temp = ''
        for row in sf.query("""SELECT Op.Name, ApprovedCPMRate__c,ApprovedFlightBudget__c,ApprovedFlightEndDate__c,ApprovedFlightModelName__c,ApprovedFlightStartDate__c,CPMRate__c,FlightModelName__c, FlightStartDate__c, 
                                FlightEndDate__c, Id, FlightBudget__c, Name, Opportunity__c, CreativeType__c, ApprovedCreativeType__c, Op.StageName, Op.RequestType__c, Op.ApprovalStatus__c,
                                TargetCountry__c, States__c, SFCPM__c, RichMediaCPM__c, ViewabilityCPM__c, BrandSafetyCPM__c, ApprovedSFCPM__c, ApprovedRichMediaCPM__c, ApprovedViewabilityCPM__c, ApprovedBrandSafetyCPM__c, ApprovalStatus__c,
                                VAImps__c, ValueAddRequested__c, ApprovedValueAddImps__c, ApprovedValueAddRequest__c, CurrencyIsoCode, Op.Industry_Acct__c, Op.Industry_Vertical__c, Op.Rate_Type__c
                                FROM ProposalFlight__c Pr, Pr.Opportunity__r Op
                                ORDER BY FlightStartDate__c ASC"""):
            keep = True
            myarray = [None] * 24
            if re.search('change request', row['FlightModelName__c'], flags=re.IGNORECASE):
                name = re.sub(',', '.', row['ApprovedFlightModelName__c'])
            else:
                name = re.sub(',', '.', row['FlightModelName__c'])
            if (not re.search('US', name)) or re.search('[Ff]acebook', name) or re.search('Skeleton Migration Flight', name) or re.search('Will Auto Update', name):
                keep = False
            myarray[0] = name
            if keep:
                op = row['Opportunity__r']
                myarray[1] = row['CPMRate__c'] or row['ApprovedCPMRate__c'] or 0

                myarray[3] = row['FlightStartDate__c'] or row['ApprovedFlightStartDate__c']
                myarray[4] = row['FlightEndDate__c'] or row['ApprovedFlightEndDate__c']
                myarray[5] = row['FlightBudget__c'] or row['ApprovedFlightBudget__c']
                myarray[6] = row['CreativeType__c'] or row['ApprovedCreativeType__c']
                try:
                    myarray[7] = op['StageName']
                except:
                    pass
                try:
                    myarray[8] = op['RequestType__c']
                except:
                    pass    
                try:    
                    myarray[9] = op['ApprovalStatus__c'] 
                except:
                    pass
                try:
                    myarray[21] = op['Industry_Acct__c']
                    myarray[22] = op['Industry_Vertical__c']
                except:
                    pass
                try:
                    myarray[23] = op['Rate_Type__c']
                except:
                    pass
                try:   
                    myarray[10] = re.sub(',', '.', op['Name'])
                except:
                    pass
                myarray[11] = row['SFCPM__c'] or row['ApprovedSFCPM__c'] or 0
                myarray[12] = row['RichMediaCPM__c'] or row['ApprovedRichMediaCPM__c'] or 0
                myarray[13] = row['ViewabilityCPM__c'] or row['ApprovedViewabilityCPM__c'] or 0
                myarray[14] = row['BrandSafetyCPM__c'] or row['ApprovedBrandSafetyCPM__c'] or 0
                myarray[15] = row['TargetCountry__c']
                myarray[16] = row['ApprovalStatus__c']
                myarray[17] = row['ValueAddRequested__c'] or row['ApprovedValueAddRequest__c']
                myarray[18] = row['VAImps__c'] or row['ApprovedValueAddImps__c']
                myarray[19] = row['CurrencyIsoCode']
                if(row['States__c']):
                    myarray[20] = re.sub(',', ';', row['States__c'])
                myarray[2] = myarray[1] - (myarray[12] + myarray[13] + myarray[14])
                
                
                if myarray[1] and myarray[1] < 50:
                    spamwriter.writerow(myarray)
                

                    
           


# take out facebook and UK
def write_prices(sf):
    with open('C:/Users/rthomas/Desktop/DatabaseProject/prices.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        for row in sf.query("""SELECT ApprovedCPMRate__c,ApprovedFlightBudget__c,ApprovedFlightEndDate__c,ApprovedFlightModelName__c,ApprovedFlightStartDate__c,CPMRate__c,FlightModelName__c, FlightStartDate__c, 
                                FlightEndDate__c, Id, FlightBudget__c, Name, Opportunity__c, CreativeType__c, ApprovedCreativeType__c
                                FROM ProposalFlight__c 
                                ORDER BY FlightStartDate__c ASC"""):
            keep = True
            myarray = [None] * 12
            if re.search('change request', row['FlightModelName__c'], flags=re.IGNORECASE):
                name = re.sub(',', '.', row['ApprovedFlightModelName__c'])
            else:
                name = re.sub(',', '.', row['FlightModelName__c'])
            if re.search('UK', name) or re.search('[Ff]acebook', name) or re.search('Skeleton Migration Flight', name) or re.search('Will Auto Update', name):
                keep = False
            temparray = name.split(" - ")
            if len(temparray) == 6:
                myarray[0:6] = temparray
            if len(temparray) == 7:
                myarray[0] = temparray[0]
                myarray[1] = temparray[1] + temparray[2]
                myarray[2:6] = temparray[3:7]
            if len(temparray) == 8:
                myarray[0] = temparray[0]
                myarray[1] = temparray[1] + temparray[2]
                myarray[2:4] = temparray[3:5]
                myarray[4] = temparray[5] + temparray[6]
                myarray[5] = temparray[7]
            if len(temparray) > 8:
                print temparray
            try:
                if keep:  
                    myarray[7] = row['CPMRate__c'] or row['ApprovedCPMRate__c']
                    myarray[8] = row['FlightStartDate__c'] or row['ApprovedFlightStartDate__c']
                    myarray[9] = row['FlightEndDate__c'] or row['ApprovedFlightEndDate__c']
                    myarray[10] = row['FlightBudget__c'] or row['ApprovedFlightBudget__c']
                    myarray[11] = row['CreativeType__c'] or row['ApprovedCreativeType__c']
                    if myarray[7] and keep:
                        spamwriter.writerow(myarray)
                
            except:
                print(myarray)
           

            
            

sf = Salesforce(username='rthomas@quantcast.com', password='qcsales', security_token='46GSRjDDmh9qNxlDiaefAhPun')
ac = bottoms_up(sf)


