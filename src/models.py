import flask
import sqlalchemy
import psycopg2
import flask.ext.sqlalchemy
import xlrd
import re 
import datetime

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:qcsales@localhost/mydatabase'
db = flask.ext.sqlalchemy.SQLAlchemy(app)
db.create_all()

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        #session.commit()
        #instance = session.query(model).filter_by(**kwargs).first()
        return instance
  
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Unicode, unique=True)
   
class Rep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repID = db.Column(db.Unicode, unique=True)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    employeeID = db.Column(db.Unicode)
    date_of_hire = db.Column(db.Date)
    department = db.Column(db.Unicode)
    channel = db.Column(db.Unicode)
    manager_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    manager = db.relationship('Rep', backref=db.backref('mgr', lazy='dynamic'), remote_side=[id])
    def name(self):
        return u"%s, %s" % (self.last_name, self.first_name)

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
    parent_agency = db.relationship('ParentAgency', backref=db.backref('advertiser', lazy='dynamic'))
    industry_id = db.Column(db.Integer, db.ForeignKey('industry.id'))
    industry = db.relationship('Industry', backref=db.backref('advertiser', lazy='dynamic'))

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', backref=db.backref('campaign', lazy='dynamic'))
    channel = db.Column(db.Unicode)    
    advertiser_id = db.Column(db.Integer, db.ForeignKey('advertiser.id'))
    advertiser = db.relationship('Advertiser', backref=db.backref('campaign', lazy='dynamic'))    
    rep_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    rep = db.relationship('Rep', backref=db.backref('campaign', lazy='dynamic'))
    cp = db.Column(db.Unicode)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cpm_price = db.Column(db.Float)
    contracted_impr = db.Column(db.Integer)
    contracted_deal = db.Column(db.Float)
    revised_deal = db.Column(db.Float)
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

class Booked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=db.backref('booked', lazy='dynamic'))
    date = db.Column(db.Date)
    bookedRev = db.Column(db.Float)
    
class Actual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship('Campaign', backref=db.backref('actual', lazy='dynamic'))    
    date = db.Column(db.Date)    
    actualRev = db.Column(db.Float)    

# Create the database tables.

def populateDB():    
    # Create and fill Tables        
    wb = xlrd.open_workbook('C:/Users/rthomas/Desktop/DatabaseProject/SalesMetricData.xls')
    wb.sheet_names()
    sh = wb.sheet_by_name('Industry')     
    for rownum in range(1,538): #sh.nrows):
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
        a = Industry(sic, naics, industry)
        db.session.add(a)
#        print("sic: " + str(sic) + "   naics: " + str(naics) + "  industry:" + industry)        
    
    sh = wb.sheet_by_name('AdvertiserParent')     
    for rownum in range(0, 1074): #sh.nrows):
        parent = sh.cell(rownum,0).value
        a = ParentAgency(parent = parent)
        db.session.add(a)

    sh = wb.sheet_by_name('Advertiser')
     
    for rownum in range(1, sh.nrows):
        advertiser = sh.cell(rownum,0).value
        parent_name = sh.cell(rownum,1).value
        sic = sh.cell(rownum,2).value
        naics = sh.cell(rownum,3).value
        industry_name = sh.cell(rownum,4).value
        if re.match('[(#]', industry_name):
            industry = None
        else:
            if isinstance(sic,float):
                sic = int(sic)
            else:
                sic = None
            if isinstance(naics,float):
                naics = int(naics)
            else:
                naics = None
            industry =  get_or_create(db.session, Industry, sic = sic, naics = naics, industry_name = industry_name)  
        parent = get_or_create(db.session, ParentAgency, parent = parent_name)
        adv = get_or_create(db.session, Advertiser, advertiser = advertiser)
        adv.parent_agency = parent
        adv.industry = industry
    
    db.session.commit()
    
    ###   Rep table    
       
    sh = wb.sheet_by_name('RepID')
     
    for rownum in range(1, 84):
        repID = sh.cell(rownum,0).value
        last_name = sh.cell(rownum,1).value
        first_name = sh.cell(rownum,2).value
        employeeID = sh.cell(rownum,3).value    
        department = sh.cell(rownum,8).value  
        channel = sh.cell(rownum,9).value    
        if isinstance(employeeID, float):
            employeeID = str(int(employeeID))
        if isinstance(sh.cell(rownum,4).value, float):
            try:
                date_of_hire = datetime.date(int(sh.cell(rownum,5).value), int(sh.cell(rownum,6).value), int(sh.cell(rownum,7).value))
            except:
                date_of_hire = None
        else:
            date_of_hire = None    
        try:
            mgr = db.session.query(Rep).filter_by(repID = sh.cell(rownum,10).value).first()
        except:
            mgr = None                      
        a = Rep(repID = repID, last_name = last_name, first_name = first_name, employeeID = employeeID, date_of_hire = date_of_hire, department = department, channel = channel, manager = mgr)
        db.session.add(a)
    db.session.commit()
    

def cleanDB():
    s = db.session
    s.query(Booked).delete()
    s.query(Actual).delete()
    s.query(Advertiser).delete()
    s.query(Rep).delete()
    s.query(Product).delete()
    s.query(Industry).delete()
    s.query(ParentAgency).delete()
    s.query(Campaign).delete()
    s.commit()
        
cleanDB()
populateDB()
