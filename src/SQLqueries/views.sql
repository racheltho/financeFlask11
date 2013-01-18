CREATE VIEW BookedRevenue AS


SELECT channel, type, cp, sum("bookedRev")
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = 4 ) --date_part('quarter', now()))
  AND (date_part('year', date) = 2011)
GROUP BY channel, type, cp

SELECT * FROM BookedRevenue

CREATE VIEW ActualRevenue AS
SELECT channel, type, cp, sum("actualRev")
  FROM actual B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
GROUP BY channel, type, cp

SELECT EXTRACT (YEAR FROM CURRENT_TIMESTAMP)

SELECT date, date_part('quarter', date) FROM booked