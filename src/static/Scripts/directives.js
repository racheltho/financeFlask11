"use strict";
/*global CampaignApp, google */

CampaignApp.directive('icon', function () {
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
                return (asc !== $scope.sort_desc) && ($scope.sort_order === $scope.sort);
            };
        }
    };
})/*
.directive('chart', function() {
        return {
          restrict: 'A',
          link: function($scope, $elm, $attr) {
            // Create the data table.
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'FY 2012');
            data.addColumn('number', 'Revenue');
            data.addRows([
              ['Q1', 17028],
              ['Q2', 21443],
              ['Q3', 23149],
              ['Q4', 34000],
            ]);

            // Set chart options
            var options = {'title':'Revenue 2012',
                           'width':400,
                           'height':300,
                           };

            // Instantiate and draw our chart, passing in some options.
            var chart = new google.visualization.BarChart($elm[0]);
            chart.draw(data, options);
          }
      }
})*/
.directive('columnChart', function() {
	return function(scope, element, attrs) {
		
		var chart = new google.visualization.ColumnChart(element[0]);
		scope.$watch(attrs.columnChart, function(value) {
			if (!value) {return;}
			var data = google.visualization.arrayToDataTable(value);
			var options = {
					  title: attrs.chartTitle,
					  titleTextStyle: {color: 'black', fontSize: '18'},
					  hAxis: {title: attrs.chartHaxisTitle, titleTextStyle: {color: 'black', fontSize: '14'}},
					  colors: ['#178cb7','666666']
			};
			chart.draw(data, options);
		});
	};
})
.directive('chart', function() {
    return {
        restrict: 'E',
        link: function(scope, elem, attrs) {
            var data = scope[attrs.ngModel];
            $.plot(elem, data, {});
            elem.show();
        }
    };
});
