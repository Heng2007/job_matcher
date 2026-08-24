# Job Market Intelligence Tool

A personal tool that classifies job postings, scores them against my current skills, and turns the gap into a "learn X → unlock N postings" plan.

## Setup

## Data Sources
|--------------|------|-------------------------------------------------------------------------------------|
|    source    | rows |                           description                                               |
|--------------|------|-------------------------------------------------------------------------------------|
| Greenhouse   | 4664 |           public Greenhouse Job Board API, picked 20 companies                      |
|--------------|------|-------------------------------------------------------------------------------------|
| Kaggle       | 1667 | https://www.kaggle.com/datasets/arshkon/linkedin-job-postings, pick 1200 out of 120k|
|--------------|------|-------------------------------------------------------------------------------------|
| CLNx         | 805  |                   UofT 2025 summer work study program                               |       
|--------------|------|-------------------------------------------------------------------------------------|
## Methodology
1. How the labels for training were made: 220 lables are hand labeled by me, the rest of 6416 labels are labeled by LLM. `label_source` distinguishing them.
## Results
1. Changing from 8 categories to 5 categories effectivelly dropped the disgreement rate between me and LLM. 55% under 8 classes → 96% under 5 classes
   
## Limitations
1. Since the original category, `NLP / LLM` and `Machain Learning`, are hard to differ. They are collapsed into one category, the cost is that the model can no longer find a job specicifically for `NLP / LLM` or specifically for `Machain Learning`. 
2. Only single digit number of `quant/finance` job present in the 6 thousands postings in training data, therefore the category is removed. The cost is that the model can no longer identify `quant/finance` jobs.
3. A keyword can match a word without matching a role, then the model got tricked by the mismatch. For example, a big part of positions involve labs were SpaceX manufacturing roles ("Chemical Lab Technician", "EEE Parts Lab Specialist"). Fixed it by replacing "lab" with a more specfic keywords.
