var CampaignApp = angular.module("CampaignApp", ["ngResource", "ui"]).
     config(function ($routeProvider) {
         $routeProvider.
           when('/', { controller: HomeCtrl, templateUrl: 'home.html' }).
           when('/campaigns', { controller: ListCtrl, templateUrl: 'list.html' }).
           when('/edit/:campaignId', { controller: EditCtrl, templateUrl: 'detail.html' }).
           when('/new', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/replist', { controller: RepListCtrl, templateUrl: 'replist.html' }).
           when('/editrep/:repId', { controller: EditRepCtrl, templateUrl: 'repdetail.html' }).
           when('/newrep', { controller: CreateRepCtrl, templateUrl: 'repdetail.html' }).
           when('/dashboard', { controller: DashboardCtrl, templateUrl: 'dashboard.html' }).
           when('/historical', { controller: HistDashboardCtrl, templateUrl: 'historical_dashboard.html' }).
           when('/approveIOs', { controller: ApproveIOsCtrl, templateUrl: 'approveIOs.html' }).
           when('/create', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/bookedRev/:campaignId', { controller: BookedRevCtrl, templateUrl: 'bookedRev.html' }).
           otherwise({ redirectTo: '/' });
     });

$.each(['Campaign', 'Advertiser', 'Product', 'Rep', 'Booked', 'Actual', 'Sfdc', 'Channel', 'Sfdccampaign'], 
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
	
}

var ListCtrl = function ($scope, $location, Campaign, Booked, Actual) {
    var make_query = function() {
        var q = order_by($scope.sort_order, $scope.sort_desc ? "desc": "asc");
        if ($scope.query) {
            //q.filters = [{name: "upper(campaign)", op: "like", val: "%" + $scope.query.toUpperCase() + "%"} ];
            q.filters = [{name: "campaign", op: "ilike", val: "%" + $scope.query + "%"} ];
        }
        return angular.toJson(q);
    }

    $scope.search = function () {
        var res = Campaign.get(
            { page: $scope.page, q: make_query(), results_per_page: 20 },
            function () {
                $scope.no_more = res.page == res.total_pages;
                if (res.page==1) { $scope.campaigns=[]; }
                $scope.campaigns = $scope.campaigns.concat(res.objects);
            }
        );
    };

    $scope.show_more = function () { return !$scope.no_more; };
    
    $scope.sort_by = function (ord) {
        if ($scope.sort_order == ord) {$scope.sort_desc = !$scope.sort_desc;}
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

function DetailsBaseCtrl($scope, $location, $routeParams, Campaign, Rep, Advertiser, Product, Channel) {
	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};
	
	$scope.get_from_rep = function(){
		var id = $scope.item.rep_id;
		if (!id) return;
    	Rep.get({ id: id }, function (item) {
        	console.log(item);
        	if (item.product_id) {
	        	Product.get( {id: item.product_id}, function(p) {
		        	if(p) $scope.item.product_id = p.id;
	        	});
	        }

        	if (item.channel_id) {
        		Channel.get( {id: item.channel_id}, function(c) {
		        	if(c) $scope.item.channel_id = c.id;
		        });
	        }
        	$scope.item.type = item.type;
	    });		
	}
	
	$scope.cancel = function() {
		var path = '/campaigns';
    	if($routeParams.fromsfdc) path = '/approveIOs';
    	$location.path(path);
	}
	
	
	$scope.add_rep = function () { }
		
	get_sel_list(Rep, 'last_name', "select_reps");
	get_sel_list(Advertiser, 'advertiser', "select_advertisers");
	get_sel_list(Product, 'product', "select_products");
	get_sel_list(Channel, 'channel', "select_channels");
}; 

var CreateCtrl = function ($scope, $location, $routeParams, $http, Campaign, Sfdc, Sfdccampaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Add';

	$scope.save_and_book = function () {
        Campaign.save($scope.item, function() { $location.path('#/bookedRev/{{campaign.id}}'); });
    };

    $scope.save = function () {
    	var path = '/campaigns';
    	if($scope.sfdcid){ 
    		path = '/approveIOs'; 
    		Sfdc.update({ id: $scope.sfdcid}, {approved:true} );
    	}
        Campaign.save($scope.item, function() { $location.path(path); });
    };

    $scope.sfdcid = $routeParams.fromsfdc;
    
	if ($scope.sfdcid) {
		$http.get('/api/campaign_from_sfdc/' + $scope.sfdcid).success(function(data) {
			$.each(['campaign', 'rep_id', 'cp', 'type', 'product_id', 'channel_id', 'advertiser_id', 'contracted_deal', 'start_date', 'end_date'],
			function(i,o) {
				if(data[o]) $scope.item[o] = data[o];
			});
		});
	};
	
};
CreateCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);

var EditCtrl = function ($scope, $location, $routeParams, Campaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    var self = this;
    $scope.btn_text = 'Update';
    $scope.sfdcid = $routeParams.fromsfdc;

    Campaign.get({ id: $routeParams.campaignId }, function (item) {
        self.original = item;
        $scope.item = new Campaign(item);
    });

    $scope.isClean = function () {
        return angular.equals(self.original, $scope.item);
    };

    $scope.save = function () {
        Campaign.update({ id: $scope.item.id }, $scope.item, function() {
        	if ($scope.sfdcid) {$location.url('/approveIOs?approved=' + $scope.sfdcid);} 
        	else {$location.path('/campaigns');} 
        });
    };
    
    $scope.save_and_book = function () {
        Campaign.update({ id: $scope.item.id }, $scope.item, function() { $location.path('#/bookedRev/{{campaign.id}}'); });
    };
};
EditCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);



var BookedRevCtrl = function ($scope, $routeParams, $location, Campaign, Booked, Actual) {
    Campaign.get({ id: $routeParams.campaignId }, function (c_item) {
        self.original = c_item;
        $scope.c_item = new Campaign(c_item);
    });	
    
    Booked.get({ campaign_id: $routeParams.campaignId }, function (b_item) {
        self.original = b_item;
        $scope.bookeds = new Campaign(b_item);
    });	
    
};


var DashboardCtrl = function ($scope, $http) {
 	$http.get('/api/bookeddata').success(function(data) {
 		//debugger;
 		$scope.booked = data.res;
 	});
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
 	$http.get('/api/count2011').success(function(data) {
 		$scope.cpadata = data.res;
 	});
 	$http.get('/api/count2012').success(function(data) {
 		$scope.cpadata = data.res;
 	});
 	
 	
/* 	$http.get('/api/count2011').success(function(data) {
 		$scope.jsoncount2011 = data.res;
 	}).then(function() {
 		$scope.count2011 = [];
 		$scope.x = [];
 		$scope.y = []; 
		$.each($scope.jsoncount2011, function(i, obj) {
    		$scope.count2011.push([obj.cp.value, obj.count2011.value]);
    		$scope.x.push([obj.cp.value]);
    		$scope.y.push([obj.count2011.value])
		});
	});
 	$http.get('/api/count2012').success(function(data) {
 		$scope.jsoncount2012 = data.res; 		
 	});
 */	
 	$scope.germanyData = 100;
	$scope.title = 'Revenue';
	$scope.chartData = [$scope.x, $scope.y]; //[['', 'Germany', 'USA', 'Brazil', 'Canada', 'France', 'RU'],	['', $scope.germanyData, 300, 400, 500, 600, 800]];
 	//$scope.data = $scope.count2011; //[[[0, 1], [1, 5], [2, 2]]];
};

var ApproveIOsCtrl = function($scope, $routeParams, $location, $http, $q, Sfdc, Sfdccampaign) {
	var make_query = function() {
        	var q = order_by("start_date", "asc");
            q.filters = [{name: "approved", op: "eq", val: false}];
            if($scope.query) q.filters.push({name: "ioname", op: "ilike", val: "%" + $scope.query + "%"});
        	return angular.toJson(q);
	};
    	
    $scope.search = function () {
        var res = Sfdccampaign.get(
            { page: $scope.page, q: make_query(), results_per_page: 20 },
            function () {
                $scope.no_more = res.page == res.total_pages;
                if (res.page==1) { $scope.sfdc_camps=[]; }
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
    }

    $scope.search = function () {
        var res = Rep.get(
            { page: $scope.page, q: make_query() },
            function () {
                $scope.no_more = res.page == res.total_pages;
                if (res.page==1) { $scope.reps=[]; }
                $scope.reps = $scope.reps.concat(res.objects);
            }
        );
    };

    $scope.show_more = function () { return !$scope.no_more; };
    
    $scope.sort_by = function (ord) {
        if ($scope.sort_order == ord) {$scope.sort_desc = !$scope.sort_desc;}
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

function RepDetailsBaseCtrl($scope, $location, Rep, Product, Channel) {
	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};
	
	$scope.add_rep = function () { }
	
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
