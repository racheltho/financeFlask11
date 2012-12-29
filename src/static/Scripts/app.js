var CampaignApp = angular.module("CampaignApp", ["ngResource"]).
     config(function ($routeProvider) {
         $routeProvider.
           when('/', { controller: ListCtrl, templateUrl: 'list.html' }).
           //when('/edit/:todoId', { controller: EditCtrl, templateUrl: 'detail.html' }).
           //when('/new', { controller: CreateCtrl, templateUrl: 'detail.html' }).
           otherwise({ redirectTo: '/' });
     });

CampaignApp.factory('Campaign', function ($resource) {
    return $resource('/api/campaign/:id', { id: '@id' }, { update: { method: 'PUT' } });
});

var ListCtrl = function ($scope, $location, Campaign) {
    var make_query = function() {
        var q = {};
        //var q = {order_by: [{field: $scope.sort_order, direction: $scope.sort_desc ? "desc": "asc"}]};
        if ($scope.query) {
            q.filters = [{name: "campaign", op: "like", val: "%" + $scope.query + "%"} ];
        }
        return angular.toJson(q);
    }

	$scope.search = function() {
		var res = Campaign.get({q: make_query()}, function () {
			$scope.campaigns = res.objects;
		})
	};

    /*$scope.search = function () {
        var res = Campaign.get(
            { page: $scope.page, q: make_query() },
            function () {
                $scope.no_more = res.page == res.total_pages;
                if (res.page==1) { $scope.todos=[]; }
                $scope.todos = $scope.todos.concat(res.objects);
            }
        );
    };*/

    /*$scope.show_more = function () { return !$scope.no_more; };
    
    $scope.sort_by = function (ord) {
        if ($scope.sort_order == ord) {$scope.sort_desc = !$scope.sort_desc;}
        else { $scope.sort_desc = false; }
        $scope.sort_order = ord;
        $scope.reset();
    };

    $scope.del = function (id) {
        Todo.remove({ id: id }, function () {
            $('#item_'+id).fadeOut();
        });
    };

    $scope.reset = function() {
        $scope.page = 1;
        $scope.search();
    };

    $scope.sort_order = 'priority';
    $scope.sort_desc = false;
    $scope.reset();*/

	$scope.reset = function() {
        $scope.search();
    };
    
    $scope.reset();
   
};

/*var CreateCtrl = function ($scope, $location, Todo) {
    $scope.btn_text = 'Add';
    
    $scope.save = function () {
        Todo.save($scope.item, function() { $location.path('/'); });
    };
};

var EditCtrl = function ($scope, $routeParams, $location, Todo) {
    var self = this;
    $scope.btn_text = 'Update';

    Todo.get({ id: $routeParams.todoId }, function (item) {
        self.original = item;
        $scope.item = new Todo(item);
    });

    $scope.isClean = function () {
        return angular.equals(self.original, $scope.item);
    };

    $scope.save = function () {
        Todo.update({ id: $scope.item.id }, $scope.item, function() { $location.path('/'); });
    };
};*/
