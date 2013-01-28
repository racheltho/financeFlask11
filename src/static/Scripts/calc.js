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
	return d;
};

var calc_booked_rev = function(booked_rev, start, end) {
	var dict = {};
	var months = mths(start,end);
	_.each(months, function(o){ dict[o] = 0; });	
	_.each(booked_rev, function(o){ dict[o.date] = o.bookedRev; });
	return $.map(months, function(o) {
		return {date: o, bookedRev: dict[o]};
	});
};

var active_days = function(st_date, end_date){
	var months = mths(st_date,end_date);
	var n = months.length;	
	var active = {};
	var month_day_array = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
	active[months[0]] = month_day_array[st_date.getMonth()] - st_date.getUTCDate() + 1;  // days in start month
	//debugger;
	if(n > 1){
		active[months[n-1]] = end_date.getDay() + 1;  // days in end month
	}
	if(n > 2){
		for(var i=1; i<n-1; i++){ active[months[i]] = month_day_array[months[i].getMonth()]; }
	}
	return active;
};

var calc_sl = function(st_date, end_date, budget, booked_rev) {
	var months = mths(st_date,end_date);
	var active = active_days(st_date,end_date);
	var total_days = _.reduce(active, function(memo, num){ return memo + num; }, 0);
	var curr_booked = calc_booked_rev(booked_rev, st_date, end_date); 
	$.each(months, function(i,o){ curr_booked[i].bookedRev = Math.round(active[o]*budget/total_days*100)/100; });
	return curr_booked;
};

var date_array = function(arr) {
	return $.map(arr, function(o) {	return new Date(o);	});
};