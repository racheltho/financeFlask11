"use strict";

test("mths() should not change input params", function() {
	var st = new Date('01-05-2011');
	mths(st, new Date('01-07-2012'));
	deepEqual(st, new Date('01-05-2011'));
});

test("mths test", function() {
	var monthsStart = new Date('09-13-2010');
	var monthsEnd = new Date('02-05-2011');
	var actMonths = mths(monthsStart, monthsEnd);
	var exp = date_array(['09-01-2010', '10-01-2010', '11-01-2010', '12-01-2010', '01-01-2011', '02-01-2011']);
	deepEqual(actMonths, exp, "Passed");
});

test("calc_booked_rev test", function() {
	var campStDate = new Date('01-15-2012');
	var campEndDate = new Date('04-15-2012');
	var currBooked = [{
		date : new Date('01-01-2012'),
		bookedRev : 432
	}, {
		date : new Date('02-01-2012'),
		bookedRev : 42
	}];
	var actStart = calc_booked_rev(campStDate, campEndDate, currBooked);
	var exp = [{
		date : new Date('01-01-2012'),
		bookedRev : 432
	}, {
		date : new Date('02-01-2012'),
		bookedRev : 42
	}, {
		date : new Date('03-01-2012'),
		bookedRev : 0
	}, {
		date : new Date('04-01-2012'),
		bookedRev : 0
	}];
	deepEqual(actStart, exp, "Passed");
});

test("calc_booked_rev with empty currBooked test", function() {
	var campStDate = new Date('01-15-2012');
	var campEndDate = new Date('04-15-2012');
	var currBooked = [];
	var actStart = calc_booked_rev(campStDate, campEndDate, currBooked);
	var exp = [{
		date : new Date('01-01-2012'),
		bookedRev : 0
	}, {
		date : new Date('02-01-2012'),
		bookedRev : 0
	}, {
		date : new Date('03-01-2012'),
		bookedRev : 0
	}, {
		date : new Date('04-01-2012'),
		bookedRev : 0
	}];
	deepEqual(actStart, exp, "Passed");
});

test("active_days test", function() {
	var campStDate = new Date('01-10-2012');
	var campEndDate = new Date('04-05-2012');
	var expdt = [new Date("01-01-2012"), new Date("02-01-2012"), new Date("03-01-2012"), new Date("04-01-2012")];
	var expdays = [22, 28, 31, 5];
	var exp = {};
	_.each(expdt, function(o, i) {
		exp[o] = expdays[i];
	});
	var active = active_days(campStDate, campEndDate);
	deepEqual(active, exp, "Passed");
});

test("active_days test 2", function() {
	var campStDate = new Date('02-18-2011');
	var campEndDate = new Date('03-11-2011');
	var expdt = [new Date("02-01-2011"), new Date("03-01-2011")];
	var expdays = [11, 11];
	var exp = {};
	_.each(expdt, function(o, i) {
		exp[o] = expdays[i];
	});
	var active = active_days(campStDate, campEndDate);
	deepEqual(active, exp, "Passed");
});

test("calc_sl test", function() {
	var campStDate = new Date('01-10-2012');
	var campEndDate = new Date('04-05-2012');
	var currBooked = [{
		date : new Date('01-01-2012'),
		bookedRev : 4320
	}, {
		date : new Date('02-01-2012'),
		bookedRev : 42
	}];
	var budget = 25000;
	var act_sl = calc_sl(campStDate, campEndDate, currBooked, budget);
	// NB: Calcs come from ...xls
	var exp = [{
		date : new Date('01-01-2012'),
		bookedRev : 6395.35
	}, {
		date : new Date('02-01-2012'),
		bookedRev : 8139.53
	}, {
		date : new Date('03-01-2012'),
		bookedRev : 9011.63
	}, {
		date : new Date('04-01-2012'),
		bookedRev : 1453.49
	}];
	deepEqual(act_sl, exp, "Passed");
});

test("calc_booked test 2", function() {
	var campStDate = new Date('02-17-2011');
	var campEndDate = new Date('03-11-2011');
	var currBooked = [{
		date : new Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : new Date('02-01-2011'),
		bookedRev : 42
	}];
	var act = calc_booked_rev(campStDate, campEndDate, currBooked);
	var exp = [{
		date : new Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : new Date('02-01-2011'),
		bookedRev : 42
	}, {
		date : new Date('03-01-2011'),
		bookedRev : 0
	}];
	deepEqual(act, exp, "Passed");
});

test("calc_sl test 2", function() {
	var campStDate = new Date('02-18-2011');
	var campEndDate = new Date('03-11-2011');
	var currBooked = [{
		date : new Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : new Date('02-01-2011'),
		bookedRev : 42
	}];
	var budget = 2200;
	var act_sl = calc_sl(campStDate, campEndDate, currBooked, budget);
	// NB: Calcs come from ...xls
	var exp = [{
		date : new Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : new Date('02-01-2011'),
		bookedRev : 1100
	}, {
		date : new Date('03-01-2011'),
		bookedRev : 1100
	}];
	deepEqual(act_sl, exp, "Passed");
});

test("parseDate test", function() {
	var strDate = "2011-10-15";
	var parsedDate = parseDate(strDate);
	var exp = new Date('10-15-2011');
	deepEqual(parsedDate, exp, "Passed");
});

test("sameDates test", function() {
	var date1 = new Date(2012, 4, 13, 10, 25, 6, 9);
	var date2 = new Date(2012, 4, 13, 0, 0, 0, 0);
	var date3 = new Date(2012, 3, 13, 0, 0, 0, 0);
	var date4 = new Date(2012, 4, 13);
	var arr = [];
	arr[0] = sameDates(date1, date2);
	arr[1] = sameDates(date2, date3);
	arr[2] = sameDates(date1, date4);
	var expArr = [true, false, true];
	deepEqual(arr, expArr, "Passed");
});

