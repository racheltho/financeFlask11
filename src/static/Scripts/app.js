var CampaignApp = angular.module("CampaignApp", ["ngResource", "ui"]).
     config(function ($routeProvider) {
         $routeProvider.
           when('/', { controller: ListCtrl, templateUrl: 'list.html' }).
           when('/edit/:campaignId', { controller: EditCtrl, templateUrl: 'detail.html' }).
           when('/new', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           when('/dashboard', { controller: DashboardCtrl, templateUrl: 'dashboard.html' }).
           when('/approveIOs', { controller: ApproveIOsCtrl, templateUrl: 'approveIOs.html' }).
           when('/newIOs', { controller: NewIOsCtrl, templateUrl: 'newIOs.html' }).
           when('/bookedRev/:campaignId', { controller: BookedRevCtrl, templateUrl: 'bookedRev.html' }).
           otherwise({ redirectTo: '/' });
     });

$.each(['Campaign', 'Advertiser', 'Product', 'Rep', 'Booked', 'Actual', 'Sfdc'], 
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
            //q.filters = [{name: "upper(campaign)", op: "like", val: "%" + $scope.query.toUpperCase() + "%"} ];
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
	
	$scope.add_rep = function () { }
	
	get_sel_list(Rep, 'last_name', "select_reps");
	//get_sel_list(Advertiser, 'advertiser', "select_advertisers");
	get_sel_list(Product, 'product', "select_products");
}; 

var CreateCtrl = function ($scope, $location, Campaign, Rep, Advertiser, Product, $injector) { 
	$injector.invoke(DetailsBaseCtrl, this, {$scope: $scope});

    $scope.btn_text = 'Add';

	$scope.save_and_book = function () {
        Campaign.save($scope.item, function() { $location.path('#/bookedRev/{{campaign.id}}'); });
    };

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


var DashboardCtrl = function ($scope, $routeParams, $location, $timeout, $log) {
	$scope.germanyData = 100;
	$scope.title = 'Revenue';
	var timeoutId;
	$scope.chartData = [['', 'Germany', 'USA', 'Brazil', 'Canada', 'France', 'RU'],	['', $scope.germanyData, 300, 400, 500, 600, 800]];
 	$scope.data = [[[0, 1], [1, 5], [2, 2]]];
};

var ApproveIOsCtrl = function($scope, $routeParams, $location, Campaign, Sfdc, Sfdcex) {
		
	Sfdc.get(function(items){
		$scope.Sfdcs = items.objects;
	//	function () {
    //            $scope.no_more = res.page == res.total_pages;
    //            if (res.page==1) { $scope.campaigns=[]; }
    //            $scope.Sfdcs = $scope.Sfdcs.concat(res.objects);
    //        }
	});
	
	$scope.approve = function (id) {
        Campaign.update({ id: id }, function () {
            $('#item_'+id).fadeOut();
        });
    };

	$scope.show_more = function () { return !$scope.no_more; };

    $scope.reset = function() {
        $scope.page = 1;
        $scope.list();
    };
 
    //$scope.reset();

}; 

var NewIOsCtrl = function($scope, $routeParams, $location, Campaign, Sfdc) {
		
	Sfdc.get(function(items){
		$scope.Sfdcs = items.objects;
	});
	
  
    $scope.save = function () {
        Campaign.save($scope.item, function() { $location.path('/'); });
    };

}; 

