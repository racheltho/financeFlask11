﻿CREATE INDEX adv_adv_index ON advertiser (advertiser);

CREATE INDEX chan_chan_index ON channel (channel);

CREATE INDEX campaign_id_index ON campaign (id);

CREATE INDEX actual_campid_index ON actual (campaign_id);

CREATE INDEX booked_campid_index ON booked (campaign_id);

CREATE INDEX campaign_chan_index ON campaign (channel_id);

CREATE INDEX rep_lastname_index ON rep (last_name);

CREATE INDEX newsfdc_ioname_index ON newsfdc (ioname);

CREATE INDEX channelmapping_sfchannel_index ON channelmapping (salesforce_channel);




CREATE OR REPLACE VIEW ForecastLastWeek AS
SELECT F.channel_id, forecast, goal, created
FROM forecastq F
JOIN
(SELECT MAX(created) AS lastweek_date, channel_id
FROM forecastq
WHERE created <= current_date - integer '5'
GROUP BY channel_id) AS C
ON F.channel_id = C.channel_id AND F.created = C.lastweek_date;


SELECT date 
FROM Forecastq
GROUP by date
ORDER BY date DESC;

SELECT CH.channel, F.forecast, F.lastweek, F.cpm_rec_booking, F.qtd_booking, F.deliverable_rev, F.goal
FROM forecastq F
JOIN
(SELECT MAX(created) AS lastweek_date, channel_id
FROM forecastq
WHERE date = date '2013-04-03'
GROUP BY channel_id) AS C
ON F.channel_id = C.channel_id AND F.created = C.lastweek_date
JOIN channel CH
ON F.channel_id = CH.id;


CREATE OR REPLACE VIEW ForecastThisQ AS
SELECT A.*, B."cpaBooked", B."cpaActual" FROM
(SELECT C.id AS channel_id, channel, sum("bookedRev") AS "cpmBooked", sum("actualRev") AS "cpmActual"
--CAST(date_part('quarter', now()) || ' ' || date_part('year', now()) || ' ' || cp AS VARCHAR) 
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN actual D
  ON A.id = D.campaign_id
  WHERE (date_part('quarter', B.date) = date_part('quarter', now()))
  AND (date_part('year', B.date) = date_part('year', now()))
  AND (date_part('quarter', D.date) = date_part('quarter', now()))
  AND (date_part('year', D.date) = date_part('year', now()))
  AND cp LIKE 'CPM'
GROUP BY channel, C.id) AS A
LEFT OUTER JOIN
(SELECT C.id AS channel_id, channel, sum("bookedRev") AS "cpaBooked", sum("actualRev") AS "cpaActual"
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN actual D
  ON A.id = D.campaign_id
  WHERE (date_part('quarter', B.date) = date_part('quarter', now()))
  AND (date_part('year', B.date) = date_part('year', now()))
  AND (date_part('quarter', D.date) = date_part('quarter', now()))
  AND (date_part('year', D.date) = date_part('year', now()))
  AND cp LIKE 'CPA'
GROUP BY channel, C.id) AS B
ON A.channel = B.channel;


CREATE OR REPLACE VIEW ForecastThisYear AS
SELECT A.*, B."CPA Booked", B."CPA Actual" FROM
(SELECT channel, sum("bookedRev") AS "CPM Booked", sum("actualRev") AS "CPM Actual"
--CAST(date_part('quarter', now()) || ' ' || date_part('year', now()) || ' ' || cp AS VARCHAR) 
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN actual D
  ON A.id = D.campaign_id
  WHERE (date_part('year', B.date) = date_part('year', now()))
  AND (date_part('year', D.date) = date_part('year', now()))
  AND cp LIKE 'CPM'
GROUP BY channel) AS A
LEFT JOIN
(SELECT channel, sum("bookedRev") AS "CPA Booked", sum("actualRev") AS "CPA Actual"
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN actual D
  ON A.id = D.campaign_id
  WHERE (date_part('year', B.date) = date_part('year', now()))
  AND (date_part('year', D.date) = date_part('year', now()))
  AND cp LIKE 'CPA'
GROUP BY channel) AS B
ON A.channel = B.channel;



CREATE OR REPLACE VIEW CampaignBooked AS
SELECT C.campaign, C.type, P.product, CH.channel, A.advertiser, C.industry, C.agency, C.sfdc_oid, C.cp, C.start_date, C.end_date, 
  C.cpm_price, C.contracted_impr, C.booked_impr, C.delivered_impr, C.contracted_deal, C.revised_deal, C.opportunity, B.date, B."bookedRev"
  FROM campaign C
  JOIN booked B
  ON C.id = B.campaign_id
  JOIN advertiser A
  ON C.advertiser_id = A.id
  JOIN channel CH
  ON C.channel_id = CH.id
  JOIN Product P
  ON C.product_id = P.id
  ORDER BY C.campaign;



CREATE OR REPLACE VIEW Agencytable AS
SELECT CAST(P.id || '|' || P.parent || '|' || A.advertiser AS Varchar) AS A, CAST (date_part('year', B.date) || ' ' || 'Q' || date_part('quarter', B.date) AS Varchar) AS Q,
	SUM(B."bookedRev")
  FROM Parent P
  JOIN Advertiser A
  ON P.id = A.parent_id
  JOIN Campaign C
  ON A.id = C.advertiser_id
  JOIN Booked B
  ON C.id = B.campaign_id 
  GROUP BY P.id, P.parent, A.advertiser,  Q
  ORDER BY P.id, A.advertiser, Q;

CREATE OR REPLACE VIEW HistoricalbyQ AS
SELECT channel, cast (date_part('year', B.date) || ' ' || 'Q' || date_part('quarter', B.date) AS Varchar) AS Q,  sum("actualRev") AS Actual
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  GROUP BY channel, Q
  ORDER BY 1,2;

CREATE OR REPLACE VIEW HistoricalCount AS
(SELECT cast(channel || '|' || cp AS Varchar) AS cpchannel, cast (date_part('year', B.date) AS INT) as year, count(P.id)
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN advertiser AD
  ON A.advertiser_id = AD.id
  JOIN parent P
  ON AD.parent_id = P.id
  WHERE channel NOT LIKE 'Publisher'
  GROUP BY channel, A.cp, cast (date_part('year', B.date) AS INT)
  ORDER BY channel, A.cp DESC)
UNION
(SELECT cast(channel || '|' || cp AS Varchar) AS cpchannel, cast (date_part('year', B.date) AS INT) as year, count(A.advertiser_id)
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE channel LIKE 'Publisher'
  GROUP BY channel, A.cp, cast (date_part('year', B.date) AS INT)
  ORDER BY channel, A.cp DESC)
  ORDER BY cpchannel, year ASC;

  CREATE OR REPLACE VIEW HistoricalCPA AS
SELECT channel, cast (date_part('year', B.date) AS INT) as year, sum("actualRev") AS Actual
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE cp LIKE 'CPA'
  GROUP BY channel, cast (date_part('year', B.date) AS INT)
  ORDER BY 1,2;

CREATE OR REPLACE VIEW HistoricalCPM AS
SELECT channel, cast (date_part('year', B.date) AS INT) as year, sum("actualRev") AS Actual
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE cp LIKE 'CPM'
  GROUP BY channel, cast (date_part('year', B.date) AS INT)
  ORDER BY 1,2;


CREATE OR REPLACE VIEW This_Rev AS
((SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('This Month' AS VARCHAR) AS B, sum("bookedRev") AS ThisMonth
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('month', date) = date_part('month', now()))
  AND (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp)
UNION
(SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('This Quarter' AS VARCHAR) AS B, sum("bookedRev") AS ThisQuarter
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = date_part('quarter', now()))
  AND (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp)
UNION
(SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('This Year' AS VARCHAR) AS B, sum("bookedRev") AS ThisYear
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp) ORDER BY 1);


CREATE OR REPLACE VIEW BookedChanges AS
SELECT cast(A.campaign || '|' || BB.change_date || '|' || DD.change_date AS varchar) AS Campaign, BB.date, cast(BB."bookedRev" || '|' || DD."bookedRev" AS Varchar) AS Booked --, BB."bookedRev" - DD."bookedRev" AS Difference
FROM
(SELECT B.* 
FROM bookedchange B
JOIN
(SELECT MAX(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  WHERE change_date <= current_date - integer '7'
  GROUP BY campaign_id, date) AS C
ON B.change_date = C.max_date 
  AND B.campaign_id = C.campaign_id
  AND B.date = C.date) AS BB
JOIN
(SELECT D.*
FROM bookedchange D
JOIN
(SELECT MAX(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  GROUP BY campaign_id, date) AS E
ON D.change_date = E.max_date 
  AND D.campaign_id = E.campaign_id
  AND D.date = E.date) AS DD
ON BB.campaign_id = DD.campaign_id
  AND BB.date = DD.date
JOIN campaign A
ON A.id = BB.campaign_id
WHERE BB."bookedRev" - DD."bookedRev" <> 0 AND DD.change_date - BB.change_date > 0
ORDER BY BB.campaign_id, BB.date;

CREATE OR REPLACE VIEW NewBookedChanges AS
SELECT DISTINCT ON (Campaign, BB.date) cast(A.campaign || '|' || BB.change_date || '|' || DD.change_date AS varchar) AS Campaign, BB.date, cast(BB."bookedRev" || '|' || DD."bookedRev" AS Varchar) AS Booked --, BB."bookedRev" - DD."bookedRev" AS Difference
FROM
(SELECT B.* 
FROM bookedchange B
JOIN
(SELECT MAX(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  WHERE change_date <= current_date - integer '7'
  GROUP BY campaign_id, date) AS C
ON B.change_date = C.max_date 
  AND B.campaign_id = C.campaign_id
  AND B.date = C.date) AS BB
JOIN
(SELECT D.*
FROM bookedchange D
JOIN
(SELECT MAX(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  WHERE change_date > current_date - integer '7'
  GROUP BY campaign_id, date) AS E
ON D.change_date = E.max_date 
  AND D.campaign_id = E.campaign_id
  AND D.date = E.date) AS DD
ON BB.campaign_id = DD.campaign_id
  AND BB.date = DD.date
JOIN campaign A
ON A.id = BB.campaign_id
WHERE BB."bookedRev" - DD."bookedRev" <> 0 AND DD.change_date - BB.change_date > 0;
--ORDER BY BB.campaign_id, BB.date