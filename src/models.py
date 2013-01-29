import flask
import json
import sqlalchemy as a
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, column_property, backref
from sqlalchemy.ext.declarative import declarative_base

import psycopg2
import flask.ext.sqlalchemy
import xlrd
import re 
from datetime import date, timedelta
from xldate import xldate_as_tuple

from flask import jsonify
from itertools import groupby, islice
from operator import itemgetter
from collections import defaultdict

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:qcsales@localhost/mydatabase'
db = flask.ext.sqlalchemy.SQLAlchemy(app)

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
   
class ParentAgency(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    parent = db.Column(db.Unicode)
    
class Advertiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertiser = db.Column(db.Unicode)
    parent_agency_id = db.Column(db.Integer, db.ForeignKey('parent_agency.id'))
    parent_agency = db.relationship('ParentAgency')
    industry_id = db.Column(db.Integer, db.ForeignKey('industry.id'))
    industry = db.relationship('Industry')

'''
association_table = db.Table('association', db.Model.metadata,
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id')),
    db.Column('rep_id', db.Integer, db.ForeignKey('rep.id'))
)'''

class Rep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repID = db.Column(db.Unicode, unique=True)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    employeeID = db.Column(db.Unicode)
    date_of_hire = db.Column(db.Date)
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

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', lazy='joined')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    advertiser_id = db.Column(db.Integer, db.ForeignKey('advertiser.id'))
    advertiser = db.relationship('Advertiser')
    industry = db.Column(db.Unicode)
    agency = db.Column(db.Unicode)
    sfdc_oid = db.Column(db.Integer)    ##  Would like to make this unique, but can't without resolving rep issue
    rep_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    rep = db.relationship('Rep')
    # To allow multiple reps.  Right now, this is creating too many problems
    # rep = relationship('Rep',secondary=association_table)
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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Booked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("bookeds", cascade="all,delete"))
    date = db.Column(db.Date)
    bookedRev = db.Column(db.Float)
    
class Actual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=backref("actuals", cascade="all,delete"))    
    date = db.Column(db.Date)    
    actualRev = db.Column(db.Float)    

class Sfdc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oid = db.Column(db.Integer)
    ioname = db.Column(db.Unicode)
#    country = db.Column(db.Unicode)
#    signedIO = db.Column(db.Unicode)
#    setUp = db.Column(db.Unicode)
#    agency = db.Column(db.Unicode)
    cp = db.Column(db.Unicode)
    channel = db.Column(db.Unicode)
    advertiser = db.Column(db.Unicode)
    owner_name = db.Column(db.Unicode)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    currency = db.Column(db.Unicode)
    approved = db.Column(db.Boolean)

# Create the database tables.

sfdc_table = Sfdc.__table__
campaign_table = Campaign.__table__
rep_table = Rep.__table__
channel_table = Channel.__table__
sfdc_campaign_join = sfdc_table.outerjoin(campaign_table.join(rep_table, campaign_table.c.rep_id == rep_table.c.id), sfdc_table.c.oid == campaign_table.c.sfdc_oid)
#sfdc_campaign_join = sfdc_table.outerjoin(campaign_table, sfdc_table.c.oid == campaign_table.c.sfdc_oid)

# map to it
class Sfdccampaign(db.Model):
    __table__ = sfdc_campaign_join
    __tablename__ = 'sfdccampaign'

    #chanid = channel_table.c.id
    #chanchannel = channel_table.c.channel
    rid = rep_table.c.id
    rchannel_id = rep_table.c.channel_id
    rproduct_id = rep_table.c.product_id
    rtype = rep_table.c.type
    cid = campaign_table.c.id
    ccp = campaign_table.c.cp
    cstart_date = campaign_table.c.start_date
    cend_date = campaign_table.c.end_date
    #cchannel = campaign_table.c.channel
    #cadvertsier = campaign_table.c.advertiser
    
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


def populateDB():    
    # Create and fill Tables        
    wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SalesMetricData.xls')
    
#    sh = wb.sheet_by_name('Channel')
#    for rownum in range(0,4):
#        chan = sh.cell(rownum,0).value
#        c = Channel(channel = chan)
#        db.session.add(c)
#    db.session.commit()
#    
#    
#    sh = wb.sheet_by_name('Industry')     
#    for rownum in range(1,538): #sh.nrows):
#        sic = sh.cell(rownum,0).value
#        naics = sh.cell(rownum,1).value
#        industry = sh.cell(rownum,2).value            
#        if isinstance(sic,float):
#            sic = int(sic)
#        else:
#            sic = None 
#        if isinstance(naics,float):
#            naics = int(naics)
#        else:
#            naics = None    
#        a = Industry(sic, naics, industry)
#        db.session.add(a)
#    db.session.commit()
#
#    
#    sh = wb.sheet_by_name('AdvertiserParent')     
#    for rownum in range(0, 1074): #sh.nrows):
#        parent = sh.cell(rownum,0).value
#        a = ParentAgency(parent = parent)
#        db.session.add(a)
#    
#    db.session.commit()
#    
#    sh = wb.sheet_by_name('Advertiser')
#     
#    for rownum in range(1, sh.nrows):
#        advertiser = sh.cell(rownum,0).value
#        parent_name = sh.cell(rownum,1).value
#        sic = sh.cell(rownum,2).value
#        naics = sh.cell(rownum,3).value
#        industry_name = sh.cell(rownum,4).value
#        if re.match('[(#]', industry_name):
#            industry = None
#        else:
#            if isinstance(sic,float):
#                sic = int(sic)
#            else:
#                sic = None
#            if isinstance(naics,float):
#                naics = int(naics)
#            else:
#                naics = None
#            industry =  get_or_create(db.session, Industry, sic = sic, naics = naics, industry_name = industry_name)  
#        parent = get_or_create(db.session, ParentAgency, parent = parent_name)
#        adv = get_or_create(db.session, Advertiser, advertiser = advertiser)
#        adv.parent_agency = parent
#        adv.industry = industry
#        db.session.commit()
#    
    ###   Rep table    
       
#    sh = wb.sheet_by_name('RepID')
#     
#    for rownum in range(1, 82):
#        repID = sh.cell(rownum,0).value
#        last_name = sh.cell(rownum,1).value
#        first_name = sh.cell(rownum,2).value
#        employeeID = sh.cell(rownum,3).value    
#        department = sh.cell(rownum,5).value  
#        channel = db.session.query(Channel).filter_by(channel = sh.cell(rownum,6).value).first()   
#        if isinstance(employeeID, float):
#            employeeID = str(int(employeeID))
#        if isinstance(sh.cell(rownum,4).value, float):
#            try:
#                date_tuple = xldate_as_tuple(sh.cell(rownum,4).value,0)[0:3]
#                date_of_hire = date(*date_tuple)
#            except:
#                date_of_hire = None
#        else:
#            date_of_hire = None    
#        try:
#            mgr = db.session.query(Rep).filter_by(repID = sh.cell(rownum,7).value).first()
#        except:
#            mgr = None                      
#        type = sh.cell(rownum,8).value
#        product = db.session.query(Product).filter_by(product = sh.cell(rownum,9).value).first()
#        a = Rep(repID = repID, last_name = last_name, first_name = first_name, employeeID = employeeID, date_of_hire = date_of_hire, department = department, channel = channel, manager = mgr, type=type, product=product)
#        db.session.add(a)
#        db.session.commit()
# 

###  Campaign Table
#
#    sh = wb.sheet_by_name('Campaign')
#     
#    for rownum in range(1,3115): #sh.nrows):
#        campaign = sh.cell(rownum,13).value
#        t = sh.cell(rownum,3).value
#        product = get_or_create(db.session, Product, product = sh.cell(rownum,4).value)
#        channel = get_or_create(db.session, Channel, channel = sh.cell(rownum,5).value)
#        advertiser = get_or_create(db.session, Advertiser, advertiser = sh.cell(rownum,6).value)
#        industry = sh.cell(rownum,8).value
#        agency = sh.cell(rownum,9).value
#        sfdc_oid = sh.cell(rownum,10).value
#        if not isinstance(sfdc_oid, float):
#            sfdc_oid = None
#        else:
#            sfdc_oid = int(sfdc_oid)
#        rep = get_or_create(db.session, Rep, repID = sh.cell(rownum,14).value)
#        cp = sh.cell(rownum,15).value
#        start_date = xldate_as_tuple(sh.cell(rownum,16).value,0)[0:3]
#        py_start = date(*start_date)
#        end = xldate_as_tuple(sh.cell(rownum,17).value,0)[0:3]
#        py_end = date(*end)              
#        cpm_price = sh.cell(rownum,19).value
#        if not isinstance(cpm_price, float):  
#            cpm_price = None
#        contracted_impr = sh.cell(rownum,20).value
#        if isinstance(contracted_impr, float):
#            contracted_impr = int(contracted_impr)
#        else:
#            contracted_impr = None
#        contracted_deal = sh.cell(rownum,21).value
#        if not isinstance(contracted_deal, float):  
#            contracted_deal = None    
#        revised_deal = sh.cell(rownum,23).value
#        if not isinstance(revised_deal, float):  
#            revised_deal = None
#        # For multiple reps:
#        '''instance = db.session.query(Campaign).filter_by(campaign = campaign, start_date = py_start, end_date = py_end).first()
#        if instance:
#            instance.rep.append(rep)
#            db.session.commit()
#        else: 
#            if sfdc_oid == 11919:
#                instance = db.session.query(Campaign).filter_by(sfdc_oid = 11919).first()
#                if instance:
#                    instance.rep.append(rep)
#                    db.session.commit()
#                else:
#                    a = Campaign(campaign = campaign, type = t, product = product, channel = channel, advertiser = advertiser, 
#                                 industry = industry, agency = agency, sfdc_oid = sfdc_oid, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, cpm_price = cpm_price, 
#                                 contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)    
#                    db.session.add(a)
#                    db.session.commit()  
#            else:
#                a = Campaign(campaign = campaign, type = t, product = product, channel = channel, advertiser = advertiser, 
#                             industry = industry, agency = agency, sfdc_oid = sfdc_oid, rep = [rep], cp = cp, start_date = py_start, end_date = py_end, cpm_price = cpm_price, 
#                             contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)    
#                print(campaign)
#                db.session.add(a)
#                db.session.commit() 
#                '''
#    
#        a = Campaign(campaign = campaign, type = t, product = product, channel = channel, advertiser = advertiser, 
#                     industry = industry, agency = agency, sfdc_oid = sfdc_oid, rep = rep, cp = cp, start_date = py_start, end_date = py_end, cpm_price = cpm_price, 
#                     contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)    
#        db.session.add(a)
#        db.session.commit()
#    
#    # Fill revenue tables
#    sh = wb.sheet_by_name('Actual')
#    for rownum in range(1,sh.nrows):
#        camp_str = sh.cell(rownum,0).value
#        rep = db.session.query(Rep).filter_by(repID = sh.cell(rownum,1).value).first()
#        product =  db.session.query(Product).filter_by(product = sh.cell(rownum,2).value).first()
#        channel = sh.cell(rownum,3).value
##        advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,4).value).first()
#        start = xldate_as_tuple(sh.cell(rownum,5).value,0)[0:3]
#        py_start = date(*start)
#        end = xldate_as_tuple(sh.cell(rownum,6).value,0)[0:3]
#        py_end = date(*end)              
#        try:
#            campaign = db.session.query(Campaign).filter_by(campaign = camp_str).first()
#            for colnum in range(7,sh.ncols):
#                rev = sh.cell(rownum,colnum).value
#                if isinstance(rev,float) and rev != 0.0: 
#                    mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                    pyDate = date(*mydate)
#                    a = Actual(campaign=campaign, date=pyDate, actualRev=rev)
#                    db.session.add(a)
#        except:
#            try:
#                campaign = db.session.query(Campaign).filter_by(campaign = camp_str, repId = rep, channel=channel, product = product, start_date = py_start, end_date = py_end).first()
#                for colnum in range(7,sh.ncols):                
#                    rev = sh.cell(rownum,colnum).value
#                    if isinstance(rev,float) and rev != 0.0:
#                        mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                        pyDate = date(*mydate)
#                        a = Actual(campaign=campaign, date=pyDate, actualRev=rev)
#                        db.session.add(a)            
#            except:
#                pass
#    db.session.commit()
#    
#    sh = wb.sheet_by_name('Booked')
#    for rownum in range(1,sh.nrows):
#        camp_str = sh.cell(rownum,0).value
#        rep = db.session.query(Rep).filter_by(repID = sh.cell(rownum,1).value).first()
#        product =  db.session.query(Product).filter_by(product = sh.cell(rownum,2).value).first()
#        channel = sh.cell(rownum,3).value
##        advertiser = db.session.query(Advertiser).filter_by(advertiser = sh.cell(rownum,4).value).first()
#        start = xldate_as_tuple(sh.cell(rownum,5).value,0)[0:3]
#        py_start = date(*start)
#        end = xldate_as_tuple(sh.cell(rownum,6).value,0)[0:3]
#        py_end = date(*end)              
#        try:
#            campaign = db.session.query(Campaign).filter_by(campaign = camp_str).first()
#            for colnum in range(7,sh.ncols):
#                rev = sh.cell(rownum,colnum).value
#                if isinstance(rev,float) and rev != 0.0: 
#                    mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                    pyDate = date(*mydate)
#                    a = Booked(campaign=campaign, date=pyDate, bookedRev=rev)
#                    db.session.add(a)
#        except:
#            try:
#                campaign = db.session.query(Campaign).filter_by(campaign = camp_str, repId = rep, channel=channel, product = product, start_date = py_start, end_date = py_end).first()
#                for colnum in range(7,sh.ncols):                
#                    rev = sh.cell(rownum,colnum).value
#                    if isinstance(rev,float) and rev != 0.0:
#                        mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                        pyDate = date(*mydate)
#                        a = Booked(campaign=campaign, date=pyDate, bookedRev=rev)
#                        db.session.add(a)            
#            except:
#                pass
#    db.session.commit()
    
    
    print("PopulateDB Finished")


def cleanDB():
    s = db.session
    s.query(Sfdc).delete()    
    s.query(Booked).delete()
    s.query(Actual).delete()
    s.query(Campaign).delete()    
    s.query(Rep).delete()
    s.query(Advertiser).delete()
    s.query(ParentAgency).delete()
    s.query(Industry).delete()    
    s.query(Channel).delete()
    s.query(Product).delete()
    s.commit()

def json_dict(o):
    return json_obj([dict(d) for d in o])

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

db.create_all()       


'''
data = get_sql('SELECT * FROM HistoricalCPM')
res = pivot_1(data)
print(json.dumps(list(res), indent=2))
'''

#cleanDB()
#populateDB()
#readSFDCexcel()

#instance = db.session.query(Campaign).filter_by(sfdc_oid = 11384).first()
#for rep in instance.rep:
#    print(rep.name())


#query = db.session.query(Campaign)

#import pdb; pdb.set_trace()

#field = getattr(Campaign, "rep")
#field = getattr(field, "last_name")
#direction = getattr(field, "asc")
#query = query.order_by(direction())

"""
s = db.session
sql = a.text('SELECT * FROM BookedRevenue')
res = s.execute(sql);
data =  res.fetchall()
print json.dumps([dict(d) for d in data])
"""

print("Leaving models.py")
