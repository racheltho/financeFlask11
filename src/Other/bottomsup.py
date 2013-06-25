SELECT Owner.Name, Rate_Type__c, Name, Campaign_EVENT__c, StageName, BillingSchedule__c, Agency__c
FROM Opportunity
LIMIT 50


SELECT Sc.Revenue, Sc.ScheduleDate, Sc.CurrencyIsoCode, Sc.Quantity, Sc.Type, Ow.Name, Op.Rate_Type__c, Op.Name, Op.Campaign_EVENT__c, Op.StageName, Op.BillingSchedule__c, Op.Agency__c
FROM OpportunityLineItemSchedule Sc, Sc.OpportunityLineItem.Opportunity Op, Op.Owner Ow
WHERE not Op.StageName LIKE '0 - Lost'
LIMIT 50