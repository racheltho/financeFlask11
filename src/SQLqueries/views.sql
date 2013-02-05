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

SELECT * FROM HistoricalCPM;
SELECT * FROM HistoricalCPA;

DROP VIEW HistoricalCount

CREATE OR REPLACE VIEW HistoricalCount AS
SELECT cast(channel || '|' || cp AS Varchar) AS cpchannel, cast (date_part('year', B.date) AS INT) as year, count(A."advertiser_id")
  FROM campaign A
  JOIN actual B
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  GROUP BY channel, A.cp, cast (date_part('year', B.date) AS INT)
  ORDER BY channel, A.cp DESC;

SELECT * FROM HistoricalCount

DROP VIEW HistoricalbyQ

CREATE OR REPLACE VIEW HistoricalbyQ AS
SELECT channel, cast (date_part('year', B.date) || ' ' || 'Q' || date_part('quarter', B.date) AS Varchar) AS Q,  sum("actualRev") AS Actual
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  GROUP BY channel, Q
  ORDER BY 1,2;

SELECT * FROM HistoricalbyQ

CREATE OR REPLACE VIEW CPA AS
SELECT channel, sum("bookedRev"), cast(date_part('year', B.date) AS INT) AS year
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = date_part('quarter', now()))
  AND (date_part('year', date) = date_part('year', now()))
  AND cp LIKE 'CPA'
GROUP BY channel, type, year;

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