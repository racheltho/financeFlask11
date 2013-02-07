
CREATE OR REPLACE VIEW Agencytable AS
SELECT CAST(P.id || '|' || P.parent || '|' || A.advertiser AS Varchar) AS A, CAST (date_part('year', B.date) || ' ' || 'Q' || date_part('quarter', B.date) AS Varchar) AS Q,
	SUM(B."bookedRev")
  FROM Parent P
  JOIN Advertiser A
  ON P.id = A.parent_agency_id
  JOIN Campaign C
  ON A.id = C.advertiser_id
  JOIN Booked B
  ON C.id = B.campaign_id 
  GROUP BY P.id, P.parent, A.advertiser,  Q
  ORDER BY P.id, A.advertiser, Q

SELECT * FROM Agencytable WHERE A LIKE 2 || '|%'


CREATE OR REPLACE VIEW Agencytable AS
SELECT P.id, CAST (date_part('year', B.date) || '|' || 'Q' || date_part('quarter', B.date) AS Varchar) AS Q,
	P.parent, A.advertiser, C.campaign, C.contracted_deal, C.revised_deal, SUM(B."bookedRev")
  FROM Parent P
  JOIN Advertiser A
  ON P.id = A.parent_agency_id
  JOIN Campaign C
  ON A.id = C.advertiser_id
  JOIN Booked B
  ON C.id = B.campaign_id 
  GROUP BY P.id, P.parent, A.advertiser, C.campaign, C.contracted_deal, C.revised_deal, Q
  ORDER BY P.id, A.advertiser, C.campaign, Q

  SELECT * FROM Agencytable WHERE id = 20