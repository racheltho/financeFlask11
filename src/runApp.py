from models import db, app, Industry, ParentAgency, Campaign, Advertiser, Rep, Booked, Actual, Product
import flask.ext.restless
import datetime

# Create the Flask-Restless API manager.

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(ParentAgency, methods=['GET','POST', 'DELETE', 'PUT'])
manager.create_api(Campaign, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=20)
manager.create_api(Advertiser, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Product, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Booked, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)
manager.create_api(Actual, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=2000)

# start the flask loop
app.run()