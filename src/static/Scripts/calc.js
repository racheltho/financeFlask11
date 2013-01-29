"use strict";

var mths = function(start, end){
	var d = [];
	var start1 = new Date(start);
	start1.setDate(1);
	var end1 = new Date(end);
	end1.setDate(1);
	var temp_date = new Date(start1);
	while(temp_date <= end1){
		d.push(new Date(temp_date));
		temp_date.setMonth(temp_date.getMonth() + 1);
	}
	//_.each(d, function(m){ m.setHours(0); m.setMinutes(0); m.setSeconds(0); m.setMilliseconds(0); });
	return d;
};

var calc_booked_rev = function(start, end, booked_rev) {
	var dict = {};
	var answer = [];
	var months = mths(start,end);
	
	//_.each(booked_rev, function(m){ m.date.setHours(0); m.date.setMinutes(0); m.date.setSeconds(0); m.date.setMilliseconds(0); });
	//_.each(months, function(m){ m.setHours(0); m.setMinutes(0); m.setSeconds(0); m.setMilliseconds(0); });
	_.each(months, function(o){ dict[o] = 0; });
	_.each(booked_rev, function(o){ dict[o.date] = Math.round(o.bookedRev*100)/100; });
	$.each(dict, function(index, value) {
		answer.push({date: new Date(index), bookedRev: value});
	});
	answer.sort(function(c, d) {
    	var a = c.date;
    	var b = d.date;
	    return a < b ? -1 : (a > b ? 1 : 0);
	});
	return answer;
};

var active_days = function(st_date, end_date){
	var months = mths(st_date,end_date);
	var n = months.length;	
	var active = {};
	var month_day_array = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
	active[months[0]] = month_day_array[st_date.getMonth()] - st_date.getUTCDate() + 1;  // days in start month
	if(n > 1){
		active[months[n-1]] = end_date.getUTCDate();  // days in end month
	}
	if(n > 2){
		for(var i=1; i<n-1; i++){ active[months[i]] = month_day_array[months[i].getMonth()]; }
	}
	return active;
};

var calc_sl = function(st_date, end_date, booked_rev, budget) {
	var months = mths(st_date,end_date);
	var active = active_days(st_date,end_date);
	var total_days = _.reduce(active, function(memo, num){ return memo + num; }, 0);
	var curr_booked = calc_booked_rev(st_date, end_date, booked_rev);
	var dict = {};
	var answer = [];
	// convert curr_booked into dictionary dict
	_.each(curr_booked, function(o){ dict[o.date] = o.bookedRev; });
	// use months to update the appropriate fields of dict 
	$.each(months, function(i,o){ dict[o] = Math.round(active[o]*budget/total_days*100)/100; });
	// convert dict back into an array of objects to be returned
	$.each(dict, function(index, value) {
		answer.push({date: new Date(index), bookedRev: value});
	});
	answer.sort(function(c, d) {
    	var a = c.date;
    	var b = d.date;
	    return a < b ? -1 : (a > b ? 1 : 0);
	});
	return answer;
};

var date_array = function(arr) {
	return $.map(arr, function(o) {	return new Date(o);	});
};

var parseDate = function(input) {
  var parts = input.match(/(\d+)/g);
  // new Date(year, month [, date [, hours[, minutes[, seconds[, ms]]]]])
  return new Date(parts[0], parts[1]-1, parts[2]); // months are 0-based
};

var sameDates = function(date1, date2){
	return ((date1.getFullYear()==date2.getFullYear())&&(date1.getMonth()==date2.getMonth())&&(date1.getDate()==date2.getDate()));
}

