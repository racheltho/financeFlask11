import sys
import requests

from collections import Iterator

from requests.auth import AuthBase
from sanetime import time
from werkzeug.urls import Href

from qobjects import PCode

from datetime import datetime



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


def active_campaigns(sf):
    """
    Prototype of the monolithic active_campaigns query.
    """
    advertisers = {}

    for row in sf.query("""SELECT
                               c.id,
                               c.name,
                               c.rtbid__c,
                               c.creative_type__c,
                               c.lastmodifieddate,
                               a.publisher_id__c,
                               a.name,
                               a.lastmodifieddate,
                               io.id,
                               io.name,
                               io.rtbid__c,
                               io.lastmodifieddate,
                               f.name,
                               f.name__c,
                               f.lastmodifieddate,
                               t.Name,
                               l.id,
                               l.name,
                               l.rtbid__c,
                               l.start_date__c,
                               l.end_date__c,
                               l.lastmodifieddate
                        FROM CREATIVE_MAP__C cm,
                             cm.Creative__r c,
                             cm.RTB_Line_Item__r l,
                             c.Account__r a,
                             l.Line_Item__r f,
                             f.Target__r t,
                             f.Insertion_Order__r io
                        WHERE
                            cm.RTB_Line_Item__r.end_date__c > YESTERDAY and
                            cm.RTB_Line_Item__r.Line_Item__r.Insertion_Order__r.end_date__c > YESTERDAY and
                            cm.Creative__r.isdeleted = false and
                            cm.Creative__r.enabled__c = true and
                            cm.RTB_Line_Item__r.isdeleted = false and
                            cm.RTB_Line_Item__r.Line_Item__r.isdeleted = false and
                            cm.RTB_Line_Item__r.Line_Item__r.Insertion_Order__r.isdeleted = falseand
                            cm.RTB_Line_Item__r.Line_Item__r.Target__c <> null"""):

        sf_account = row['Creative__r'][u'Account__r']
        sf_creative = row['Creative__r']
        sf_lineitem = row['RTB_Line_Item__r']
        sf_flight = sf_lineitem['Line_Item__r']
        sf_insertion_order = sf_flight['Insertion_Order__r']
        sf_target = sf_flight['target__r']

        pcode = PCode('p-' + sf_account['publisher_id__c'])

        advertiser = advertisers.setdefault(pcode, {
            'id': pcode,
            'name': sf_account['Name'],
            'updated_at': sf_account['LastModifiedDate'],
            'insertion_orders': {},
            'creatives': {},
        })

        creative_id = int(sf_creative['RTBID__c'])
        creative = advertiser['creatives'].setdefault(creative_id, {
            'id': creative_id,
            'name': sf_creative['Name'],
            'type': sf_creative['Creative_Type__c'].lower(),
            'updated_at': time(sf_creative['LastModifiedDate']).utc_datetime,
        })

        insertion_order_id = int(sf_insertion_order['rtbid__c'])
        insertion_order = advertiser['insertion_orders'].setdefault(insertion_order_id,
            {
                'id': insertion_order_id,
                'name': sf_insertion_order['Name'],
                'updated_at': sf_insertion_order['LastModifiedDate'],
                'flights': {},
            })

        flight_id = sf_flight['Name']
        flight = insertion_order['flights'].setdefault(flight_id, {
            'id': flight_id,
            'name': sf_flight['Name__c'],
            'updated_at': sf_flight['LastModifiedDate'],
            'target': {'name': sf_target['Name']},
            'lineitems': {},
            })

        lineitem_id = int(sf_lineitem['rtbid__c'])
        lineitem = flight['lineitems'].setdefault(lineitem_id, {
            'id': lineitem_id,
            'name': sf_lineitem['Name'],
            'start': time(sf_lineitem['start_date__c']).utc_datetime,
            'end': time(sf_lineitem['end_date__c']).utc_datetime,
            'updated_at': sf_lineitem['LastModifiedDate'],
            'creative_ids': set(),
        })

        lineitem['creative_ids'].add(creative_id)

    # Move to using lists, now that we know the objs are unique
    advertisers = advertisers.values()
    for a in advertisers:
        a['insertion_orders'] = a['insertion_orders'].values()
        a['creatives'] = a['creatives'].values()

        for io in a['insertion_orders']:
            io['flights'] = io['flights'].values()

            for f in io['flights']:
                f['lineitems'] = f['lineitems'].values()

    return advertisers



def new_opportunities(sf):
    """
    new opportunities query.
    """
    advertisers = {}

#    class Sfdc(db.Model):
#        id = db.Column(db.Integer, primary_key=True)
#        oid = db.Column(db.Integer)
#        ioname = db.Column(db.Unicode)
##    country = db.Column(db.Unicode)
##    signedIO = db.Column(db.Unicode)
##    setUp = db.Column(db.Unicode)
#        agency = db.Column(db.Unicode)
#        cp = db.Column(db.Unicode)
#        channel = db.Column(db.Unicode)
#        advertiser = db.Column(db.Unicode)
#        owner_name = db.Column(db.Unicode)
#        start_date = db.Column(db.Date)
#        end_date = db.Column(db.Date)
#        budget = db.Column(db.Float)
#        currency = db.Column(db.Unicode)
#        approved = db.Column(db.Boolean)


    for row in sf.query("""SELECT IO.Name, IO.CreatedDate, IO.LastModifiedDate, IO.Start_Date__c, IO.End_Date__c, IO.Budget__c, IO.SalesChannel__c, IO.Advertiser_Account__c, 
                                op.Name, op.CreatedDate, a.Name, op.CampaignStart__c, op.CampaignEnd__c, op.Rate_Type__c, op.Opportunity_ID__c, op.SalesPlanner__c, 
                                op.LastModifiedDate, op.Owner.Name, 
                                aa.Name, aa.CurrencyIsoCode
                            FROM Insertion_Order__c IO, IO.Opportunity__r op, op.Agency__r a, IO.Advertiser_Account__r aa
                            WHERE op.Agency__c <> null LIMIT 50"""):

        #sf_io = row['Insertion_Order__c']


        sf_ioname = row['Name']
        sf_channel = row['SalesChannel__c']
        sf_budget = row['Budget__c']
               
        sf_oid = int(row['Opportunity__r']['Opportunity_ID__c'])
        sf_cp = row['Opportunity__r']['Rate_Type__c']
        
        start_date = row['Opportunity__r']['CampaignStart__c']
        end_date = row['Opportunity__r']['CampaignEnd__c']
        last_modified = row['Opportunity__r']['LastModifiedDate'][0:9]
        sf_start_date = datetime.strptime(start_date,'%Y-%m-%d').date()
        sf_end_date = datetime.strptime(end_date,'%Y-%m-%d').date()
        sf_last_modified = datetime.strptime(last_modified,'%Y-%m-%d').date()
        
        agency_r = row['Opportunity__r']['Agency__r']
        sf_agencyname = None
        if(agency_r):
            sf_agencyname = agency_r['Name']
        owner = row['Opportunity__r']['Owner']
        sf_owner_name = None
        if(owner):
            sf_owner_name = owner['Name']

        sf_advertiser = row['Advertiser_Account__r']['Name']
        sf_currency = row['Advertiser_Account__r']['CurrencyIsoCode']
                
        

        a = Sfdc(oid = sf_oid, channel = sf_channel, agency = sf_agencyname, cp = sf_cp, advertiser = sf_advertiser, owner_name = sf_owner_name, start_date = sf_start_date, 
                 end_date = sf_end_date, budget = sf_budget, ioname = sf_ioname, currency = sf_currency, approved = False)
        s.add(a)
        s.commit()



sf = Salesforce(username='rthomas@quantcast.com', password='qcsales', security_token='46GSRjDDmh9qNxlDiaefAhPun')
ac = new_opportunities(sf)

