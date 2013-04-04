# Rachel Thomas
import flask
import json
import sqlalchemy as a
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, column_property, backref
from sqlalchemy.ext.declarative import declarative_base

import psycopg2
import flask_sqlalchemy
import xlrd
import csv

import re 
from datetime import date, timedelta
from datetime import datetime as D
from xldate import xldate_as_tuple

from flask import jsonify
from itertools import groupby, islice, chain
from operator import itemgetter
from collections import defaultdict

from requests.auth import AuthBase
from sanetime import time
from werkzeug.urls import Href
import requests



# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/mydatabase11'
db = flask_sqlalchemy.SQLAlchemy(app)

def get_or_create(session, model, **kwargs):
    for name, value in kwargs.items():
        if value is None or value == "":
            return None
        else:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = model(**kwargs)
                session.add(instance)
                return instance

def get_date_or_none(entry):
    my_date = None
    if isinstance(entry, float):
        try:
            date_tuple = xldate_as_tuple(entry,0)[0:3]
            my_date = date(*date_tuple)
        except:
            my_date = None
    return my_date


def int_or_none(entry):
    if entry == '':
        return None
    else:
        if isinstance(entry, float) or isinstance(entry, str):
            return int(entry)
        else:
            return None
    
def str_or_none(entry):
    if entry == '':
        return None
    else:
        return entry   


def json_dict(o):
    return json_obj([dict(d) for d in o])

def json_dict_forecast(o):
    forecast_dict = {};
    for d in o:
        forecast_dict[d.channel] = dict(d)
    return json_obj(forecast_dict)


def json_obj(o):
    return jsonify(dict(res=o))

def get_sql(sql):
    s = db.session
    sql = a.text(sql)
    res = s.execute(sql);
    return  res.fetchall()

def pivot_1(data):
    cols = sorted(set(row[1] for row in data))
    pivot = list((k, defaultdict(lambda: 0, (islice(d, 1, None) for d in data))) 
             for k, data in groupby(data, itemgetter(0)))
    res = [[k] + [details[c] for c in cols] for k, details in pivot] 
    return [['Key'] + cols] + res
 
def pivot_2(data):
    cols = sorted(set(row[1] for row in data))
    pivot = list((k, defaultdict(lambda: u'0|0', (islice(d, 1, None) for d in data))) 
             for k, data in groupby(data, itemgetter(0)))
    res = [[k] + [details[c] for c in cols] for k, details in pivot] 
    return [['Key'] + cols] + res 
 
def pivot_19(data):
    cols = sorted(set(row[19] for row in data))
    print(cols)
    pivot = list((k, defaultdict(lambda: 0, (islice(d, 19, None) for d in data))) 
             for k, data in groupby(data, itemgetter(0)))
    res = [[k] + [details[c] for c in cols] for k, details in pivot] 
    return [['Key'] + cols] + res 
 
    
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

    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Unicode, unique=True)
      
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.Unicode, unique=True)   
         
class Industry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sic = db.Column(db.Integer)
    naics = db.Column(db.Integer)
    industry_name = db.Column(db.Unicode)
    def __init__(self, sic=None, naics=None, industry_name=None):
        self.sic = sic
        self.naics = naics
        self.industry_name = industry_name
   
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    parent = db.Column(db.Unicode)
   

class Advertiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertiser = db.Column(db.Unicode)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    parent = db.relationship('Parent', backref=backref("advertisers", cascade="all,delete"))
    sic = db.Column(db.Integer)
    naics = db.Column(db.Integer)
    adjusted_industry = db.Column(db.Unicode)
    consolidated_industry = db.Column(db.Unicode)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

"""
class Association(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref('associations', cascade='all,delete'))
    rep_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    rep = db.relationship('Rep')
"""

association_table = db.Table('association', db.Model.metadata,
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id', ondelete="CASCADE")),
    db.Column('rep_id', db.Integer, db.ForeignKey('rep.id'))
)

class Rep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repID = db.Column(db.Unicode, unique=True)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    employeeID = db.Column(db.Unicode)
    date_of_hire = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    seller = db.Column(db.Boolean)
    department = db.Column(db.Unicode)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    manager_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    manager = db.relationship('Rep', remote_side=[id])
    type = db.Column(db.Unicode)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product')
    def name(self):
        return u"%s, %s" % (self.last_name, self.first_name)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.Date)
    campaign = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', lazy='joined')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    advertiser_id = db.Column(db.Integer, db.ForeignKey('advertiser.id'))
    advertiser = db.relationship('Advertiser')
    agency = db.Column(db.Unicode)
    industry = db.Column(db.Unicode)
    agency = db.Column(db.Unicode)
    sfdc_oid = db.Column(db.Integer)    ##  Would like to make this unique, but can't without resolving rep issue
    #rep_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    #rep = db.relationship('Rep')
    # To allow multiple reps.  Right now, this is creating too many problems
    rep = db.relationship('Rep',secondary=association_table)
    cp = db.Column(db.Unicode)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cpm_price = db.Column(db.Float)
    contracted_impr = db.Column(db.Integer)
    booked_impr = db.Column(db.Integer)
    delivered_impr = db.Column(db.Integer)
    contracted_deal = db.Column(db.Float)
    revised_deal = db.Column(db.Float)
    opportunity = db.Column(db.Unicode)
    def get_absolute_url(self):
        return u"/note/%s/" % self.campaign
    def getBookedRev(self, myDate):
        a = self.booked_set.filter(date = myDate)
        if a:
            return a[0].bookedRev
        else:  
            return 0
    def getActualRev(self, myDate):
        a = self.actual_set.filter(date = myDate)
        if a:
            return a[0].actualRev
        else:  
            return 0
    def as_dict(self):
        res = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if(self.advertiser != None):
            res['advertiser'] = self.advertiser.as_dict()
        res['rep'] = [r.as_dict() for r in self.rep if r != None]
        return res
    
    
class Campaignchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign')
    change_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cpm_price = db.Column(db.Float)
    revised_deal = db.Column(db.Float)
    # Question: Do I want to record type of change?

class Booked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.Date)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("bookeds", cascade="all,delete"))
    date = db.Column(db.Date)
    bookedRev = db.Column(db.Float)
    
class Bookedchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("bookedchange", cascade="all,delete"))
    change_date = db.Column(db.Date)
    date = db.Column(db.Date)
    bookedRev = db.Column(db.Float)    
    
class Actual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.Date)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("actuals", cascade="all,delete"))    
    date = db.Column(db.Date)    
    actualRev = db.Column(db.Float)
    
class Actualchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("actualchange", cascade="all,delete"))    
    change_date = db.Column(db.Date)
    date = db.Column(db.Date)    
    actualRev = db.Column(db.Float)    
    

class Sfdc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oid = db.Column(db.Integer)
    ioname = db.Column(db.Unicode)
#    country = db.Column(db.Unicode)
#    signedIO = db.Column(db.Unicode)
#    setUp = db.Column(db.Unicode)
##    sfdc_agency = db.Column(db.Unicode)
    cp = db.Column(db.Unicode)
    channel = db.Column(db.Unicode)
    advertiser = db.Column(db.Unicode)
    owner_name = db.Column(db.Unicode)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
##    last_modified = db.Column(db.Date)
    budget = db.Column(db.Float)
    currency = db.Column(db.Unicode)
    approved = db.Column(db.Boolean)
    
    
class Forecastq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    quarter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    goal = db.Column(db.Float)
    forecast = db.Column(db.Float)
    lastweek = db.Column(db.Float)
    cpm_rec_booking = db.Column(db.Float)
    qtd_booking = db.Column(db.Float)
    deliverable_rev = db.Column(db.Float)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    created = db.Column(db.DateTime)
    
class Forecastyear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    fcst = db.Column(db.Float)
    lastweek = db.Column(db.Float)
    ytd = db.Column(db.Float)


# Create the database tables.
sfdc_table = Sfdc.__table__
campaign_table = Campaign.__table__
rep_table = Rep.__table__
channel_table = Channel.__table__
sfdc_campaign_join = sfdc_table.outerjoin(campaign_table, sfdc_table.c.oid == campaign_table.c.sfdc_oid)

# map to it
class Sfdccampaign(db.Model):
    __table__ = sfdc_campaign_join
    __tablename__ = 'sfdccampaign'
    cid = campaign_table.c.id
    ccp = campaign_table.c.cp
    cstart_date = campaign_table.c.start_date
    cend_date = campaign_table.c.end_date


def strptime_or_none(mydate):
    if(mydate == None):
        return None
    else:
        return D.strptime(mydate,'%Y-%m-%d').date()


def sfdc_from_sfdc(sf):
    s = db.session
    for row in sf.query("""SELECT IO.Name, IO.CreatedDate, IO.LastModifiedDate, IO.Start_Date__c, IO.End_Date__c, IO.Budget__c, IO.SalesChannel__c, IO.Advertiser_Account__c, 
                                op.Name, op.CreatedDate, a.Name, op.CampaignStart__c, op.CampaignEnd__c, op.Rate_Type__c, op.Opportunity_ID__c, op.SalesPlanner__c, 
                                op.LastModifiedDate, op.Owner.Name, 
                                aa.Name, aa.CurrencyIsoCode
                            FROM Insertion_Order__c IO, IO.Opportunity__r op, op.Agency__r a, IO.Advertiser_Account__r aa
                            WHERE op.Id <> null"""):

        #sf_io = row['Insertion_Order__c']


        sf_ioname = row['Name']
        sf_channel = row['SalesChannel__c']
        sf_budget = row['Budget__c']
        try:
            sf_oid = int_or_none(row['Opportunity__r']['Opportunity_ID__c'])
        except:
            print(row['Opportunity__r'])
            print(row['Opportunity__r']['Opportunity_ID__c'])
        sf_cp = row['Opportunity__r']['Rate_Type__c']
        
        start_date = row['Opportunity__r']['CampaignStart__c']
        end_date = row['Opportunity__r']['CampaignEnd__c']
        last_mod_temp = row['Opportunity__r']['LastModifiedDate']
        sf_last_modified = None
        if(last_mod_temp):
            last_modified = last_mod_temp[0:10]
            sf_last_modified = strptime_or_none(last_modified)
    
        sf_start_date = strptime_or_none(start_date)
        sf_end_date = strptime_or_none(end_date)
        
        
        agency_r = row['Opportunity__r']['Agency__r']
        sf_agencyname = None
        if(agency_r):
            sf_agencyname = agency_r['Name']
        owner = row['Opportunity__r']['Owner']
        sf_owner_name = None
        if(owner):
            owner_temp = owner['Name']
            last = re.search('[A-Z][a-z]*$', owner_temp)
            if(last.group() == "Pigeon"):
                sf_owner_name = "Pigeon, Matt"
            else:
                first = re.search('^[A-Z][a-z]*', owner_temp)
                sf_owner_name = last.group() + ", " + first.group()

        advertiser = row['Advertiser_Account__r']
        sf_advertiser = None
        sf_currency = None
        if(advertiser):
            sf_advertiser = advertiser['Name']
            sf_currency = advertiser['CurrencyIsoCode']

        a = Sfdc(oid = sf_oid, channel = sf_channel, sfdc_agency = sf_agencyname, cp = sf_cp, advertiser = sf_advertiser, owner_name = sf_owner_name, start_date = sf_start_date, 
                 end_date = sf_end_date, last_modified = sf_last_modified, budget = sf_budget, ioname = sf_ioname, currency = sf_currency, approved = False)
        s.add(a)
        s.commit()


def readSFDCexcel():
    s = db.session
    s.query(Sfdc).delete()
    wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SFDC OID Report 1-7-13.xls')
    sh = wb.sheet_by_index(0)
    for colnum in range(0, sh.ncols):
        colname = sh.cell(0, colnum).value
        if re.search('Opportunity ID', colname):
            oid_index = colnum
        if re.search('Channel',colname):
            channel_index = colnum
        if re.search('Pricing Model', colname):
            cp_index = colnum
        if re.search('Advertiser',colname):
            advertiser_index = colnum
        if re.search('Opportunity Owner',colname):
            rep_index = colnum   
        if re.search('Start Date',colname):
            start_index = colnum  
        if re.search('End Date',colname):
            end_index = colnum  
        if re.search('Budget$',colname):
            budget_index = colnum
        if re.search('Insertion Order',colname):
            ioname_index = colnum
        if re.search('Currency',colname):
            currency_index = colnum
    for rownum in range(1,sh.nrows):
        oid_val = sh.cell(rownum, oid_index).value
        if oid_val is None or oid_val =='':
            break
        else:
            oid = int(oid_val)
            channel = sh.cell(rownum, channel_index).value
            cp = sh.cell(rownum, cp_index).value
            advertiser = sh.cell(rownum, advertiser_index).value
            rep_name_temp  = sh.cell(rownum, rep_index).value
            last = re.search('[A-Z][a-z]*$', rep_name_temp)
            first = re.search('^[A-Z][a-z]*', rep_name_temp)
            rep_name = last.group() + ", " + first.group()
            start = xldate_as_tuple(sh.cell(rownum,start_index).value,0)[0:3]
            py_start = date(*start) + timedelta(days=1)
            end = xldate_as_tuple(sh.cell(rownum,end_index).value,0)[0:3]
            py_end = date(*end)    
            ioname = sh.cell(rownum, ioname_index).value          
            budget_val = sh.cell(rownum, budget_index).value
            currency = sh.cell(rownum, currency_index).value
            if budget_val == '':
                budget_val = None
            a = Sfdc(oid=oid, channel=channel, cp=cp, advertiser=advertiser, owner_name = rep_name, start_date = py_start, end_date = py_end, budget = budget_val, ioname=ioname, currency=currency, approved = False)
            s.add(a)
            s.commit()



def populateProduct(wb): 
    sh = wb.sheet_by_name('Product')
    for rownum in range(0,8):
        prod = sh.cell(rownum,0).value
        p = Product(product = prod)
        db.session.add(p)
        db.session.commit()
    print("PopulateProduct Finished")


def populateChannel(wb): 
    sh = wb.sheet_by_name('Channel')
    for rownum in range(0,4):
        chan = sh.cell(rownum,0).value
        c = Channel(channel = chan)
        db.session.add(c)
        db.session.commit()
    print("PopulateChannel Finished")
    

def populateParent(wb):         
    sh = wb.sheet_by_name('Parents')   
    for rownum in range(3,1230):
        parent = sh.cell(rownum,8).value
        a = Parent(parent = parent)
        db.session.add(a)   
    db.session.commit()
    print("PopulateParent Finished")


def populateAdvertiser(wb):            
    sh = wb.sheet_by_name('ParentInfo_02082013')
    for rownum in range(4, 2233): #sh.nrows):
        parent = get_or_create(db.session, Parent, parent = sh.cell(rownum,7).value)
        acc = sh.cell(rownum,8).value
        sic = int_or_none(sh.cell(rownum,9).value)
        naics = int_or_none(sh.cell(rownum,10).value)
        adj = str_or_none(sh.cell(rownum,11).value)
        consol = str_or_none(sh.cell(rownum,12).value)
        instance = db.session.query(Advertiser).filter_by(parent = parent, advertiser = acc).first()
        if instance:
            pass
        else:
            a = Advertiser(parent = parent, advertiser = acc, sic = sic, naics = naics, adjusted_industry = adj, consolidated_industry = consol)
            db.session.add(a)
            db.session.commit()
    print("PopulateAdvertiser Finished")            

    
def populateRep(wb):  
    sh = wb.sheet_by_name('RepID')     
    for rownum in range(1, 92):
        repID = sh.cell(rownum,0).value
        last_name = sh.cell(rownum,1).value
        first_name = sh.cell(rownum,2).value
        employeeID = sh.cell(rownum,3).value    
        if isinstance(employeeID, float):
            employeeID = str(int(employeeID))
        date_of_hire = get_date_or_none(sh.cell(rownum,4).value)    
        termination_date = get_date_or_none(sh.cell(rownum,5).value)
        seller = bool(sh.cell(rownum,6).value)
        department = sh.cell(rownum,7).value  
        channel = db.session.query(Channel).filter_by(channel = sh.cell(rownum,8).value).first()  
        try:
            mgr = db.session.query(Rep).filter_by(repID = sh.cell(rownum,9).value).first()
        except:
            mgr = None                      
        mytype = sh.cell(rownum,10).value
        product = get_or_create(db.session, Product, product = sh.cell(rownum,11).value)
        a = Rep(repID = repID, last_name = last_name, first_name = first_name, employeeID = employeeID, date_of_hire = date_of_hire, termination_date = termination_date,
                seller = seller, department = department, channel = channel, manager = mgr, type=mytype, product=product)
        db.session.add(a)
        db.session.commit()
    print("PopulateRep Finished") 


def populateCampaignRevenue(wb):         
    sh = wb.sheet_by_name('Rev032813_574')
    for rownum in range(2,5890): #sh.nrows):
        campaign = sh.cell(rownum,13).value
        print(campaign)
        date_created = date(2013, 3, 28)
        t = sh.cell(rownum,3).value
        product = get_or_create(db.session, Product, product = sh.cell(rownum,4).value)
        chan = sh.cell(rownum,5).value
        if(chan == "MSLAL"):
            chan = "Publisher"
        channel = get_or_create(db.session, Channel, channel = chan)
        try:
            advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,6).value).first()
            #advertiser = get_or_create(db.session, Advertiser, advertiser = sh.cell(rownum,6).value)
        except:
            advertiser = None
            print(sh.cell(rownum,6).value + " not found")
        industry = sh.cell(rownum,8).value
        agency = sh.cell(rownum,9).value
        sfdc_oid = sh.cell(rownum,10).value
        if not isinstance(sfdc_oid, float):
            sfdc_oid = None
        else:
            sfdc_oid = int(sfdc_oid)
        repid = sh.cell(rownum,14).value
        if(repid == "VB"):
            repid = "VV"
        rep = get_or_create(db.session, Rep, repID = repid)          
        cp = sh.cell(rownum,15).value
        try:
            start_date = xldate_as_tuple(sh.cell(rownum,16).value,0)[0:3]
            py_start = date(*start_date)
            end = xldate_as_tuple(sh.cell(rownum,17).value,0)[0:3]
            py_end = date(*end)
        except:
            pass                            
        cpm_price = sh.cell(rownum,19).value
        if not isinstance(cpm_price, float):  
            cpm_price = None
        contracted_impr = sh.cell(rownum,20).value
        if isinstance(contracted_impr, float):
            contracted_impr = int(contracted_impr)
        else:
            contracted_impr = None
        contracted_deal = sh.cell(rownum,21).value
        if not isinstance(contracted_deal, float):  
            contracted_deal = None    
        revised_deal = sh.cell(rownum,23).value
        if not isinstance(revised_deal, float):  
            revised_deal = None
        # For multiple reps:
        camp_instance = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
        if camp_instance:
            camp_instance.rep.append(rep)
            db.session.commit()
            c = camp_instance
        else: 
            if sfdc_oid == 11919:
                camp_instance = db.session.query(Campaign).filter_by(sfdc_oid = 11919).first()
                if camp_instance:
                    c = camp_instance
                    camp_instance.rep.append(rep)
                    db.session.commit()
                else:
                    c = Campaign(campaign = campaign, date_created = date_created, type = t, product = product, channel = channel, advertiser = advertiser, 
                                 industry = industry, agency = agency, sfdc_oid = sfdc_oid, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, cpm_price = cpm_price, 
                                 contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)    
                    db.session.add(c)
                    db.session.commit()
                    cc = Campaignchange(campaign = c, change_date = D.now(), start_date = py_start, end_date = py_end, cpm_price = cpm_price, revised_deal = revised_deal)
                    db.session.add(cc)
                    db.session.commit()
            else:
                c = Campaign(campaign = campaign, date_created = date_created, type = t, product = product, channel = channel, advertiser = advertiser, 
                             industry = industry, agency = agency, sfdc_oid = sfdc_oid, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, cpm_price = cpm_price, 
                             contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)    
                db.session.add(c)
                db.session.commit()
                cc = Campaignchange(campaign = c, change_date = date_created, start_date = py_start, end_date = py_end, cpm_price = cpm_price, revised_deal = revised_deal)
                db.session.add(cc)
                db.session.commit()

            #campaignObj = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
        for colnum in chain(xrange(26,38), xrange(56,68), xrange(88,100)):
            rev = sh.cell(rownum,colnum).value
            if isinstance(rev,float) and rev != 0.0: 
                mydate = xldate_as_tuple(sh.cell(1,colnum).value,0)[0:3]
                pyDate = date(*mydate)
                book_instance = db.session.query(Booked).filter_by(campaign=c, date=pyDate).first()
                if book_instance:
                    rev = book_instance.bookedRev + rev
                    book_instance.bookedRev = rev
                else:    
                    a = Booked(campaign=c, date_created = date_created, date=pyDate, bookedRev=rev)
                    db.session.add(a)
                aa = Bookedchange(campaign=c, change_date = date_created, date=pyDate, bookedRev = rev)
                db.session.add(aa)
                db.session.commit()
            
        for colnum in chain(xrange(41,53), xrange(73,85), xrange(103,115)):
            rev = sh.cell(rownum,colnum).value
            if isinstance(rev,float) and rev != 0.0: 
                mydate = xldate_as_tuple(sh.cell(1,colnum).value,0)[0:3]
                pyDate = date(*mydate)
                actual_instance = db.session.query(Actual).filter_by(campaign=c, date=pyDate).first()
                if actual_instance:
                    rev = actual_instance.actualRev + rev
                    actual_instance.actualRev = rev
                else:    
                    a = Actual(campaign=c, date_created = date_created, date=pyDate, actualRev=rev)
                    db.session.add(a)
                    # For CPM, we need to add 
                    if cp == "CPM" and pyDate.year == 2013:
                        b = Booked(campaign=c, date_created = date_created, date=pyDate, bookedRev=rev)
                        db.session.add(b)
                        bb = Bookedchange(campaign=c, change_date = date_created, date=pyDate, bookedRev = rev)
                        db.session.add(bb)
                aa = Actualchange(campaign=c, change_date = date_created, date=pyDate, actualRev = rev)                    
                db.session.add(aa)
                db.session.commit()
    print("PopulateRevenue Finished") 
    
    
def populateCampaignRevenue09(wb):         
    sh = wb.sheet_by_name('Rev09')
    for rownum in range(4,264): #sh.nrows):
        date_created = D.now()
        product = get_or_create(db.session, Product, product = sh.cell(rownum,0).value)
        try:
            advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,2).value).first()
            #advertiser = get_or_create(db.session, Advertiser, advertiser = sh.cell(rownum,6).value)
        except:
            advertiser = None
            print(sh.cell(rownum,2).value + " not found")
        agency = sh.cell(rownum,3).value
        campaign = sh.cell(rownum,4).value
        t = sh.cell(rownum,5).value
        channel = get_or_create(db.session, Channel, channel = sh.cell(rownum,6).value)
        cp = sh.cell(rownum,7).value
        industry = sh.cell(rownum,8).value
        if(industry == '(blank)'):
            industry = None
        repid = sh.cell(rownum,9).value
        if(repid == "VB"):
            repid = "VV"
        rep = get_or_create(db.session, Rep, repID = repid)
        try:
            start_date = xldate_as_tuple(sh.cell(rownum,10).value,0)[0:3]
            py_start = date(*start_date)
            end = xldate_as_tuple(sh.cell(rownum,11).value,0)[0:3]
            py_end = date(*end)
        except:
            pass                            
        contracted_deal = sh.cell(rownum,12).value
        if not isinstance(contracted_deal, float):  
            contracted_deal = None    
        revised_deal = sh.cell(rownum,12).value
        if not isinstance(revised_deal, float):  
            revised_deal = None
        # For multiple reps:
        instance = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
        if instance:
            instance.rep.append(rep)
            db.session.commit()
            c = instance
        else: 
            c = Campaign(campaign = campaign, date_created = date_created, type = t, product = product, channel = channel, advertiser = advertiser, industry = industry, 
                         agency = agency, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, contracted_deal = contracted_deal, revised_deal = revised_deal)    
            #print(campaign)
            db.session.add(c)
            db.session.commit()
            cc = Campaignchange(campaign = c, change_date = D.now(), start_date = py_start, end_date = py_end, revised_deal = revised_deal)
            db.session.add(cc)
            db.session.commit()
        #campaignObj = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()     
        for colnum in range(20,32):
            rev = sh.cell(rownum,colnum).value
            if isinstance(rev,float) and rev != 0.0: 
                mydate = xldate_as_tuple(sh.cell(3,colnum).value,0)[0:3]
                pyDate = date(*mydate)
                actual_instance = db.session.query(Actual).filter_by(campaign=c, date=pyDate).first()
                if actual_instance:
                    rev = actual_instance.actualRev + rev
                    actual_instance.actualRev = rev
                else:    
                    a = Actual(campaign=c, date=pyDate, actualRev=rev)
                    db.session.add(a)
                aa = Actualchange(campaign=c, change_date = D.now(), date=pyDate, actualRev = rev)
                db.session.add(aa)
                db.session.commit()
    print("PopulateCampaignRevenue09 Finished") 


def populateCampaignRevenue10(wb):         
    sh = wb.sheet_by_name('Rev10')
    for rownum in range(3,881): #sh.nrows):
        date_created = D.now()
        t = sh.cell(rownum,2).value
        product = get_or_create(db.session, Product, product = sh.cell(rownum,3).value)
        cp = sh.cell(rownum,4).value
        channel = get_or_create(db.session, Channel, channel = sh.cell(rownum,5).value)
        agency = sh.cell(rownum,16).value
        try:
            advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,20).value).first()
            #advertiser = get_or_create(db.session, Advertiser, advertiser = sh.cell(rownum,6).value)
        except:
            advertiser = None
            print(sh.cell(rownum,6).value + " not found")
        campaign = sh.cell(rownum,21).value
        industry = sh.cell(rownum,15).value
        if(industry == '(blank)'):
            industry = None
        repid = sh.cell(rownum,22).value
        if(repid == "VB"):
            repid = "VV"
        rep = get_or_create(db.session, Rep, repID = repid)
        try:
            start_date = xldate_as_tuple(sh.cell(rownum,24).value,0)[0:3]
            py_start = date(*start_date)
            end = xldate_as_tuple(sh.cell(rownum,25).value,0)[0:3]
            py_end = date(*end)
        except:
            pass                            
        contracted_deal = sh.cell(rownum,28).value
        if not isinstance(contracted_deal, float):  
            contracted_deal = None    
        revised_deal = sh.cell(rownum,28).value
        if not isinstance(revised_deal, float):  
            revised_deal = None
        # For multiple reps:
        instance = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
        if instance:
            instance.rep.append(rep)
            db.session.commit()
            c = instance
        else: 
            c = Campaign(campaign = campaign, date_created = date_created, type = t, product = product, channel = channel, advertiser = advertiser, industry = industry, 
                         agency = agency, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, contracted_deal = contracted_deal, revised_deal = revised_deal)    
            #print(campaign)
            db.session.add(c)
            db.session.commit()
            cc = Campaignchange(campaign = c, change_date = D.now(), start_date = py_start, end_date = py_end, revised_deal = revised_deal)
            db.session.add(cc)
            db.session.commit()
        #campaignObj = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
        for colnum in range(37,49):
            rev = sh.cell(rownum,colnum).value
            if isinstance(rev,float) and rev != 0.0: 
                mydate = xldate_as_tuple(sh.cell(2,colnum).value,0)[0:3]
                pyDate = date(*mydate)
                actual_instance = db.session.query(Actual).filter_by(campaign=c, date=pyDate).first()
                if actual_instance:
                    rev = actual_instance.actualRev + rev
                    actual_instance.actualRev = rev
                else:    
                    a = Actual(campaign=c, date=pyDate, actualRev=rev)
                    db.session.add(a)
                aa = Actualchange(campaign=c, change_date = D.now(), date=pyDate, actualRev = rev)
                db.session.add(aa)
                db.session.commit()
    print("PopulateCampaignRevenue10 Finished") 


def cleanDB():
    s = db.session
    s.query(Booked).delete()
    s.query(Actual).delete()
    s.query(Campaign).delete()    
    s.commit()
"""
    s.query(Rep).delete()
    s.query(Advertiser).delete()
    s.query(Parent).delete()
    s.query(Industry).delete()    
    s.query(Channel).delete()
    s.query(Product).delete()
"""

## XXX Doesn't work
def DropDB():
    db.session.execute(a.text('DROP TABLE Product CASCADE')); 
    db.session.execute(a.text('DROP TABLE Channel CASCADE')); 



'''
data = get_sql('SELECT * FROM HistoricalCPM')
res = pivot_1(data)
print(json.dumps(list(res), indent=2))
'''


#DropDB()
db.create_all()   
wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SalesMetricData03212013.xls')
#populateChannel(wb)
#populateProduct(wb)
#populateParent(wb)
#populateAdvertiser(wb)
#populateRep(wb)
#populateCampaignRevenue10(wb)
#populateCampaignRevenue(wb)
#populateCampaignRevenue09(wb)
#readSFDCexcel()


#sf = Salesforce(username='rthomas@quantcast.com', password='qcsales', security_token='46GSRjDDmh9qNxlDiaefAhPun')
#ac = sfdc_from_sfdc(sf)




#import pdb; pdb.set_trace()



"""
s = db.session
sql = a.text('SELECT * FROM BookedRevenue')
res = s.execute(sql);
data =  res.fetchall()
print json.dumps([dict(d) for d in data])
"""

print("Leaving models.py")
