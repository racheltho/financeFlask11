"use strict";


test( "hello test", function() {
  ok( 1 == "1", "Passed!" );
});


test("mths() should not change input params", function() {
	var st = new Date('01-05-2011');
	mths(st, new Date('01-07-2012'));
	deepEqual(st, new Date('01-05-2011'));
});

test( "mths test", function() {
	var monthsStart = new Date('09-13-2010');
	var monthsEnd = new Date('02-05-2011');
	var actMonths = mths(monthsStart, monthsEnd);
	var exp = date_array(['09-01-2010', '10-01-2010','11-01-2010','12-01-2010','01-01-2011','02-01-2011']);
	deepEqual(actMonths, exp, "Passed");
});

test("calc_booked_rev test", function(){
	var campStDate = new Date('01-15-2012');
	var campEndDate = new Date('04-15-2012');
	var currBooked = [{date: new Date('01-01-2012'), bookedRev: 432}, {date: new Date('02-01-2012'), bookedRev: 42}];
	var actStart = calc_booked_rev(currBooked, campStDate, campEndDate);	
	var exp = [{date: new Date('01-01-2012'), bookedRev: 432}, {date: new Date('02-01-2012'), bookedRev: 42}, {date: new Date('03-01-2012'), bookedRev: 0}, {date: new Date('04-01-2012'), bookedRev: 0}];
	deepEqual(actStart, exp, "Passed");
});

test("calc_booked_rev with empty currBooked test", function(){
	var campStDate = new Date('01-15-2012');
	var campEndDate = new Date('04-15-2012');
	var currBooked = [];
	var actStart = calc_booked_rev(currBooked, campStDate, campEndDate);	
	var exp = [{date: new Date('01-01-2012'), bookedRev: 0}, {date: new Date('02-01-2012'), bookedRev: 0}, {date: new Date('03-01-2012'), bookedRev: 0}, {date: new Date('04-01-2012'), bookedRev: 0}];
	deepEqual(actStart, exp, "Passed");
});

test("active_days test", function(){
	var campStDate = new Date('01-10-2012');
	var campEndDate = new Date('04-05-2012');
	var expdt = [new Date("01-01-2012"), new Date("02-01-2012"), new Date("03-01-2012"), new Date("04-01-2012")];
	var expdays = [22, 28, 31, 5];
	var exp = {};
	_.each(expdt, function(o,i) {exp[o] = expdays[i];});
	var active = active_days(campStDate, campEndDate);
	deepEqual(active, exp, "Passed");
});

test("calc_sl test", function(){
	var campStDate = new Date('01-10-2012');
	var campEndDate = new Date('04-05-2012');
	var budget = 25000;
	var act_sl = calc_sl(campStDate, campEndDate, budget);	
	// NB: Calcs come from ...xls
	var exp = [{date: new Date('01-01-2012'), bookedRev: 6395.35}, {date: new Date('02-01-2012'), bookedRev: 8139.53}, {date: new Date('03-01-2012'), bookedRev: 9011.63}, 
				{date: new Date('04-01-2012'), bookedRev: 1453.49}];
	deepEqual(act_sl, exp, "Passed");
});

//print(actStart);
/* => 
	[{Date: '2012-01-01', bookedRev: 432}, {Date: '2012-02-01', bookedRev: 42}, {Date: '2012-03-01', bookedRev: 0}, {Date: '2012-04-01', bookedRev: 0}]

var enteredStDate = new Date('02-10-2012');
var enteredEndDate = new Date('03-25-2012');
var revenue = 2200;
var actAfter = calc_sl_bookedRev(actStart, enteredStDate, enteredEndDate, revenue);
*/
//print(actAfter);

/* =>
	[{Date: '2012-01-01', bookedRev: 0}, {Date: '2012-02-01', bookedRev: 920.93}, {Date: '2012-03-01', bookedRev: 1279.07}, {Date: '2012-04-01', bookedRev: 0}];
*/