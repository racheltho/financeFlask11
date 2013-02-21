CREATE INDEX adv_adv_index ON advertiser (advertiser);

CREATE OR REPLACE VIEW CampaignBooked AS
SELECT C.campaign, C.type, P.product, CH.channel, A.advertiser, C.industry, C.agency, C.sfdc_oid, C.rep_id, C.cp, C.start_date, C.end_date, 
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
SELECT cast(channel || '|' || cp AS Varchar) AS cpchannel, cast (date_part('year', B.date) AS INT) as year, count(A."advertiser_id")
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  GROUP BY channel, A.cp, cast (date_part('year', B.date) AS INT)
  ORDER BY channel, A.cp DESC;

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