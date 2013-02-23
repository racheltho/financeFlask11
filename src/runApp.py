from models import *
from db_utils import *
from flask import Response

import flask.ext.restless
import datetime
import sqlalchemy as a
import string

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
manager.create_api(Campaignchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Bookedchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Actualchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Sfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
manager.create_api(Channel, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
manager.create_api(Sfdccampaign, methods=['GET'], results_per_page=20)

@app.route('/static/api/campaigntoexcel')
def writeToExcel():
    data = get_sql('SELECT * FROM CampaignBooked')
    newdata = []
    
    for i in range(0,len(data)):
        newdata.append([data[i][0:17]] + [data[i][18]] + [data[i][19]])
        
    res = pivot_1(newdata)
    
    transformed_data = []
    temp = ['Campaign','Type','Product','Channel','Advertiser','Industry','Agency', 'SFDC OID', 'CPA/CPM', 'Start Date', 'End Date', 'CPM Price', 'Contracted Impressions', 'Booked Impressions', 'Delivered Impressions', 'Contracted Deal', 'Revised Deal']
    temp += res[0][1:len(res[0])]
    transformed_data.append(temp)
    
    for i in range(1,len(res)):
        temp = list(res[i][0])
        temp += res[i][1:len(res[i])]
        transformed_data.append(temp)
   
    filename = 'salesmetric' + str(D.today().date()) + '.csv'
    lines = csv2string(transformed_data)
    resp = Response(lines, status=200, mimetype='text/csv')
    resp.headers['Content-Disposition'] = 'attachment; filename=' + filename
    return resp 
    
    """
    with open(filename, 'wb') as fout:
        writer = csv.writer(fout)
        writer.writerows(transformed_data)
    return json.dumps(filename)
    """

@app.route('/api/agencytable/<int:agencyid>')
def get_agency_table(agencyid):
    data = get_sql("SELECT * FROM Agencytable WHERE A LIKE " + str(agencyid) + "|| '|%'")
    res = pivot_1(data)
    return json_obj(res)    

@app.route('/api/bookedchange<int:campaignid>')
def get_bookedchanges(campaignid):
    data = get_sql("SELECT change_date, date, \"bookedRev\" FROM bookedchange WHERE campaign_id = " + str(campaignid))
    res = pivot_1(data)
    return json_obj(res)


@app.route('/api/actualchange<int:campaignid>')
def get_actualchanges(campaignid):
    data = get_sql("SELECT change_date, date, \"actualRev\" FROM actualchange WHERE campaign_id = " + str(campaignid))
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
