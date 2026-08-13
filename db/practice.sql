-- - How many postings per source?
-- - Which company has the most postings?
-- - What is the average description length per source?


SELECT COUNT(id), source
from postings
GROUP BY source;



SELECT COUNT(id),company 
from postings 
GROUP BY company
ORDER BY COUNT(id) DESC
LIMIT 1;



SELECT AVG(LENGTH(description)), source 
from postings 
GROUP BY source;