'''
Created on Jan 21, 2013

@author: rthomas
'''

from models import *
from datetime import date

def find_rep_db(name, s):
    print(name)
    last,first = name.split(', ')
    res = s.query(Rep).filter_by(last_name=last)
    res = res.filter(Rep.first_name.ilike(first + '%')).first()
    if (res): 
        print(res.last_name)
        return res
    res = s.query(Rep).filter_by(last_name=last).first()
    if(name == 'Bartlett, Valerie'):
        res = s.query(Rep).filter_by(last_name="Vinco", first_name="Valerie").first()
    return res

def id_or_none(o):
    if (o): return o.id
    return None

def sfdc_to_campaign(sfdcid, ses):
    ses = db.session
    s = ses.query(Sfdc).filter_by(id = sfdcid).first()
    r = find_rep_db(s.owner_name, ses)
    c = Campaign()
    c.campaign = s.ioname
    c.start_date = s.start_date
    c.end_date = s.end_date
    a = ses.query(Advertiser).filter_by(advertiser = s.advertiser).first()
    c.advertiser_id = id_or_none(a)
    c.contracted_deal = s.budget
    c.cp = s.cp
    c.sfdc_oid = s.oid
    c.rep_id = id_or_none(r)

    if (r is None): return c
    
    c.product_id = id_or_none(ses.query(Product).filter_by(id= r.product_id).first())
    c.channel_id = id_or_none(ses.query(Channel).filter_by(id = r.channel_id).first())
    c.type = r.type
    
    return c
