import flask
import sqlalchemy
import psycopg2
import flask.ext.sqlalchemy
import flask.ext.restless
import sys
import os
import xlrd
import datetime
import re
from xldate import xldate_as_tuple
from sqlalchemy.orm import sessionmaker
from models import *

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:qcsales@localhost/mydatabase'
db = flask.ext.sqlalchemy.SQLAlchemy(app)


Session = sessionmaker(db)
session = Session()
    # Create and fill Tables
        
wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SalesMetricData.xls')
wb.sheet_names()


    # Fill revenue tables
#    sh = wb.sheet_by_name('Actual')
#    for rownum in range(2,sh.nrows):
#        camp_str = sh.cell(rownum,0).value
#        rep = Rep.objects.get(repID = sh.cell(rownum,1).value)
#        product = Product.objects.get(product = sh.cell(rownum,2).value)
#        channel = Channel.objects.get(channel = sh.cell(rownum,3).value)
#        advertiser = Advertiser.objects.get(advertiser = sh.cell(rownum,4).value)
#        start = xldate_as_tuple(sh.cell(rownum,5).value,0)[0:3]
#        py_start = datetime.date(*start)
#        end = xldate_as_tuple(sh.cell(rownum,6).value,0)[0:3]
#        py_end = datetime.date(*end)       
#        
#        try:
#            campaign = Campaign.objects.get(campaign = camp_str)
#            for colnum in range(7,sh.ncols):
#                rev = sh.cell(rownum,colnum).value
#                if isinstance(rev,float) and rev != 0.0: 
#                    mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                    pyDate = datetime.date(*mydate)
#                    a = Actual(campaign=campaign, date=pyDate, actualRev=rev)
#                    a.save()
#        except:
#            try:
#                campaign = Campaign.objects.get(campaign = camp_str, repId = rep, channel=channel, product = product, advertiser = advertiser, start_date = py_start, end_date = py_end)
#                for colnum in range(7,sh.ncols):                
#                    rev = sh.cell(rownum,colnum).value
#                    if isinstance(rev,float) and rev != 0.0:
#                        mydate = xldate_as_tuple(sh.cell(0,colnum).value,0)[0:3]
#                        pyDate = datetime.date(*mydate)
#                        a = Actual(campaign=campaign, date=pyDate, actualRev=rev)
#                        a.save()               
#            except:
#                pass


####  Campaign Table
#
#    sh = wb.sheet_by_name('Campaign')
#     
#    for rownum in range(1,sh.nrows):
#        campaign = sh.cell(rownum,0).value
#        type = Type.objects.get(type = sh.cell(rownum,1).value)
#        product = Product.objects.get(product = sh.cell(rownum,2).value)
#        channel = Channel.objects.get(channel = sh.cell(rownum,3).value)
#        advertiser, created = Advertiser.objects.get_or_create(advertiser = sh.cell(rownum,4).value)
#        repId, created = Rep.objects.get_or_create(repID = sh.cell(rownum,5).value)
#        cp, created = CP.objects.get_or_create(cp = sh.cell(rownum,6).value)
#        if isinstance(sh.cell(rownum,7).value, float):
#            try:
#                start_date = datetime.date(int(sh.cell(rownum,7).value), int(sh.cell(rownum,8).value), int(sh.cell(rownum,9).value))
#            except ObjectDoesNotExist:
#                start_date = None
#        else:
#            start_date = None  
#        if isinstance(sh.cell(rownum,10).value, float):
#            try:
#                end_date = datetime.date(int(sh.cell(rownum,10).value), int(sh.cell(rownum,11).value), int(sh.cell(rownum,12).value))
#            except ObjectDoesNotExist:
#                end_date = None
#        else:
#            end_date = None    
#        cpm_price = sh.cell(rownum,13).value
#        if not isinstance(cpm_price, float):  
#            cpm_price = None
#        contracted_impr = sh.cell(rownum,14).value
#        if isinstance(contracted_impr, float):
#            contracted_impr = int(contracted_impr)
#        else:
#            contracted_impr = None
#        contracted_deal = sh.cell(rownum,15).value
#        if not isinstance(contracted_deal, float):  
#            contracted_deal = None    
#        revised_deal = sh.cell(rownum,16).value
#        if not isinstance(revised_deal, float):  
#            revised_deal = None            
#        a = Campaign(campaign = campaign, type = type, product = product, channel = channel, advertiser = advertiser, 
#                     repId = repId, cp = cp, start_date = start_date, end_date = end_date, cpm_price = cpm_price, 
#                     contracted_impr = contracted_impr, contracted_deal = contracted_deal, revised_deal =revised_deal)
#        a.save()
    
####   Rep table    
       
#    sh = wb.sheet_by_name('RepID')
#     
#    for rownum in range(1, 84):
#        repID = sh.cell(rownum,0).value
#        last_name = sh.cell(rownum,1).value
#        first_name = sh.cell(rownum,2).value
#        employeeID = sh.cell(rownum,3).value           
#        if isinstance(employeeID, float):
#            employeeID = str(int(employeeID))
#        if isinstance(sh.cell(rownum,4).value, float):
#            try:
#                date_of_hire = datetime.date(int(sh.cell(rownum,5).value), int(sh.cell(rownum,6).value), int(sh.cell(rownum,7).value))
#            except ObjectDoesNotExist:
#                date_of_hire = None
#        else:
#            date_of_hire = None    
#        try:
#            department = Dept.objects.get(dept = sh.cell(rownum,8).value)
#        except ObjectDoesNotExist:
#            department = None
#        try:
#            channel = Channel.objects.get(channel = sh.cell(rownum,9).value)
#        except ObjectDoesNotExist:
#            channel = None    
#        try:
#            mgr = Rep.objects.get(repID = sh.cell(rownum,10).value)
#        except ObjectDoesNotExist:
#            mgr = None
#                      
#        a = Rep(repID = repID, last_name = last_name, first_name = first_name, employeeID = employeeID, date_of_hire = date_of_hire, department = department, channel = channel, manager = mgr)
#        a.save()
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
#            industry, created =  Industry.objects.get_or_create(sic = sic, naics = naics, industry_name = industry_name)
#        parent, created = ParentAgency.objects.get_or_create(parent = parent_name)
#
#        a, created = Advertiser.objects.get_or_create(parent = parent, advertiser = advertiser, industry = industry)

########### Parent    
#    sh = wb.sheet_by_name('AdvertiserParent')
#     
#    for rownum in range(0, 1074): #sh.nrows):
#        parent = sh.cell(rownum,0).value
#        a = ParentAgency(parent = parent)
#        a.save()
#        print(parent)

    
    
#######    # Industry
sh = wb.sheet_by_name('Industry')
     
for rownum in range(2,12): #sh.nrows):
    sic = sh.cell(rownum,0).value
    naics = sh.cell(rownum,1).value
    industry = sh.cell(rownum,2).value
            
    if isinstance(sic,float):
        sic = int(sic)
    else:
        sic = None
    if isinstance(naics,float):
        naics = int(naics)
    else:
        naics = None    
    a = Industry(sic = sic, naics = naics, industry_name = industry)
    session.add(a)
    print("sic: " + str(sic) + "   naics: " + str(naics) + "  industry:" + industry)
        
session.commit()  


# Main
#if __name__ == '__main__':
#    print("hello")
#    load_data()
    
    
    
    