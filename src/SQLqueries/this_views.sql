CREATE OR REPLACE VIEW This_Rev AS
((SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('B. This Month' AS VARCHAR) AS B, sum("bookedRev") AS ThisMonth
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('month', date) = date_part('month', now()))
  AND (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp)
UNION
(SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('C. This Quarter' AS VARCHAR) AS B, sum("bookedRev") AS ThisQuarter
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = date_part('quarter', now()))
  AND (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp)
UNION
(SELECT CAST(channel || '|' || cp AS VARCHAR) AS A, CAST('D. This Year' AS VARCHAR) AS B, sum("bookedRev") AS ThisYear
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp) ORDER BY 1);




SELECT *
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE date >= now() - interval '7 days'

SELECT now() - interval '7 days'

DROP VIEW This_month;
DROP VIEW This_quarter;
DROP VIEW This_year;