from models import db, app, Industry, Campaign, Rep, Booked, Actual, Product, Sfdc, Channel
from flask import jsonify
import flask.ext.restless
import datetime

# Create the Flask-Restless API manager.

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
#manager.create_api(ParentAgency, methods=['GET','POST', 'DELETE', 'PUT'])
manager.create_api(Campaign, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=0)
#manager.create_api(Advertiser, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
manager.create_api(Product, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Booked, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Actual, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Sfdc, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20, max_results_per_page=0)
manager.create_api(Channel, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)

"""
@app.route('/api/sfdcex')
def get_sfdcex():
    s = db.session
    sfdcs = s.query(Sfdc)
    return jsonify(sfdcs)
"""

# start the flask loop
app.run()