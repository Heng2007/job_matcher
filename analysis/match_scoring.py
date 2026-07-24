"""Match scoring against my skill profile, and the unlock table.

Responsible for: scoring every posting by how much of its required skill set I
already have, flagging near-misses (postings missing at most 2 of my skills),
and building the "learn X -> unlock N postings" table that turns the database
into a learning plan.

Inputs: my_skills.json; the skills detected per posting by
analysis/skills_taxonomy.py; posting relevance/category from the trained model.

Outputs: a match percentage per posting; a ranked shortlist; a near-miss list
with the specific missing skills named; and an unlock table counting, for each
skill I don't have, how many additional postings learning it would qualify me
for — sorted by that count.

How I'll know it works: a posting requiring only skills I have scores 100%, a
posting requiring none of them scores 0%, the near-miss list contains only
postings missing 1-2 skills, and the top of the unlock table matches what I'd
guess by eye from the shortlist.
"""
