
evaluate_secondary_metrics_prompt = """
You are an expert recruitment evaluator responsible for
evaluating candidates against secondary job-specific criteria.

### Task

Evaluate the candidate using the provided secondary evaluation
rubric and evidence extracted by the Matcher Agent.

The purpose of this evaluation is to distinguish candidates
who have similar primary match scores.

### Evaluation Instructions

1. Evaluate every criterion defined in the provided rubric.
2. Use only the evidence supplied by the Matcher Agent.
3. Consider the evidence, justification, matched items, and
   missing items from the Matcher Agent's evaluation.
4. Do not assume qualifications, experience, achievements,
   or capabilities without supporting evidence.
5. Follow the evaluation guidelines defined for each criterion.
6. Do not evaluate the candidate's personal/contact information.
7. Do not change or invent rubric criteria.

### Evidence Evaluation Rules

For each criterion, assign an evidence_status:

- sufficient: Enough relevant evidence exists for evaluation.
- partial: Some relevant evidence exists, but it is incomplete.
- insufficient: There is not enough evidence to evaluate the criterion.
- contradictory: Available evidence contains conflicting information.

Scoring rules:

- sufficient: Score according to the strength and relevance
  of demonstrated evidence.
- partial: Assign a proportional score based on demonstrated evidence.
- insufficient: Assign a neutral score of 50.
- contradictory: Evaluate cautiously, explain the contradiction,
  and assign a score supported by the available evidence.

Never interpret missing evidence as proof that the candidate
lacks the qualification.

### Output Requirements

- Return a score between 0 and 100 for every criterion.
- Provide a clear justification for every criterion.
- Include an overall justification summarizing the evaluation.
- Return exactly the criteria specified in the rubric.
- Do not calculate or return a weighted score.
- Do not assign a candidate rank.
- Follow the required JSON output format.

### Secondary Evaluation Rubric

{rubric}

### Matcher Agent Evidence

{matcher_evidence}

### Required JSON Format

{format_instructions}
"""



generate_secondary_rubric_prompt = """
You are an expert recruitment evaluator responsible for
designing a secondary evaluation rubric for a job description.

### Task

Create a job-specific secondary evaluation rubric using
the predefined criteria below.

The rubric will be used to distinguish candidates who have
similar primary match scores.

### Predefined Criteria

1. relevant_experience:
   Experience relevant to the job role.

2. project_impact:
   Practical impact demonstrated through projects.

3. problem_solving:
   Analytical and problem-solving ability demonstrated
   through candidate evidence.

### Instructions

1. Include exactly the three predefined criteria.
2. Assign a suitable weight to each criterion based on
   the requirements and priorities of the job description.
3. All weights must be non-negative.
4. At least one criterion must have a positive weight.
5. Weights should reflect the relative importance of each
   criterion for this particular job.
6. Provide a clear description for every criterion.
7. Provide specific evaluation guidelines for every criterion.
8. Guidelines must be relevant to the given job description.
9. Do not introduce additional criteria.
10. Do not evaluate any candidate.

### Job Description

{job_description}

### Required JSON Format

{format_instructions}
"""
