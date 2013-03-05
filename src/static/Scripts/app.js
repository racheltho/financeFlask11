"use strict";

/*global ListCtrl, EditCtrl, CreateCtrl, HomeCtrl, RepListCtrl, EditRepCtrl, CreateRepCtrl, DashboardCtrl, HistDashboardCtrl, ApproveIOsCtrl, BookedRevCtrl, AgencyDashboardCtrl */

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
           when('/agencydash', {controller: AgencyDashboardCtrl, templateUrl: 'agency_dashboard.html'}).
           when('/historical', { controller: HistDashboardCtrl, templateUrl: 'historical_dashboard.html' }).
           when('/approveIOs', { controller: ApproveIOsCtrl, templateUrl: 'approveIOs.html' }).
           when('/create', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/weekoverweek', { controller: WeekOverWeekCtrl, templateUrl: 'weekoverweek.html' }).
           when('/history/:campaignId', { controller: CampHistoryCtrl, templateUrl: 'camp_history.html' }).
           otherwise({ redirectTo: '/' });
    });     

$.each(['Campaign', 'Advertiser', 'Product', 'Rep', 'Booked', 'Actual', 'Sfdc', 'Channel', 'Sfdccampaign', 'Parent', 'Campaignchange', 'Bookedchange', 'Actualchange'], 
	function(i, s) {
		CampaignApp.factory(s, function ($resource) {
		    return $resource('/api/' + s.toLowerCase() + '/:id', 
		    { id: '@id' }, { update: { method: 'PUT' } });
		});	
	});


var order_by = function(order, dir) {
	return {order_by: [{field: order, direction: dir}]};
};

var HomeCtrl = function($scope, $location) {
	
};

var ListCtrl = function ($scope, $location, $http, Campaign, Booked, Actual) {
	
	$scope.download = function(){
		$http.get('/api/campaigntoexcel').success(function(csv) {
			$scope.downloadtext = "Download successful";		
		});	
	};
	

    var make_query = function() {
        var q = order_by($scope.sort_order, $scope.sort_desc ? "desc": "asc");
        if ($scope.query) {
            q.filters = [{name: "campaign", op: "ilike", val: "%" + $scope.query + "%"} ];
        }
        return angular.toJson(q);
    };

    $scope.search = function () {
        var res = Campaign.get(
            { page: $scope.page, q: make_query(), results_per_page: 20 },
            function () {
                $scope.no_more = res.page === res.total_pages;
                if (res.page===1) { $scope.campaigns=[]; }
                $scope.campaigns = $scope.campaigns.concat(res.objects);
            }
        );
    };

    $scope.show_more = function () { return !$scope.no_more; };
    
    $scope.sort_by = function (ord) {
        if ($scope.sort_order === ord) {$scope.sort_desc = !$scope.sort_desc;}
        else { $scope.sort_desc = false; }
        $scope.sort_order = ord;
        $scope.reset();
    };

    $scope.del = function (id) {
   	
        Campaign.remove({ id: id }, function () {
            $('#item_'+id).fadeOut();
        });
    };

    $scope.reset = function() {
        $scope.page = 1;
        $scope.search();
    };

    $scope.sort_order = 'campaign';
    $scope.sort_desc = false;
    
    $scope.reset();
   
};

var CampHistoryCtrl = function($scope, $routeParams, $http, Campaign, Campaignchange, Bookedchange, Actualchange){
	Campaign.get({ id: $routeParams.campaignId }, function (item) {
        $scope.campaign = item;
    });
    
    var q = order_by("change_date", "asc");
    q.filters = [{name: "campaign_id", op: "eq", val: $routeParams.campaignId} ];
	Campaignchange.get({q: angular.toJson(q)}, function (items) {
        $scope.campaignchanges = items.objects;
    });
	$http.get('/api/bookedchange' + $routeParams.campaignId).success(function(data) {
		$scope.bookedchanges = data.res;
 		$scope.booked_keys = $scope.bookedchanges[0].slice(1);
 		$scope.bchanges = $scope.bookedchanges.slice(1);
	});	
	$http.get('/api/actualchange' + $routeParams.campaignId).success(function(data) {
		$scope.actualchanges = data.res;
 		$scope.actual_keys = $scope.actualchanges[0].slice(1);
 		$scope.achanges = $scope.actualchanges.slice(1);
	});	
};

var WeekOverWeekCtrl = function($scope, $routeParams, $http, Campaign, Campaignchange, Bookedchange, Actualchange){
	$http.get('/api/newbookedchanges').success(function(data){
		$scope.newchanges = data.res;
		$scope.changes_keys = $scope.newchanges[0].slice(1);
		var myslice = $scope.newchanges.slice(1);
 		$scope.changes_data = [];
 		var temp = [];
 		var obj = {};
 		$.each(myslice, function(i,o){ 
 			temp = o[0].split('|');
 			obj = { data1: [temp[0]].concat(temp[1]), data2: [temp[2]] };
 			$.each(o.slice(1), function(i2, o2){ obj.data1 = obj.data1.concat(parseFloat(o2.split('|')[0]));
 												 obj.data2 = obj.data2.concat(parseFloat(o2.split('|')[1]));});
 			$scope.changes_data.push(obj);
 		});
 		//$.each(myslice, function(i,o){ $scope.changes_data[i] = o[0].split('|').concat(o.slice(1));});
		//console.log($scope.changes_data);
		//$.each(myslice, function(i,o){ $scope.changes_data[i] = o[0].split('|').concat($.each(o.slice(1), function(i2, o2){ return o2.split('|')}));})
		debugger;
	});
			
	
};


var DetailsBaseCtrl = function($scope, $location, $routeParams, Campaign, Rep, Advertiser, Product, Channel, Parent, Bookedchange) {
	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};

	$scope.add_rep = function() {
		if (!$scope.new_rep) {return;}
		var reps = $scope.item.rep;
		var new_rep = $scope.new_rep;
		if(_.find(reps, function(o) {return o.id === new_rep.id.toString();})) { return; }
		$scope.item.rep.push(new_rep);
		$scope.new_rep = "";
	};

	$scope.delete_rep = function(rep) {
		if (!rep) {return;}
		var reps = $scope.item.rep;
		var idx = reps.indexOf(rep);
		if (idx<0) {return;}
		$scope.item.rep.splice(idx,1);
		$('#rep_' + rep.id).fadeOut();
	};
		
	$scope.get_from_rep = function(item){
		if (!item) {return;}
    	if (item.product_id) {
        	Product.get( {id: item.product_id}, function(p) {
	        	if(p) {$scope.item.product_id = p.id;}
        	});
        }

    	if (item.channel_id) {
    		Channel.get( {id: item.channel_id}, function(c) {
	        	if(c) {$scope.item.channel_id = c.id;}
	        });
        }
    	$scope.item.type = item.type;
	};
	
	$scope.cancel = function() {
		var path = '/campaigns';
    	if($routeParams.fromsfdc) {path = '/approveIOs';}
    	$location.path(path);
	};
	
	$scope.calculate = function() {
		$scope.item.bookeds = calc_sl($scope.calc_start, $scope.calc_end, $scope.table_bookeds, $scope.calc_deal);
	};
	
	$scope.update_campaign_calcs = function() {
		$scope.calc_start = parseDate($scope.item.start_date);
        $scope.calc_end = parseDate($scope.item.end_date);
        $scope.calc_deal = $scope.item.revised_deal || $scope.item.contracted_deal;
        $scope.item.bookeds = $scope.item.bookeds || [];
	    $.map($scope.item.bookeds, function(val, i) {
	    	val.date = parseDate(val.date);
	    });
	    $scope.item.bookeds = calc_booked_rev($scope.calc_start, $scope.calc_end, $scope.item.bookeds);
	};

	var getSelectAjax = function(fmt, name, sort_by, minchars, xtra_filters) {
		return 	{
			formatSelection: fmt, formatResult: fmt,
			minimumInputLength: minchars,
		    ajax: {
		      url: "/api/" + name,
		      data: function (term, page) {
		        var q = order_by(sort_by, "asc");
		        q.filters = [{name: sort_by, op: "ilike", val: "%" + term + "%"} ];
		        if (xtra_filters) {	q.filters = q.filters.concat(xtra_filters); }
		        return {q:angular.toJson(q)};
		      },
		      results: function (data) { return {results: data.objects}; }
		    },
			initSelection: function(elm, cb) {
				var id=$(element).val();
		        if (id==="") {
		        	return cb(null);
		        }
				return cb(id);
			}
		};
	};
	
	$scope.select_reps = getSelectAjax(function(o) { return o.last_name + ', ' + o.first_name;}, 
		'rep', 'last_name', 0, {name: "seller", op: "eq", val: true}); 
	$scope.select_advertisers = getSelectAjax(function(o) { return o.advertiser;}, 
		'advertiser', 'advertiser', 2);
	
	get_sel_list(Product, 'product', "select_products");
	get_sel_list(Channel, 'channel', "select_channels");

	$scope.item = {};
}; 

var CreateCtrl = function ($scope, $location, $routeParams, $http, Campaign, Campaignchange, Bookedchange, Sfdc, Sfdccampaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Add';

    $scope.save = function () {
    	var path = '/campaigns';
    	if($scope.sfdcid){ 
    		path = '/approveIOs'; 
    		Sfdc.update({ id: $scope.sfdcid}, {approved:true} );
    	}
        $scope.item.advertiser_id = $scope.item.advertiser.id;
        
	    Campaign.save($scope.item, function() {
	    	var now = new Date();
        	var today = $.datepicker.formatDate('yy-mm-dd', now); 
        	var q = order_by("change_date", "asc");
	    	Campaignchange.save({campaign_id: $scope.item.id, change_date : today, start_date: $scope.item.start_date, 
	    		end_date: $scope.item.end_date, cpm_price: $scope.item.cpm_price, revised_deal: $scope.item.revised_deal});
	    	$.each($scope.item.bookeds, function(index, value){
	    		Bookedchange.save({campaign_id: value.campaign_id, change_date: today, date: value.date, bookedRev: value.bookedRev});
	    	});
	    	$location.path(path); });
	    };

    $scope.sfdcid = $routeParams.fromsfdc;
    
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
CreateCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);

var EditCtrl = function ($scope, $location, $routeParams, Campaign, Campaignchange, Bookedchange, Rep, Advertiser, Product, $injector, Booked) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Update';
    $scope.sfdcid = $routeParams.fromsfdc;
    $scope.history = true;

    Campaign.get({ id: $routeParams.campaignId }, function (item) {
        $scope.item = item;
        $scope.update_campaign_calcs();
    } );

    $scope.save = function () {
    	$scope.item.advertiser_id = $scope.item.advertiser.id;
        Campaign.update({ id: $scope.item.id }, $scope.item, function() {
        	var now = new Date();
        	var today = $.datepicker.formatDate('yy-mm-dd', now); 
        	var q = order_by("change_date", "asc");
        	q.filters = [{name: "campaign_id", op: "eq", val: $scope.item.id}, {name:"change_date", op: "eq", val: today} ];
			Campaignchange.get({q: angular.toJson(q)}, function (item) {
				var mycc = item.objects[0];
				if(mycc){
					Campaignchange.update({id: mycc.id, campaign_id: $scope.item.id, change_date : today, start_date: $scope.item.start_date, 
	    				end_date: $scope.item.end_date, cpm_price: $scope.item.cpm_price, revised_deal: $scope.item.revised_deal});
				}else{
					Campaignchange.save({campaign_id: $scope.item.id, change_date : today, start_date: $scope.item.start_date, 
	    				end_date: $scope.item.end_date, cpm_price: $scope.item.cpm_price, revised_deal: $scope.item.revised_deal});
	    		}
			});
    		
	    	$.each($scope.item.bookeds, function(index, value){
	    		var date_str = $.datepicker.formatDate('yy-mm-dd', value.date);
	    		var q = order_by("change_date", "asc");
        		q.filters = [{name: "campaign_id", op: "eq", val: $scope.item.id}, {name:"change_date", op: "eq", val: today}, {name:"date", op:"eq", val: date_str}];
				Bookedchange.get({q: angular.toJson(q)}, function (item) {
					var mybc = item.objects[0];
					if(mybc){
	    				Bookedchange.update({id: mybc.id, campaign_id: $scope.item.id, change_date: today, date: date_str, bookedRev: value.bookedRev});
	    			}else{
	    				Bookedchange.save({campaign_id: $scope.item.id, change_date: today, date: date_str, bookedRev: value.bookedRev});
	    			}
	    		});
	    	});
        	if ($scope.sfdcid) {$location.url('/approveIOs?approved=' + $scope.sfdcid);} 
        	else {$location.path('/campaigns');} 
        });   
    };
    
//    $scope.view_history = function(){
//    	$location.path('/history/:id');
//    }
    
};
EditCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);

var DashboardCtrl = function ($scope, $http) {
	$http.get('/api/thisrev').success(function(data) {
 		$scope.this_chart = data.res;
 		$scope.this_keys = $scope.this_chart[0].slice(1);
 		var myslice = $scope.this_chart.slice(1);
 		$scope.this_data = []; 
 		$.each(myslice, function(i,o){ $scope.this_data[i] = o[0].split('|').concat(o.slice(1));});
 	});

	// return true if item at this index is the same as the last one 	
 	$scope.channel = function(index) {
 		if(index === 0 || !$scope.this_data[index]) {return true;}
 		if($scope.this_data[index-1][0] === $scope.this_data[index][0]) {return false;}
 		return true;
 	};
 	$scope.spanamt = function(index) {
 		return $scope.channel(index+1) ? 1 : 2;
 	};
};

var HistDashboardCtrl = function ($scope, $http) {
 	$http.get('/api/historicalcpm').success(function(data) {
 		$scope.cpm_chart = data.res;
 		$scope.cpm_keys = $scope.cpm_chart[0].slice(1);
 		$scope.cpm_data = $scope.cpm_chart.slice(1);
 	});
 	$http.get('/api/historicalcpa').success(function(data) {
 		$scope.cpa_chart = data.res;
 		$scope.cpa_keys = $scope.cpa_chart[0].slice(1);
 		$scope.cpa_data = $scope.cpa_chart.slice(1);
 	});
 	$http.get('/api/historicalbyq').success(function(data) {
 		$scope.hbyq_chart = data.res;
 		$scope.hbyq_keys = $scope.hbyq_chart[0].slice(1);
 		$scope.hbyq_data = $scope.hbyq_chart.slice(1);
 	});
 	$http.get('/api/count').success(function(data) {
 		$scope.count_chart = data.res;
 		$scope.count_keys = $scope.count_chart[0].slice(1);
 		var myslice = $scope.count_chart.slice(1);
 		$scope.count_data = []; 
 		$.each(myslice, function(i,o){ $scope.count_data[i] = o[0].split('|').concat(o.slice(1));});
 	});

	// return true if item at this index is the same as the last one 	
 	$scope.channel = function(index) {
 		if(index === 0 || !$scope.count_data[index]) {return true;}
 		if($scope.count_data[index-1][0] === $scope.count_data[index][0]) {return false;}
 		return true;
 	};
 	$scope.spanamt = function(index) {
 		return $scope.channel(index+1) ? 1 : 2;
 	};

	$scope.title = 'Revenue';
	$scope.chartData = [$scope.x, $scope.y]; 
 	//$scope.data = $scope.count2011; //[[[0, 1], [1, 5], [2, 2]]];
};


var AgencyDashboardCtrl = function($scope, $http, Parent, Advertiser) {

	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};
	
	get_sel_list(Parent, 'parent', "select_parents");
	//get_sel_list(Advertiser, 'advertiser', "select_advertisers");
	
	var make_ad_query = function() {
        var q = order_by("advertiser", "asc");
        if ($scope.parent_id) { q.filters = [{ name: "parent_id", op: "eq", val: $scope.parent_id } ];}
        return angular.toJson(q);
    };
	
	$scope.getAdvertisers = function(){	
		Advertiser.get({q: make_ad_query()}, function(items){
			$scope.advertisers = items;
		});
		$http.get('/api/agencytable/'+ $scope.parent_id ).success(function(data) {
 			$scope.agency_chart = data.res;
 			$scope.agency_keys = $scope.agency_chart[0].slice(1);
 			var myslice = $scope.agency_chart.slice(1);
 			$scope.agency_data = []; 
 			$.each(myslice, function(i,o){ $scope.agency_data[i] = (o[0].split('|').concat(o.slice(1))).slice(1);
											$scope.agency_data[i][2] = Math.round($scope.agency_data[i][2]);
 											});
 		});
	};
	
	$scope.advertiser_name = function(index) {
 		if(index === 0 || !$scope.agency_data[index]) {return true;}
 		if($scope.agency_data[index-1][1] === $scope.agency_data[index][1]) {return false;}
 		return true;
 	};
 	
	
	
	/* For my original 11 column array:
	 * $.each(myslice, function(i,o){ $scope.agency_data[i] = (o[0].split('|').concat(o.slice(1))).slice(1);
 											$scope.agency_data[i][3] = parseInt($scope.agency_data[i][3],10);
 											$scope.agency_data[i][4] = parseInt($scope.agency_data[i][4],10);
 											$.each([5,6,7,8,9], function(i2,o2){ $scope.agency_data[i][o2] = Math.round($scope.agency_data[i][o2]); });
 											})
 											
 		$scope.spanamt = function(index) {
 		var counter = 1;
 		while(index < $scope.agency_data.length - 1 && $scope.agency_data[index][1] === $scope.agency_data[index+1][1]){
 			index += 1;
 			counter += 1;
 		}
 		return counter;
 		};									
	 
	 */
};


var ApproveIOsCtrl = function($scope, $routeParams, $location, $http, $q, Sfdc, Sfdccampaign) {
	var make_query = function() {
        	var q = order_by("start_date", "asc");
            q.filters = [{name: "approved", op: "eq", val: false}];
            if($scope.query) {q.filters.push({name: "ioname", op: "ilike", val: "%" + $scope.query + "%"});}
        	return angular.toJson(q);
	};
    	
    $scope.show_name = function(last, first) {
    	if (last) {return last + ', ' + first;}
    	return "";
    };
    
    $scope.search = function () {
        var res = Sfdccampaign.get(
            { page: $scope.page, q: make_query(), results_per_page: 20 },
            function () {
                $scope.no_more = res.page === res.total_pages;
                if (res.page===1) { $scope.sfdc_camps=[]; }
                $scope.sfdc_camps = $scope.sfdc_camps.concat(res.objects);
            }
        );
    };
	
	$scope.approve = function (id) {
        Sfdc.update({ id: id }, {approved:true}, function () {
            $('#item_'+id).fadeOut();
        });
    };

	$scope.show_more = function () { return !$scope.no_more; };

    $scope.reset = function() {
        $scope.page = 1;
        $scope.search();
    };
 
    $scope.reset();

	if ($routeParams.approved) {
		$scope.approve($routeParams.approved);
	}
}; 


var RepListCtrl = function ($scope, $location, Rep) {
    var make_query = function() {
        var q = order_by($scope.sort_order, $scope.sort_desc ? "desc": "asc");
        if ($scope.query) {
            //q.filters = [{name: "upper(campaign)", op: "like", val: "%" + $scope.query.toUpperCase() + "%"} ];
            q.filters = [{name: "last_name", op: "ilike", val: "%" + $scope.query + "%"} ];
        }
        return angular.toJson(q);
    };

    $scope.search = function () {
        var res = Rep.get(
            { page: $scope.page, q: make_query() },
            function () {
                $scope.no_more = res.page === res.total_pages;
                if (res.page===1) { $scope.reps=[]; }
                $scope.reps = $scope.reps.concat(res.objects);
            }
        );
    };

    $scope.show_more = function () { return !$scope.no_more; };
    
    $scope.sort_by = function (ord) {
        if ($scope.sort_order === ord) {$scope.sort_desc = !$scope.sort_desc;}
        else { $scope.sort_desc = false; }
        $scope.sort_order = ord;
        $scope.reset();
    };

    $scope.del = function (id) {
        Rep.remove({ id: id }, function () {
            $('#item_'+id).fadeOut();
        });
    };

    $scope.reset = function() {
        $scope.page = 1;
        $scope.search();
    };

    $scope.sort_order = 'last_name';
    $scope.sort_desc = false;
    
    $scope.reset();
   
};

var RepDetailsBaseCtrl = function($scope, $location, Rep, Product, Channel) {
	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};
	
	$scope.add_rep = function () { };
	
	get_sel_list(Rep, 'last_name', "select_reps");
	//get_sel_list(Advertiser, 'advertiser', "select_advertisers");
	get_sel_list(Product, 'product', "select_products");
	get_sel_list(Channel, 'channel', "select_channels");
}; 

var CreateRepCtrl = function ($scope, $location, Campaign, Rep, Advertiser, Product, Channel, $injector) { 
	$injector.invoke(RepDetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Add';

    $scope.save = function () {
        Rep.save($scope.item, function() { $location.path('/replist'); });
    };
};
CreateRepCtrl.prototype = Object.create(RepDetailsBaseCtrl.prototype);

var EditRepCtrl = function ($scope, $location, $routeParams, Campaign, Rep, Advertiser, Product, Channel, $injector) { 
	$injector.invoke(RepDetailsBaseCtrl, this, {$scope: $scope});

    var self = this;
    $scope.btn_text = 'Update';

    Rep.get({ id: $routeParams.repId }, function (item) {
        self.original = item;
        $scope.item = new Rep(item);
    });

    $scope.isClean = function () {
        return angular.equals(self.original, $scope.item);
    };

    $scope.save = function () {
        Rep.update({ id: $scope.item.id }, $scope.item, function() { $location.path('/replist'); });
    };
    
};
EditRepCtrl.prototype = Object.create(RepDetailsBaseCtrl.prototype);
