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
from time import mktime, strptime, struct_time
from datetime import date, timedelta
from datetime import datetime as D
from xldate import xldate_as_tuple

import sklearn
from flask import jsonify
from itertools import groupby, islice, chain
from operator import itemgetter
from collections import defaultdict

from requests.auth import AuthBase
from sanetime import time
from werkzeug.urls import Href
import requests

import csv


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

def get_or_none(session, model, **kwargs):
    for name, value in kwargs.items():
        if value is None or value == "":
            return None
        else:
            instance = session.query(model).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                return None


def get_date_or_none(entry):
    my_date = None
    if isinstance(entry, float):
        try:
            date_tuple = xldate_as_tuple(entry,0)[0:3]
            my_date = date(*date_tuple)
        except:
            my_date = None
    return my_date


def sfdc_date_or_none(entry):
    my_date = None
    try:
        my_date = D(int(entry[0:4]), int(entry[5:7]), int(entry[8:10]))
    except:
        my_date = None
    return my_date

def sfdc_datetime_or_none(entry):
    my_date = None
    try:
        my_date = D(int(entry[0:4]), int(entry[5:7]), int(entry[8:10]), int(entry[11:13]), int(entry[14:16]), int(entry[17:19]))
    except:
        my_date = None
    return my_date


def int_or_none(entry):
    if entry == '':
        return None
    else:
        if isinstance(entry,int) or isinstance(entry, float) or isinstance(entry, str) or isinstance(entry, unicode):
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

def json_dict_dict(o, field):
    forecast_dict = {};
    for d in o:
        forecast_dict[d[field]] = dict(d)
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
         
class Channelmapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salesforce_channel = db.Column(db.Unicode)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    countrycode = db.Column(db.Unicode)
         
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
    territory = db.Column(db.Unicode)
    manager = db.Column(db.Unicode)
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
    sfdc_oid = db.Column(db.Integer)
    sfdc_ioid = db.Column(db.Unicode)
    ioauto = db.Column(db.Integer)
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
    
class Changesfdc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    field = db.Column(db.Unicode)
    iohid = db.Column(db.Unicode)
    deleted = db.Column(db.Boolean)
    newvalue_date = db.Column(db.Date)
    oldvalue_date = db.Column(db.Date)
    newvalue_budg = db.Column(db.Float)
    oldvalue_budg = db.Column(db.Float)
    parentid = db.Column(db.Unicode)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("campaigns", cascade="all,delete"))


class Newsfdc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ioid = db.Column(db.Unicode)
    opid = db.Column(db.Integer)
    ioauto = db.Column(db.Integer)
    optype = db.Column(db.Unicode)
    dealtype = db.Column(db.Unicode)
    saleschannel = db.Column(db.Unicode)
    advertiseracc = db.Column(db.Unicode)
    opname = db.Column(db.Unicode)
    ioname = db.Column(db.Unicode)
    campname = db.Column(db.Unicode)
    salesplanner = db.Column(db.Unicode)
    pricing = db.Column(db.Unicode)
    start = db.Column(db.Date)
    end = db.Column(db.Date)
    setup = db.Column(db.Unicode)
    opindustry = db.Column(db.Unicode)
    totalcampbudget = db.Column(db.Float)
    budget = db.Column(db.Float)
    signedio = db.Column(db.Unicode)
    geo = db.Column(db.Unicode)
    arledger = db.Column(db.Unicode)
    erpsync = db.Column(db.Unicode)
    oracle = db.Column(db.Integer)
    invoiceemail = db.Column(db.Unicode)
    owner_last = db.Column(db.Unicode)
    owner_first = db.Column(db.Unicode)
    agency = db.Column(db.Unicode)
    sfdc_date_created = db.Column(db.Date)
    date_created = db.Column(db.Date)
    approved = db.Column(db.Boolean)
    rep_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    rep = db.relationship('Rep')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')

    
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


def strptime_or_none(mydate):
    if(mydate == None):
        return None
    else:
        return D.strptime(mydate,'%Y-%m-%d').date()


def write_channels(sf):
    with open('channels.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        for row in sf.query("SELECT CreatedById,CreatedDate,Field,Id,IsDeleted,NewValue,OldValue FROM Insertion_Order__History IOH WHERE Field = 'Budget__c'  AND CreatedDate >= LAST_WEEK  ORDER BY Field ASC NULLS FIRST  LIMIT 50"):
            sales_channel = row['SalesChannel__c']
            spamwriter.writerow(sales_channel)
              
            
def get_changedsfdc(sf):
    s = db.session
    for row in sf.query("""SELECT CreatedDate, Field, Id, IsDeleted, NewValue, OldValue, ParentId
                            FROM Insertion_Order__History 
                            WHERE (Field = 'Budget__c'  OR Field = 'Start_Date__c' OR Field = 'End_Date__c')
                            AND CreatedDate >= LAST_WEEK   """):
        
        sf_created = row['CreatedDate']
        sf_field = row['Field']
        sf_iohid = row['Id']
        sf_deleted = row['IsDeleted']
        sf_parentid = row['ParentId']
        
        if sf_field == "Budget__c":
            newvalue_budg = row['NewValue']
            oldvalue_budg = row['OldValue']
            newvalue_date = None
            oldvalue_date = None
        else:
            newvalue_date = sfdc_datetime_or_none(row['NewValue'])
            oldvalue_date = sfdc_datetime_or_none(row['OldValue'])
            newvalue_budg = None
            oldvalue_budg = None

        sf_campaign = s.query(Campaign).filter_by(sfdc_ioid = sf_parentid).first()
        
        a = Changesfdc(created = sf_created, field = sf_field, iohid = sf_iohid, deleted = sf_deleted, newvalue_date = newvalue_date, oldvalue_date = oldvalue_date,
                       newvalue_budg = newvalue_budg, oldvalue_budg = oldvalue_budg, parentid = sf_parentid, campaign = sf_campaign)
        s.add(a)
        s.commit()


def get_newsfdc(sf):
    s = db.session
    for row in sf.query("""SELECT IO.id, op.Opportunity_ID__c, IO.rtbid__c, aa.Type, op.Type, IO.SalesChannel__c, aa.Name, op.Name, IO.Name, op.Campaign_EVENT__c, op.SalesPlanner__c, op.Rate_Type__c, 
                                IO.Start_Date__c, IO.End_Date__c, IO.SetUp_Status__c, aa.Industry, op.rm_Amount__c, IO.Budget__c, aa.SignedIO__c, aa.AR__c, aa.ERPSyncStatus__c, aa.OracleCustomer__c, 
                                aa.InvoiceDistEmail__c, IO.GeoTargeting__c, op.Owner.Name, IO.CreatedDate, ag.Name
                        FROM Insertion_Order__c IO, IO.Opportunity__r op, op.Agency__r ag, IO.Advertiser_Account__r aa
                        WHERE IO.CreatedDate >= LAST_WEEK AND IO.Opportunity__r.id <> null"""):

        try:
            sf_agency = row['Opportunity__r']['Agency__r']['Name']
        except:
            sf_agency = None
            
        opp_r = row['Opportunity__r']

        adacc_r = row['Advertiser_Account__r']
        
        sf_ioid = row['Id']
        
        try:
            sf_opid = int_or_none(opp_r['Opportunity_ID__c'])
        except:
            sf_opid = None
        sf_ioauto = row['rtbid__c']
        sf_optype = adacc_r['Type']
        try:
            sf_dealtype = opp_r['Type']
        except:
            sf_dealtype = None
        sf_saleschannel = row['SalesChannel__c']
        try:
            temp_ad = adacc_r['Name']
            sf_advertiseracc = re.sub("'", "", temp_ad)
        except:
            sf_advertiseracc = None
        try:
            sf_opname = opp_r['Name']
        except:
            sf_opname = None
        
        sf_ioname = row['Name']
        sf_campname = opp_r['Campaign_EVENT__c']
        sf_salesplanner = opp_r['SalesPlanner__c']
        sf_pricing = opp_r['Rate_Type__c']
        start_str = row['Start_Date__c']
        end_str = row['End_Date__c']
        created_str = row['CreatedDate']
        sf_created = sfdc_date_or_none(created_str)
        sf_start = sfdc_date_or_none(start_str)
        sf_end = sfdc_date_or_none(end_str)
        try:
            print(row['Setup_Status__c'])
            sf_setup = row['Setup_Status__c']
        except:
            sf_setup = None
        sf_opindustry = adacc_r['Industry']
        sf_totalcampbudg = opp_r['rm_Amount__c']
        sf_budget = row['Budget__c']
        sf_signedio = adacc_r['SignedIO__c']
        sf_geo = row['GeoTargeting__c']
        sf_arledger = adacc_r['AR__c']
        sf_erpsync = adacc_r['ERPSyncStatus__c']
        sf_oracle = adacc_r['OracleCustomer__c']
        sf_invoice = adacc_r['InvoiceDistEmail__c']
        sf_owner = opp_r['Owner']
        sf_owner_last = None
        sf_owner_first = None
        if(sf_owner):
            owner_temp = sf_owner['Name']
            last = re.search('[A-Z][a-z][A-Z]?[a-z]*$', owner_temp)
            sf_owner_last = last.group()
            first = re.search('^[A-Z][a-z]*', owner_temp)
            sf_owner_first = first.group()
            if(sf_owner_last == "Bartlett"):
                sf_owner_last = "Vinco"
                sf_owner_first = "Valerie"
            r = s.query(Rep).filter_by(last_name = sf_owner_last, first_name = sf_owner_first).first()
            if(r is None):
                r = s.query(Rep).filter_by(last_name = sf_owner_last).all()
                if(len(r)==1):
                    r = r[0]
                else:
                    r = None
        else:
            r = None
        cm = s.query(Channelmapping).filter_by(salesforce_channel = sf_saleschannel).first()
        if(cm is not None):
            channel = cm.channel
       


        a = Newsfdc(opid = sf_opid, ioid = sf_ioid, ioauto = sf_ioauto, optype = sf_optype, dealtype = sf_dealtype, saleschannel = sf_saleschannel, advertiseracc = sf_advertiseracc, opname = sf_opname,
                    ioname = sf_ioname, campname = sf_campname, salesplanner = sf_salesplanner, pricing = sf_pricing, start = sf_start, end = sf_end, setup = sf_setup, opindustry = sf_opindustry,
                    totalcampbudget = sf_totalcampbudg, budget = sf_budget, signedio = sf_signedio, geo = sf_geo, arledger = sf_arledger, erpsync = sf_erpsync, oracle = sf_oracle, invoiceemail = sf_invoice, 
                    owner_last = sf_owner_last, owner_first = sf_owner_first, date_created = D.now(), sfdc_date_created = sf_created, agency = sf_agency, approved = False,
                    channel = channel, rep = r)
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
    

def populateChannelmapping(wb):
    sh = wb.sheet_by_name('Channelmapping')
    for rownum in range(1,35):
        sfdc = sh.cell(rownum,0).value
        channel = get_or_none(db.session, Channel, channel = sh.cell(rownum,1).value)
        country = sh.cell(rownum,2).value
        c = Channelmapping(channel = channel, salesforce_channel = sfdc, countrycode = country)
        db.session.add(c)
        db.session.commit()
    print("PopulateChannelMapping finished")
    

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
    for rownum in range(1, 134):
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
        mgr = sh.cell(rownum,9).value
        territory = sh.cell(rownum,12).value
        if territory == '':
            territory = None           
        mytype = sh.cell(rownum,10).value
        product = get_or_create(db.session, Product, product = sh.cell(rownum,11).value)
        a = Rep(repID = repID, last_name = last_name, first_name = first_name, employeeID = employeeID, date_of_hire = date_of_hire, termination_date = termination_date,
                seller = seller, department = department, channel = channel, manager = mgr, type=mytype, product=product, territory = territory)
        db.session.add(a)
        db.session.commit()
    print("PopulateRep Finished") 


def populateCampaignRevenue(wb):         
    sh = wb.sheet_by_name('Rev041813_585')
    for rownum in range(2,6198): #sh.nrows):
        campaign = sh.cell(rownum,13).value
        print(campaign)
        date_created = D.now()
        t = sh.cell(rownum,3).value
        product = get_or_create(db.session, Product, product = sh.cell(rownum,4).value)
        chan = sh.cell(rownum,5).value
        if(chan == "MSLAL"):
            chan = "Publisher"
        channel = get_or_create(db.session, Channel, channel = chan)
        try:
            advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,6).value).first()
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
            db.session.add(c)
            db.session.commit()
            cc = Campaignchange(campaign = c, change_date = D.now(), start_date = py_start, end_date = py_end, revised_deal = revised_deal)
            db.session.add(cc)
            db.session.commit()   
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
            db.session.add(c)
            db.session.commit()
            cc = Campaignchange(campaign = c, change_date = D.now(), start_date = py_start, end_date = py_end, revised_deal = revised_deal)
            db.session.add(cc)
            db.session.commit()
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


db.create_all()   

# Uncomment these to populate database initially
#wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SalesMetricData04222013.xls')
#populateChannel(wb)
#populateChannelmapping(wb)
#populateProduct(wb)
#populateParent(wb)
#populateAdvertiser(wb)
#populateRep(wb)
#populateCampaignRevenue10(wb)
#populateCampaignRevenue(wb)
#populateCampaignRevenue09(wb)

# Uncomment these once a week to read new and changed flights from SalesForce into the database
#sf = Salesforce(username='rthomas@quantcast.com', password='qcsales', security_token='46GSRjDDmh9qNxlDiaefAhPun')
#ac = get_changedsfdc(sf)
#ac = get_newsfdc(sf)
#ac = write_channels(sf)



print("Leaving models.py")
