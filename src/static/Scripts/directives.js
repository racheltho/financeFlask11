CampaignApp.directive('jqDatepicker', function ($parse) {
    return function(scope, element, attrs) {
        var ngModel = $parse(attrs.ngModel);
        $(function() {
            element.datepicker({
                showOn: "both",
                changeYear: true,
                changeMonth: true,
                dateFormat: 'yy-mm-dd',
                maxDate: '+10y',
                yearRange: '2000:2020',
                onSelect: function(dateText) {
                    scope.$apply(function(s) { ngModel.assign(s, dateText); });
                }
            });
        });
    };

}).directive('icon', function () {
    return {
        restrict: 'E', replace: true, scope:true,
        template: '<i class="icon-{{val}}"></i>',
        controller: function ($scope, $element, $attrs) {
            $scope.val = $attrs.name;
        }
    };

})
.directive('sorted', function () {
    return {
        scope: true, transclude: true,
        template: '<a ng-click="do_sort()" ng-transclude></a>' +
        '<span ng-show="do_show(true)"><icon name="circle-arrow-down" /></span>' +
        '<span ng-show="do_show(false)"><icon name="circle-arrow-up" /></span>',

        controller: function ($scope, $element, $attrs) {
            $scope.sort = $attrs.sorted;

            $scope.do_sort = function() { $scope.sort_by($scope.sort); };

            $scope.do_show = function(asc) {
                return (asc != $scope.sort_desc) && ($scope.sort_order == $scope.sort);
            };
        }
    };
});
