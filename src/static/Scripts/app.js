var CampaignApp = angular.module("CampaignApp", ["ngResource", "ui"]).
     config(function ($routeProvider) {
         $routeProvider.
           when('/', { controller: ListCtrl, templateUrl: 'list.html' }).
           when('/edit/:campaignId', { controller: EditCtrl, templateUrl: 'detail.html' }).
           when('/new', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/revenue', { controller: RevenueCtrl, templateUrl: 'revenue.html' }).
           when('/dashboard', { controller: DashboardCtrl, templateUrl: 'dashboard.html' }).
           when('/approveIOs', { controller: ApproveIOsCtrl, templateUrl: 'approveIOs.html' }).
           otherwise({ redirectTo: '/' });
     });

$.each(['Campaign', 'Advertiser', 'Product', 'Rep', 'Booked', 'Actual'], 
	function(i, s) {
		CampaignApp.factory(s, function ($resource) {
		    return $resource('/api/' + s.toLowerCase() + '/:id', 
		    { id: '@id' }, { update: { method: 'PUT' } });
		});	
	});

var order_by = function(order, dir) {
	return {order_by: [{field: order, direction: dir}]};
};

var ListCtrl = function ($scope, $location, Campaign) {
    var make_query = function() {
        var q = order_by($scope.sort_order, $scope.sort_desc ? "desc": "asc");
        if ($scope.query) {
            q.filters = [{name: "campaign", op: "like", val: "%" + $scope.query + "%"} ];
        }
        return angular.toJson(q);
    }

    $scope.search = function () {
        var res = Campaign.get(
            { page: $scope.page, q: make_query() },
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

function DetailsBaseCtrl($scope, $location, Campaign, Rep, Advertiser, Product) {
	var get_sel_list = function(model, field, ngmodel_fld) {
		var q = order_by(field, "asc");
		model.get({q: angular.toJson(q)}, function(items) {
			$scope[ngmodel_fld] = items.objects;
	 	});
	};
	
	get_sel_list(Rep, 'last_name', "select_reps");
	get_sel_list(Advertiser, 'advertiser', "select_advertisers");
	get_sel_list(Product, 'product', "select_products");
}; 

var CreateCtrl = function ($scope, $location, Campaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Add';

    $scope.save = function () {
        Campaign.save($scope.item, function() { $location.path('/'); });
    };
};
CreateCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);

var EditCtrl = function ($scope, $location, $routeParams, Campaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    var self = this;
    $scope.btn_text = 'Update';

    Campaign.get({ id: $routeParams.campaignId }, function (item) {
        self.original = item;
        $scope.item = new Campaign(item);
    });

    $scope.isClean = function () {
        return angular.equals(self.original, $scope.item);
    };

    $scope.save = function () {
        Campaign.update({ id: $scope.item.id }, $scope.item, function() { $location.path('/'); });
    };
};
EditCtrl.prototype = Object.create(DetailsBaseCtrl.prototype);

var RevenueCtrl = function ($scope, $routeParams, $location, Campaign, Booked, Actual) {
};

var DashboardCtrl = function ($scope, $routeParams, $location) {
};


var ApproveIOsCtrl = function($scope, $routeParams, $location, Campaign) {
	var make_query = function() {
		var q = {};
		//var q = {order_by: [{field: $scope.sort_order, direction: $scope.sort_desc ? "desc": "asc"}]};
		if ($scope.query) {
			q.filters = [{
				name : "campaign",
				op : "like",
				val : "%" + $scope.query + "%"
			}];
		}
		return angular.toJson(q);
	}
	$scope.search = function() {
		var res = Campaign.get({
			q : make_query()
		}, function() {
			$scope.new_campaigns = res.objects;
		})
	};
	$scope.search();
}; 



