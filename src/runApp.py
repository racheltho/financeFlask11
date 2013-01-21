from models import *

import flask.ext.restless
import datetime
import sqlalchemy as a

# Create the Flask-Restless API manager.

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
#manager.create_api(ParentAgency, methods=['GET','POST', 'DELETE', 'PUT'])
manager.create_api(Campaign, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Advertiser, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
manager.create_api(Product, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Booked, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Actual, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Sfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Channel, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
manager.create_api(Sfdccampaign, methods=['GET'], results_per_page=20)

@app.route('/api/bookeddata')
def get_bookeddata():
    data = get_sql('SELECT * FROM BookedRevenue')
    return json_dict(data)

@app.route('/api/historicaldata')
def get_historicaldata():
    data = get_sql('SELECT * FROM HistoricalRevenue')
    return json_dict(data)

@app.route('/api/count2011')
def get_count2011():
    data = get_sql('SELECT * FROM HistoricalCount2011')
    return json_dict(data)

@app.route('/api/count2012')
def get_count2012():
    data = get_sql('SELECT * FROM HistoricalCount2012')
    return json_dict(data)

@app.route('/api/historicalcpm')
def get_historicalcpm():
    data = get_sql('SELECT * FROM HistoricalCPM')
    res = pivot_1(data)
    return json_obj(res)

"""
data = get_sql('SELECT * FROM HistoricalCPM')
res = pivot_1(data)
print json.dumps(list(res), indent=2)
"""

# start the flask loop
app.run()