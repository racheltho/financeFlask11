"use strict";

//var date_suf = ' 00:00:00 UTC';
var date_suf = '';
var test_UTC_Date = function(d) {
	return new Date(d + date_suf);
};

test("mths() should not change input params", function() {
	var st = stringToDate('2011-05-01');
	mths(st, test_UTC_Date('01-07-2012'));
	deepEqual(st, stringToDate('2011-05-01'));
});

test("mths test", function() {
	var monthsStart = test_UTC_Date('09-13-2010');
	var monthsEnd = test_UTC_Date('02-05-2011');
	var actMonths = mths(monthsStart, monthsEnd);
	var exp = date_array(['09-01-2010', '10-01-2010', '11-01-2010', '12-01-2010', '01-01-2011', '02-01-2011']);
	deepEqual(actMonths, exp, "Passed");
});

test("mths null test", function(){
	deepEqual(mths(null, null), []);
	deepEqual(mths(null, test_UTC_Date('05-25-2012')), []);
	deepEqual(mths(test_UTC_Date('06-12-1983'), null),[]);
});

test("calc_rev test (booked)", function() {
	var campStDate = test_UTC_Date('01-15-2012');
	var campEndDate = test_UTC_Date('04-15-2012');
	var currBooked = [{
		date : test_UTC_Date('01-01-2012'),
		bookedRev : 432
	}, {
		date : test_UTC_Date('02-01-2012'),
		bookedRev : 42
	}];
	var actStart = calc_rev(campStDate, campEndDate, currBooked, "bookedRev");
	var exp = [{
		date : test_UTC_Date('01-01-2012'),
		bookedRev : 432
	}, {
		date : test_UTC_Date('02-01-2012'),
		bookedRev : 42
	}, {
		date : test_UTC_Date('03-01-2012'),
		bookedRev : 0
	}, {
		date : test_UTC_Date('04-01-2012'),
		bookedRev : 0
	}];
	deepEqual(actStart, exp, "Passed");
});

test("calc_rev test (actual)", function() {
	var campStDate = test_UTC_Date('01-15-2012');
	var campEndDate = test_UTC_Date('04-15-2012');
	var currActual = [{
		date : test_UTC_Date('01-01-2012'),
		actualRev : 432
	}, {
		date : test_UTC_Date('02-01-2012'),
		actualRev : 42
	}];
	var actStart = calc_rev(campStDate, campEndDate, currActual, "actualRev");
	var exp = [{
		date : test_UTC_Date('01-01-2012'),
		actualRev : 432
	}, {
		date : test_UTC_Date('02-01-2012'),
		actualRev : 42
	}, {
		date : test_UTC_Date('03-01-2012'),
		actualRev : 0
	}, {
		date : test_UTC_Date('04-01-2012'),
		actualRev : 0
	}];
	deepEqual(actStart, exp, "Passed");
});

test("calc_rev with empty currBooked test", function() {
	var campStDate = test_UTC_Date('01-15-2012');
	var campEndDate = test_UTC_Date('04-15-2012');
	var currBooked = [];
	var actStart = calc_rev(campStDate, campEndDate, currBooked, "bookedRev");
	var exp = [{
		date : test_UTC_Date('01-01-2012'),
		bookedRev : 0
	}, {
		date : test_UTC_Date('02-01-2012'),
		bookedRev : 0
	}, {
		date : test_UTC_Date('03-01-2012'),
		bookedRev : 0
	}, {
		date : test_UTC_Date('04-01-2012'),
		bookedRev : 0
	}];
	deepEqual(actStart, exp, "Passed");
});

test("active_days test", function() {
	var campStDate = test_UTC_Date('01-10-2012');
	var campEndDate = test_UTC_Date('04-05-2012');
	var expdt = [test_UTC_Date("01-01-2012"), test_UTC_Date("02-01-2012"), test_UTC_Date("03-01-2012"), test_UTC_Date("04-01-2012")];
	var expdays = [22, 28, 31, 5];
	var exp = {};
	_.each(expdt, function(o, i) {
		exp[o] = expdays[i];
	});
	var active = active_days(campStDate, campEndDate);
	deepEqual(active, exp, "Passed");
});

test("active_days test 2", function() {
	var campStDate = test_UTC_Date('02-18-2011');
	var campEndDate = test_UTC_Date('03-11-2011');
	var expdt = [test_UTC_Date("02-01-2011"), test_UTC_Date("03-01-2011")];
	var expdays = [11, 11];
	var exp = {};
	_.each(expdt, function(o, i) {
		exp[o] = expdays[i];
	});
	var active = active_days(campStDate, campEndDate);
	deepEqual(active, exp, "Passed");
});

test("calc_sl test", function() {
	var campStDate = test_UTC_Date('01-10-2012');
	var campEndDate = test_UTC_Date('04-05-2012');
	var currBooked = [{
		date : test_UTC_Date('01-01-2012'),
		bookedRev : 4320
	}, {
		date : test_UTC_Date('02-01-2012'),
		bookedRev : 42
	}];
	var budget = 25000;
	var act_sl = calc_sl(campStDate, campEndDate, currBooked, "bookedRev", budget);
	// NB: Calcs come from ...xls
	var exp = [{
		date : test_UTC_Date('01-01-2012'),
		bookedRev : 6395.35
	}, {
		date : test_UTC_Date('02-01-2012'),
		bookedRev : 8139.53
	}, {
		date : test_UTC_Date('03-01-2012'),
		bookedRev : 9011.63
	}, {
		date : test_UTC_Date('04-01-2012'),
		bookedRev : 1453.49
	}];
	deepEqual(act_sl, exp, "Passed");
});

test("calc_booked test 2", function() {
	var campStDate = test_UTC_Date('02-17-2011');
	var campEndDate = test_UTC_Date('03-11-2011');
	var currBooked = [{
		date : test_UTC_Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : test_UTC_Date('02-01-2011'),
		bookedRev : 42
	}];
	var act = calc_rev(campStDate, campEndDate, currBooked, "bookedRev");
	var exp = [{
		date : test_UTC_Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : test_UTC_Date('02-01-2011'),
		bookedRev : 42
	}, {
		date : test_UTC_Date('03-01-2011'),
		bookedRev : 0
	}];
	deepEqual(act, exp, "Passed");
});

test("calc_sl test 2", function() {
	var campStDate = test_UTC_Date('02-18-2011');
	var campEndDate = test_UTC_Date('03-11-2011');
	var currBooked = [{
		date : test_UTC_Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : test_UTC_Date('02-01-2011'),
		bookedRev : 42
	}];
	var budget = 2200;
	var act_sl = calc_sl(campStDate, campEndDate, currBooked, "bookedRev", budget);
	// NB: Calcs come from ...xls
	var exp = [{
		date : test_UTC_Date('01-01-2011'),
		bookedRev : 4320
	}, {
		date : test_UTC_Date('02-01-2011'),
		bookedRev : 1100
	}, {
		date : test_UTC_Date('03-01-2011'),
		bookedRev : 1100
	}];
	deepEqual(act_sl, exp, "Passed");
});

test("calc_sl test 3", function() {
	var strStDate = "2013-05-01";
	var campStDate = stringToDate(strStDate);
	var strEndDate = "2013-06-01";
	var campEndDate = stringToDate(strEndDate);
	var currBooked = [];
	var budget = 16750;
	var act_sl = calc_sl(campStDate, campEndDate, currBooked, "bookedRev", budget);
	var exp = [{
		date : stringToDate('2013-05-01'),
		bookedRev : 16226.56	// (31/32 * 16750)
	}, {
		date : stringToDate('2013-06-01'),
		bookedRev : 523.44	// (1/32 * 16750)
	}];
	deepEqual(act_sl, exp, "Passed");
});


test("stringToDate test", function() {
	var strDate = "2011-10-15";
	var parsedDate = stringToDate(strDate);
	var exp = test_UTC_Date('10-15-2011');
	deepEqual(parsedDate, exp, "Passed");
});

test("stringToDate handles Null", function(){
	var dummy;
	var res = stringToDate(dummy);
	ok(!res);
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
