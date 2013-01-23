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

SELECT * FROM HistoricalCPM;
SELECT * FROM HistoricalCPA;


CREATE OR REPLACE VIEW HistoricalRevenue AS
SELECT channel,  cp, sum(B."actualRev") AS y2011, sum(D."actualRev") AS y2012
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  JOIN actual D
  ON A.id = D.campaign_id
 WHERE date_part('year', B.date) = 2011 AND date_part('year', D.date) = 2012
  GROUP BY channel, cp
  ORDER BY channel, cp DESC;

CREATE OR REPLACE VIEW HistoricalCount2011 AS

SELECT channel, cp, , date_part('year', B.date) AS Year, count(A."advertiser_id")
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  GROUP BY channel, A.cp, date_part('year', B.date)
  ORDER BY channel, A.cp DESC;

CREATE OR REPLACE VIEW HistoricalCount2012 AS
SELECT channel, cp, count(A."advertiser_id") AS count2012
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
 WHERE date_part('year', B.date) = 2012
  GROUP BY channel, A.cp
  ORDER BY channel, A.cp DESC;

CREATE OR REPLACE VIEW CPA AS
SELECT channel, sum("bookedRev"), date_part('year', B.date) AS year
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = date_part('quarter', now()))
  AND (date_part('year', date) = date_part('year', now()))
  AND cp LIKE 'CPA'
GROUP BY channel, type;

--SELECT * FROM BookedRevenue;

CREATE OR REPLACE VIEW ActualRevenue AS
SELECT channel, type, cp, sum("actualRev")
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
GROUP BY channel, type, cp;

SELECT EXTRACT (YEAR FROM CURRENT_TIMESTAMP);

--SELECT date, date_part('quarter', date) FROM booked;