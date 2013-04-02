SELECT *, similarity(A.advertiser, 'Seagate Recovery Services')
  FROM advertiser A
  WHERE similarity(A.advertiser, 'Seagate Recovery Services') > .1
  ORDER by similarity(A.advertiser, 'Seagate Recovery Services') DESC
  LIMIT 3;

CREATE EXTENSION pg_trgm


SELECT * FROM Campaign ORDER BY advertiser_id

SELECT * FROM Advertiser where Advertiser LIKE 'Shutterfly%'