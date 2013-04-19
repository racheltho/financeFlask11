SELECT C.id, B.channel, C.advertiser, sum(D."bookedRev")
  FROM channel B
  JOIN campaign A
  ON A.channel_id = B.id
  JOIN advertiser C
  ON A.advertiser_id = C.id
  JOIN booked D
  ON D.campaign_id = A.id
  GROUP BY C.id, B.channel, C.advertiser
  ORDER BY C.advertiser ASC;
  
  