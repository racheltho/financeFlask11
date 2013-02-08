from models import *
from db_utils import *

import flask.ext.restless
import datetime
import sqlalchemy as a

# Create the Flask-Restless API manager.

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(Parent, methods=['GET','POST', 'DELETE', 'PUT'], results_per_page=20000, max_results_per_page=20000)
manager.create_api(Campaign, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Advertiser, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20000, max_results_per_page=20000)
manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
manager.create_api(Product, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Booked, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Actual, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Sfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Channel, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
manager.create_api(Sfdccampaign, methods=['GET'], results_per_page=20)

@app.route('/api/agencytable/<int:agencyid>')
def get_agency_table(agencyid):
    data = get_sql("SELECT * FROM Agencytable WHERE A LIKE " + str(agencyid) + "|| '|%'")
    res = pivot_1(data)
    return json_obj(res)    

@app.route('/api/campaign_from_sfdc/<int:sfdcid>')
def get_campaign_from_sfdc(sfdcid):
    c = sfdc_to_campaign(sfdcid, db.session)
    return jsonify(c.as_dict())

'''
@app.route('/api/bookeddata')
def get_bookeddata():
    data = get_sql('SELECT * FROM BookedRevenue')
    return json_dict(data)

@app.route('/api/historicaldata')
def get_historicaldata():
    data = get_sql('SELECT * FROM HistoricalRevenue')
    return json_dict(data)
'''
@app.route('/api/count')
def get_count():
    data = get_sql('SELECT * FROM HistoricalCount')
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/historicalcpm')
def get_historicalcpm():
    data = get_sql('SELECT * FROM HistoricalCPM')
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/historicalcpa')
def get_historicalcpa():
    data = get_sql('SELECT * FROM HistoricalCPA')
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/historicalbyq')
def get_historicalbyq():
    data = get_sql('SELECT * FROM HistoricalbyQ')
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/thisrev')
def get_thisrev():
    data = get_sql('SELECT * FROM This_Rev')
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/thismonth')
def get_thismonth():
    data = get_sql('SELECT * FROM This_month')
    return jsonify(data)

@app.route('/api/thisquarter')
def get_thisquarter():
    data = get_sql('SELECT * FROM This_quarter')
    return jsonify(data)

@app.route('/api/thisyear')
def get_thisyear():
    data = get_sql('SELECT * FROM This_year')
    return jsonify(data)




"""
data = get_sql('SELECT * FROM HistoricalCPM')
res = pivot_1(data)
print json.dumps(list(res), indent=2)
"""

print("Ready to run app")

# start the flask loop
app.run()

#print get_count()
