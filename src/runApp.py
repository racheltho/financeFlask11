from models import *
from db_utils import *
from flask import Response

#import flask.ext.restless
import flask_restless

import datetime
import sqlalchemy as a
import string


if __name__ == '__main__':
    # Create the Flask-Restless API manager.
    db.create_all()
    #manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)    
    
    # Create API endpoints, which will be available at /api/<tablename> by
    # default. Allowed HTTP methods can be specified as well.
    manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
    manager.create_api(Parent, methods=['GET','POST', 'DELETE', 'PUT'], results_per_page=20000, max_results_per_page=20000)
    manager.create_api(Campaign, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
    manager.create_api(Advertiser, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20000, max_results_per_page=20000)
    manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000, max_results_per_page=2000)
    manager.create_api(Product, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
    manager.create_api(Booked, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
    manager.create_api(Actual, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
    manager.create_api(Campaignchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
    manager.create_api(Bookedchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
    manager.create_api(Actualchange, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
    #manager.create_api(Sfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=10000)
    manager.create_api(Channel, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
    manager.create_api(Forecastq, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
    manager.create_api(Forecastyear, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
    manager.create_api(Newsfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
    manager.create_api(Channelmapping, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
    manager.create_api(Changesfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
    #manager.create_api(Sfdccampaign, methods=['GET'], results_per_page=20)

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

    @app.route('/api/newbookedchanges')
    def get_booked_changes():
        data = get_sql("SELECT * FROM NewBookedChanges")
        res = pivot_2(data)
        return json_obj(res)

    @app.route('/api/forecastq')
    def get_forecast_q():
        data = get_sql("SELECT * FROM ForecastThisQ")
        return json_dict_dict(data,"channel")

    @app.route('/api/lastforecast')
    def get_forecast_lastweek():
        data = get_sql("SELECT * FROM ForecastLastWeek")
        return json_dict_dict(data, "channel_id")

    @app.route('/api/forecastyear')
    def get_forecast_year():
        data = get_sql("SELECT * FROM ForecastThisYear")
        return json_dict(data)

    @app.route('/api/forecastweekof')
    def get_weekof():
        data = get_sql("SELECT date FROM Forecastq GROUP by date ORDER BY date DESC")
        return json_dict(data)


    @app.route('/api/weekof/<weekdate>')
    def get_forecast_weekof(weekdate):
        data = get_sql("SELECT CH.channel, F.forecast, F.lastweek, F.cpm_rec_booking, F.qtd_booking, F.deliverable_rev, F.goal FROM forecastq F JOIN (SELECT MAX(created) AS lastweek_date, channel_id FROM forecastq WHERE date = date '" + str(weekdate) + "' GROUP BY channel_id) AS C ON F.channel_id = C.channel_id AND F.created = C.lastweek_date JOIN channel CH ON F.channel_id = CH.id ")
        return json_dict(data)


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

    @app.route('/api/sfdc_adver/<string:sfdc_advertiser>')
    def get_sfdc_adver(sfdc_advertiser):
        data = get_sql('SELECT A.id, A.advertiser FROM advertiser A WHERE similarity(A.advertiser, \'' + sfdc_advertiser + '\') >= .25 ORDER by similarity(A.advertiser, \'' + sfdc_advertiser + '\') DESC LIMIT 3')
        #    data = get_sql('SELECT * FROM advertiser A WHERE similarity(A.advertiser, \'nintend\') > .4 ORDER by similarity(A.advertiser, \'nintend\') DESC LIMIT 3')
        return json_dict(data)

    print("Ready to run app")

    # start the flask loop
    app.run(host='0.0.0.0')

