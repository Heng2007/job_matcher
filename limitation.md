1. Machine Learning and NLP/LLM has a lot of overlap, it is hard to classify a job between them.
2. Many postings have requirements that match the category, but they are actually organizer position if look closely on the description.do 
3. Research assistant is scoped by the skills a posting wants, not by the department it sits in. A psychologyup or public-health lab that wants R, SPSS or data analysis counts; a chemistry lab that wants pipetting is Not relevant.
4. A keyword can match a word without matching a role, then the model got tricked by the mismatch. For example, a big part of positions involve labs were SpaceX manufacturing roles ("Chemical Lab Technician", "EEE Parts Lab Specialist"). Fixed it by replacing "lab" with a more specfic keywords.
5. The corpus is dominated by a few employers: SpaceX 1734 postings (26%), Databricks 565, Stripe 500, Anthropic 400. Every category's shape are impacted by how those companies write job ads rather than the job market. 
