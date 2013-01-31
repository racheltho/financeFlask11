CREATE OR REPLACE VIEW This_month AS
SELECT channel, cp, sum("bookedRev"), cast(date_part('year', B.date) AS INT) AS year
  FROM booked B
  JOIN campaign A
  ON A.id = B.campaign_id
  JOIN channel C
  ON A.channel_id = C.id
  WHERE (date_part('quarter', date) = date_part('quarter', now()))
  AND (date_part('year', date) = date_part('year', now()))
GROUP BY channel, cp, year;