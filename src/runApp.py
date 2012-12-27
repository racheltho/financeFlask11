from models import db, app, Industry, ParentAgency
import flask.ext.restless

# Create the Flask-Restless API manager.

db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
    
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Industry, methods=['GET', 'POST', 'DELETE', 'PUT'])
manager.create_api(ParentAgency, methods=['GET','POST', 'DELETE', 'PUT'])

# start the flask loop
app.run()