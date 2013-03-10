#FinanceDB Project Summary

##Philosophy:

This code takes advantage of the built in functionality of [Flask-Restless] (https://flask-restless.readthedocs.org/en/latest/), 
[SQLAlchemy] (http://www.sqlalchemy.org/), and [AngularJS] (http://angularjs.org/).  
The goal is to be as clean and simple as possible.

##Motivation: 

This project was created to replace a large, messy excel spreadsheet that required several people to spend many hours 
manually entering and analyzing data each week.  Because of the manual nature, as the amount of data increased, errors 
were inevitably introduced and the process had become unmanageably time-consuming.

##Platform:

FinanceDB uses [PostgreSQL] (http://www.postgresql.org/) for the database and has a Python backend (using the
microframework [Flask] (http://flask.pocoo.org/) ). [AngularJS] (http://angularjs.org/) is used for the frontend and 
[Bootstrap] (http://twitter.github.com/bootstrap/) is used for the styling.  FinanceDB uses [SQLAlchemy] (http://www.sqlalchemy.org/) for the ORM
and [Flask-Restless] (https://flask-restless.readthedocs.org/en/latest/) to create API endpoints around the SQLAlchemy objects.

##Outline:

The basic layout is as follows.

###models.py

Here is the code to create the Flask application and the Flask-SQLAlchemy ORM.  This creates the connection 
with the database, automates the creation of tables corresponding to the classes defined in models.py, 
and allows for the creation of sessions in which records are added, fetched, updated, or deleted from the tables.

```python
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/mydatabase11'
db = flask_sqlalchemy.SQLAlchemy(app)
```

Below is a sample of one of the classes:

```python
class Rep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repID = db.Column(db.Unicode, unique=True)
    last_name = db.Column(db.Unicode)
    first_name = db.Column(db.Unicode)
    employeeID = db.Column(db.Unicode)
    date_of_hire = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    seller = db.Column(db.Boolean)
    department = db.Column(db.Unicode)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel')
    manager_id = db.Column(db.Integer, db.ForeignKey('rep.id'))
    manager = db.relationship('Rep', remote_side=[id])
    type = db.Column(db.Unicode)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product')
    def name(self):
        return u"%s, %s" % (self.last_name, self.first_name)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
```

When ```python db.createall() ``` is called, tables will be created in the database for all new classes.

The [xlrd] (https://pypi.python.org/pypi/xlrd) python library is used to read data from Excel to populate the database 
initially.

```python
wb = xlrd.open_workbook('SalesMetricData02062013.xls')
sh = wb.sheet_by_name('Rev09')

...

for colnum in range(37,49):
            rev = sh.cell(rownum,colnum).value
            if isinstance(rev,float) and rev != 0.0: 
                mydate = xldate_as_tuple(sh.cell(2,colnum).value,0)[0:3]
                pyDate = date(*mydate)
                actual_instance = db.session.query(Actual).filter_by(campaign=c, date=pyDate).first()
                if actual_instance:
                    rev = actual_instance.actualRev + rev
                    actual_instance.actualRev = rev
                else:    
                    a = Actual(campaign=c, date=pyDate, actualRev=rev)
                    db.session.add(a)
                aa = Actualchange(campaign=c, change_date = D.now(), date=pyDate, actualRev = rev)
                db.session.add(aa)
                db.session.commit()
```

###runApp.py

Thanks to Flask_restless, the runApp.py file is pretty simple.  An API manager is created with just one line of code.
Note that ```app```, which is an input argument for the API manager, was defined above in models.py as the
Flask application.

```python
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
```

Endpoints for each class are created as follows (below is the example for the Rep class):

```python
manager.create_api(Rep, methods=['GET', 'POST', 'DELETE', 'PUT'], results_per_page=200)
```

And to run the app:

```python
app.run()
```

However, there are several cases where something other than the standard Class-based API is needed, for instance to
deal with business logic.  In order, to create API endpoints using SELECT statements or VIEWs from SQL:

```python
@app.route('/api/bookedchange<int:campaignid>')
def get_bookedchanges(campaignid):
    data = get_sql("SELECT change_date, date, \"bookedRev\" FROM bookedchange WHERE campaign_id = " + str(campaignid))
    res = pivot_1(data)
    return json_obj(res)

@app.route('/api/historicalbyq')
def get_historicalbyq():
    data = get_sql('SELECT * FROM HistoricalbyQ')
    res = pivot_1(data)
    return json_obj(res)
```

###app.js###

This is the main javascript file and contains the definition of the Angular module, the routing table, the javascript
clients for the flask-restless endpoints, and the controllers.  Angular provides all this functionality in a fairly
concise way.

Below is the definition of CampaignApp as an angular module and a routing table linking up addresses, 
controllers, and html pages.  The angular directive $routeProvider is used for this.

```javascript
var CampaignApp = angular.module("CampaignApp", ["ngResource", "ui"]).
     config(function ($routeProvider) {
         $routeProvider.
           when('/', { controller: ListCtrl, templateUrl: 'list.html' }).
           when('/campaigns', { controller: ListCtrl, templateUrl: 'list.html' }).
           when('/edit/:campaignId', { controller: EditCtrl, templateUrl: 'detail.html' }).
           when('/new', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/replist', { controller: RepListCtrl, templateUrl: 'replist.html' }).
           when('/editrep/:repId', { controller: EditRepCtrl, templateUrl: 'repdetail.html' }).
           when('/newrep', { controller: CreateRepCtrl, templateUrl: 'repdetail.html' }).
           when('/dashboard', { controller: DashboardCtrl, templateUrl: 'dashboard.html' }).
....
           when('/history/:campaignId', { controller: CampHistoryCtrl, templateUrl: 'camp_history.html' }).
           otherwise({ redirectTo: '/' });
    });     
```

The angular method factory, along with the service [$resource] (http://docs.angularjs.org/api/ngResource.$resource), 
is used to create javascript clients for each of the Flask-Restless endpoints.  By default, ```GET```, ```POST```, and
```DELETE``` verbs are created; however the user must specify that ```PUT``` is wanted as well.

```javascript
$.each(['Campaign', 'Advertiser', 'Product', 'Rep', 'Booked', 'Actual', 'Sfdc', 'Channel', 'Sfdccampaign', 'Parent', 'Campaignchange', 'Bookedchange', 'Actualchange'], 
    function(i, s) {
		CampaignApp.factory(s, function ($resource) {
		    return $resource('/api/' + s.toLowerCase() + '/:id', 
		    { id: '@id' }, { update: { method: 'PUT' } });
		});	
	});
```

###calc.js###

###test.js###


##Points of interest:

###Pairing (SFDC) SalesForce and Campaigns:

When a record shows up in SalesForce, it may be a new campaign, or it may be a modification of a campaign that already exists.  I wanted to display a list of newly entered SalesForce records, and if the campaign already existed, to display it directly after the corresponding SalesForce record so that the user could compare how the fields were different.  If the campaign did not exist yet, I wanted to give the user the option to create it using the SalesForce data.

In order to do this, I needed ng-repeat to loop through an outerjoin of SFDC (salesforce) and campaign records.  I put my ng-repeat directive in <tbody> instead of my usual location within <tr>.  I also used the directive ng-show inside of <tr> to only show the campaign if it existed, and to show different buttons for cases for the SFDC record where a corresponding campaign existed (edit or approve) and where it didn't (create).


Here is my html code:

```html
<h2>Approve new and revised IOs</h2>
<form class="form-search">
    <div class="input-append">
    	<input type="text" ng-model="query" class="input-medium search-query" placeholder="Search">
        <button ng-click="reset()" type="submit" class="btn"><i class="icon-search"></i></button>    
    </div>
    <button ng-click="query=''; reset()" ng-disabled="!query" type="submit" class="btn">Reset</button>
   	</div>
</form>

<table class="table table-striped table-condensed table-hover">
	<thead>
		<th></th>
    	<th>SFDC IO ID</th>
		<th>Name</th>
    	<th>CPA/CPM</th>
    	<th>Channel</th>
    	<th>Advertiser</th>
    	<th>Rep Name</th>
    	<th>Start Date</th>
    	<th>End Date</th>
    	<th>Budget</th>
    	<th></th><th></th>
    </thead>
	<tbody ng-repeat="sfdc_camp in sfdc_camps" id="item_{{sfdc_camp.id}}" class="sfdccamp">
		<tr><td> SFDC: </td>
            <td> {{sfdc_camp.oid}} </td>
            <td> {{sfdc_camp.ioname}} </td>
            <td> {{sfdc_camp.cp}} </td>
            <td> {{sfdc_camp.channel }} </td>
            <td> {{sfdc_camp.advertiser}} </td>
            <td> {{sfdc_camp.owner_name}} </td>
            <td> {{sfdc_camp.start_date | date}} </td>
            <td> {{sfdc_camp.end_date | date}} </td>
            <td> {{sfdc_camp.budget | currency}} </td>
            <td></td><td></td></tr>
        <tr ng-show="sfdc_camp.campaign"><td> Campaign: </td>
        	<td> {{sfdc_camp.sfdc_oid}} </td>
        	<td> {{sfdc_camp.campaign}} </td>
        	<td> {{sfdc_camp.ccp }}</td>
           	<td> {{sfdc_camp.channel.channel}}</td>
           	<td> {{sfdc_camp.advertiser.advertiser }}</td>
           	<td> {{show_name(sfdc_camp.last_name, sfdc_camp.first_name) }}</td>
       	 	<td> {{sfdc_camp.cstart_date | date}}</td>
	    	<td> {{sfdc_camp.cend_date | date}}</td>
    		<td> {{sfdc_camp.revised_deal | currency }}</td>
    		<div><td><a href="#/edit/{{sfdc_camp.cid}}?fromsfdc={{sfdc_camp.id}}"><button>Edit</button></a></td>
	            	<td><button ng-click="approve(sfdc_camp.id)">Approve</button></td></div>
	    </tr>
    	<tr ng-show="!sfdc_camp.campaign">
    		<td class="camp" colspan="12"> (No campaign) <a href="#/create?fromsfdc={{sfdc_camp.id}}">
                <button>Create</button></a></td>
	    </tr>
    </tbody>
</table>
```

And here is the code within models.py to create the join:
```python
sfdc_table = Sfdc.__table__
campaign_table = Campaign.__table__
sfdc_campaign_join = sfdc_table.outerjoin(campaign_table, sfdc_table.c.oid == campaign_table.c.sfdc_oid)
```

When the campaign does not already exist, and the user hits create, the user will be directed to the usual campaign creation form, only with some fields already populated with the relevant info from the SalesForce record.  This is does within app.js, within the CreateCtrl controller.

```javascript
var CreateCtrl = function ($scope, $location, $routeParams, $http, Campaign, Campaignchange, Bookedchange, Sfdc, Sfdccampaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

... Other stuff...
    
	if ($scope.sfdcid) {
		$http.get('/api/campaign_from_sfdc/' + $scope.sfdcid).success(function(data) {
			$.each(['campaign', 'advertiser', 'cp', 'type', 'product_id', 'channel_id',
				'advertiser_id', 'contracted_deal', 'start_date', 'end_date'],
				function(i,o) {	if(data[o]) {$scope.item[o] = data[o];}	});
			if (data.rep) {
				$scope.item.rep = data.rep;
			}
	        $scope.update_campaign_calcs();
		});
	}
};
```

