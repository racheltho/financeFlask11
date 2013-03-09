<<<<<<< HEAD
Project Summary
==============
>>>>>>> ceef466ee29b016287f16b4fb636f08431ddad4c

<h2> Motivation: </h2> This project was created to replace a large, messy excel spreadsheet that required several people to spend many hours manually entering and analyzing data each week.  Because of the manual nature, as the amount of data increased, errors were inevitably introduced and the process had become unmanageably time-consuming.<h2>

<h2> Overview: </h2> I've tried to take advantage of the built in functionality of flaks-restless, sqlalchemy, and angularjs to keep my code as clean and as simple as possible.

The basic layout is as follows:

models.py:
=========
Here is the code to create the Flask application and the Flask-SQLAlchemy object.  This creates the connection with the database, automates the creation of tables corresponding to the classes I define next, and allows for the creation of sessions in which records are added to the tables.

<code>
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres@localhost/mydatabase11'
db = flask_sqlalchemy.SQLAlchemy(app)
</code>

Below is a sample of one of my classes.  Notice that there are foreign keys joining to the channel and product tables, and a self-join back to the rep table (for the manager).
<code>
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
</code>

When <code> db.createall() </code> is called, tables will be created in the database for all new classes.



<h2> More challenging/unusual points: </h2>  

<h3>Pairing (SFDC) SalesForce and Campaigns:</h3>
When a record shows up in SalesForce, it may be a new campaign, or it may be a modification of a campaign that already exists.  I wanted to display a list of newly entered SalesForce records, and if the campaign already existed, to display it directly after the corresponding SalesForce record so that the user could compare how the fields were different.  If the campaign did not exist yet, I wanted to give the user the option to create it using the SalesForce data.

In order to do this, I needed ng-repeat to loop through an outerjoin of SFDC (salesforce) and campaign records.  I put my ng-repeat directive in <tbody> instead of my usual location within <tr>.  I also used the directive ng-show inside of <tr> to only show the campaign if it existed, and to show different buttons for cases for the SFDC record where a corresponding campaign existed (edit or approve) and where it didn't (create).


Here is my html code:
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
            		<td class="camp" colspan="12"> (No campaign) <a href="#/create?fromsfdc=	{{sfdc_camp.id}}"><button>Create</button></a></td>
        	    </tr>
       	    	</tbody>
	</table>
	</code>

And here is the code within models.py to create the join:
<code>
sfdc_table = Sfdc.__table__
campaign_table = Campaign.__table__
sfdc_campaign_join = sfdc_table.outerjoin(campaign_table, sfdc_table.c.oid == campaign_table.c.sfdc_oid)
</code>

When the campaign does not already exist, and the user hits create, the user will be directed to the usual campaign creation form, only with some fields already populated with the relevant info from the SalesForce record.  This is does within app.js, within the CreateCtrl controller.

<pre><code>
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
</code></pre>
