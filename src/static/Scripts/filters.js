"use strict";

Number.prototype.formatMoney = function(c, d, t){
var n = this, c = isNaN(c = Math.abs(c)) ? 2 : c, d = d == undefined ? "," : d, t = t == undefined ? "." : t, s = n < 0 ? "-" : "", i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 };
 
CampaignApp.filter('myCurrency', function() {
	return function(number, decPlaces, decimalSep, thousandSep) {
		decPlaces = decPlaces || 0;
		var currencySymbol = "$";
		decimalSep = decimalSep || ".";
		thousandSep = thousandSep || ",";
		return currencySymbol + (number).formatMoney(decPlaces, decPlaces, thousandSep);
	};
});


CampaignApp.filter('myCurrencyThous', function() {
	return function(number, decPlaces, decimalSep, thousandSep) {
		decPlaces = decPlaces || 0;
		var currencySymbol = "$";
		decimalSep = decimalSep || ".";
		thousandSep = thousandSep || ",";
		var numberThous = number/1000;
		return currencySymbol + (numberThous).formatMoney(decPlaces, decPlaces, thousandSep);
	};
});