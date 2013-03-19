SELECT advertiser
  FROM advertiser A
  WHERE similarity(A.advertiser, 'Shutterfl') > .4
  ORDER by similarity(A.advertiser, 'Shutterfl') DESC
  LIMIT 3;

CREATE EXTENSION pg_trgm


SELECT * FROM Campaign ORDER BY advertiser_id

SELECT * FROM Advertiser where Advertiser LIKE 'Shutterfly%'