SELECT B.* FROM bookedchange B
JOIN
(SELECT MAX(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  WHERE change_date <= current_date - 1
  GROUP BY campaign_id, date) AS C
ON B.change_date = C.max_date 
  AND B.campaign_id = C.campaign_id
  AND B.date = C.date
ORDER BY B.campaign_id, B.date;

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
WHERE BB."bookedRev" - DD."bookedRev" <> 0 AND DD.change_date - BB.change_date > 0
--ORDER BY BB.campaign_id, BB.date



SELECT * FROM bookedChange B
JOIN campaign A
ON A.id = B.campaign_id
WHERE A.campaign LIKE '%Dentist%'
ORDER BY change_date


(SELECT B.* 
FROM bookedchange B
JOIN
(SELECT MIN(change_date) AS max_date, campaign_id, date
  FROM bookedchange
  WHERE change_date <= current_date - 4 AND campaign_id = 1456
  GROUP BY campaign_id, date) AS C
ON B.change_date = C.max_date 
  AND B.campaign_id = C.campaign_id
  AND B.date = C.date)


