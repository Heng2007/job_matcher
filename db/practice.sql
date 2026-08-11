-- - How many postings per source?
-- - Which company has the most postings?
-- - What is the average description length per source?


SELECT company from postings
GROUP BY company;