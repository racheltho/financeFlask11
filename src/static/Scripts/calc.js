"use strict";

// Return an array of each month from start to end, containing the 1st of that month
var mths = function(start, end) {
	if(!start || !end){ return [];}
	var d = [];
	var start1 = new Date(start);
	start1.setDate(1);
	var end1 = new Date(end);
	end1.setDate(1);
	var temp_date = new Date(start1);
	while (temp_date <= end1) {
		d.push(new Date(temp_date));
		temp_date.setMonth(temp_date.getMonth() + 1);
	}
	//_.each(d, function(m){ m.setHours(0); m.setMinutes(0); m.setSeconds(0); m.setMilliseconds(0); });
	return d;
};

var calc_rev = function(start, end, rev, booked_or_actual) {
	var dict = {};
	var answer = [];
	var months = mths(start, end);
	var temp = {};

	//_.each(booked_rev, function(m){ m.date.setHours(0); m.date.setMinutes(0); m.date.setSeconds(0); m.date.setMilliseconds(0); });
	//_.each(months, function(m){ m.setHours(0); m.setMinutes(0); m.setSeconds(0); m.setMilliseconds(0); });
	_.each(months, function(o) {
		dict[o] = 0;
	});
	_.each(rev, function(o) {
		dict[o.date] = Math.round(o[booked_or_actual] * 100) / 100;
	});
	$.each(dict, function(index, value) {
		temp = {};
		temp.date = new Date(index);
		temp[booked_or_actual] = value;
		answer.push(temp);
	});
	answer.sort(function(c, d) {
		var a = c.date;
		var b = d.date;
		return a < b ? -1 : (a > b ? 1 : 0);
	});
	return answer;
};

var active_days = function(st_date, end_date) {
	var months = mths(st_date, end_date);
	var n = months.length;
	var active = {};
	var month_day_array = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
	active[months[0]] = month_day_array[st_date.getMonth()] - st_date.getDate() + 1;
	// days in start month
	if (n > 1) {
		active[months[n - 1]] = end_date.getDate();
		// days in end month
	}
	if (n > 2) {
		for (var i = 1; i < n - 1; i++) {
			active[months[i]] = month_day_array[months[i].getMonth()];
		}
	}
	return active;
};

var calc_sl = function(st_date, end_date, rev, booked_or_actual, budget) {
	// booked_rev is array of objects
	// curr_booked is array of objects
	// months is an array
	var months = mths(st_date, end_date);
	var active = active_days(st_date, end_date);
	var total_days = _.reduce(active, function(memo, num) {
		return memo + num;
	}, 0);
	var curr_rev = calc_rev(st_date, end_date, rev, booked_or_actual);
	var dict = {};
	var answer = [];
	// convert curr_booked into dictionary dict
	_.each(curr_rev, function(o) {
		dict[o.date] = o[booked_or_actual];
	});
	// use months to update the appropriate fields of dict
	$.each(months, function(i, o) {
		dict[o] = Math.round(active[o] * budget / total_days * 100) / 100;
	});
	// convert dict back into an array of objects to be returned
	var temp = {};
	$.each(dict, function(index, value) {
		temp = {};
		temp.date = new Date(index);
		temp[booked_or_actual] = value;
		answer.push(temp);
	});
	answer.sort(function(c, d) {
		var a = c.date;
		var b = d.date;
		return a < b ? -1 : (a > b ? 1 : 0);
	});
	return answer;
};

var date_array = function(arr) {
	return $.map(arr, function(o) {
//		return new Date(o + ' 00:00:00 UTC');
		return new Date(o);
	});
};

// convert string containing a yyyy-mm-dd to a local date
var stringToDate = function(input) {
	if(!input){ return input; }
	var parts = input.match(/(\d+)/g);
	// new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
//	return new Date(Date.UTC(parts[0], parts[1] - 1, parts[2], 0, 0, 0));
	return new Date(parts[0], parts[1] - 1, parts[2], 0, 0, 0);
	// months are 0-based
};

var sameDates = function(date1, date2) {
	return ((date1.getFullYear() == date2.getFullYear()) && (date1.getMonth() == date2.getMonth()) && (date1.getDate() == date2.getDate()));
}

/*
var spanamt = function(index, dataset, ) {
 	counter = 1;
 	n = $scope.agency_data.length;
 	while($scope.agency_data[index][1]=== $scope.count_agency[index+1][1] && index < n){
 			index += 1;
 			counter += 1;
 		}
 		return counter;

*/