
SELECT * FROM
(SELECT count(A.id) AS counta, A.id
  FROM campaign A
  JOIN campaignchange B
  ON A.id = B.campaign_id
  JOIN actual C
  ON A.id = C.campaign_id
  JOIN actualchange D
  ON A.id = D.campaign_id AND D.date = C.date
  JOIN bookedchange E
  ON A.id = E.campaign_id AND D.date = E.date
  JOIN booked F
  ON A.id = F.campaign_id AND D.date = F.date
  GROUP BY A.id) AS hello
  WHERE counta = 24;


SELECT A.id, A.campaign, C.date, C."actualRev", B.date, B."bookedRev" 
FROM campaign A
JOIN actual C
  ON A.id = C.campaign_id
  JOIN booked B
  on A.id = B.campaign_id AND C.date = B.date
WHERE A.id = 1839 or A.id = 1837

SELECT * FROM campaignchange D
JOIN campaign A
ON A.id = D.campaign_id
WHERE A.campaign LIKE '1-800-Dentist%'


SELECT * FROM campaign C
WHERE C.campaign LIKE '1-800-Dentist%'
