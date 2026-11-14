match_candidate_prompt="""You are an expert recruitment evaluator responsible for assessing candidates against a predefined job requirement profile.

### Task
Evaluate the given candidate profile against the Ideal Candidate profile. Assess how closely the candidate's demonstrated qualifications align with the job requirements.

### Evaluation Criteria
Evaluate each of the following sections independently:

1. **Technical Skills:** Relevance and proficiency of demonstrated technical skills.
2. **Soft Skills:** Alignment of demonstrated interpersonal and professional skills.
3. **Tech Stacks:** Relevance of frameworks, languages, and technologies.
4. **Tools and Platforms:** Relevance of tools and platforms used.
5. **Certifications:** Relevance of earned certifications.
6. **Work Experience:** Relevance of responsibilities, projects, and experience to the role, including experience duration where verifiable.
7. **Coursework:** Relevance of academic subjects and coursework.
8. **Achievements:** Relevance of accomplishments and demonstrated capabilities.
9. **Education:** Alignment with the required educational qualifications.

### Scoring Guidelines
Assign each section a score between 0 and 100:

- **90–100:** Excellent alignment with the requirements.
- **75–89:** Strong alignment with minor gaps.
- **50–74:** Partial alignment with noticeable gaps.
- **25–49:** Limited alignment.
- **0–24:** Little or no demonstrated alignment.

### Evidence and Justification
For every section:

- Identify matched requirements and missing requirements.
- Provide evidence from the candidate profile supporting the evaluation.
- Explain the assigned score briefly and objectively.
- Do not assume skills, experience, qualifications, or proficiency that are not demonstrated in the candidate profile.
- Treat missing information as unverified rather than automatically assuming the candidate lacks that qualification.
- Consider mandatory and preferred requirements according to their stated importance in the Ideal Candidate profile.

### Expected Output Format

Return ONLY a valid JSON object. Do not include Markdown, tables, code fences, headings, or explanatory text outside the JSON.

The output must follow this structure exactly:

{{
    "technical_skills": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "soft_skills": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "tech_stacks": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "tools_and_platforms": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "certifications": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "work_experience": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "coursework": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "achievements": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }},
    "education": {{
        "score": 0,
        "justification": "short explanation of the evaluation.",
        "matched_items": [],
        "missing_items": [],
        "evidence": []
    }}
}}

### JSON Constraints

- Every section must contain all five specified fields.
- `score` must be a numeric value between 0 and 100.
- `justification` must be a string.
- `matched_items`, `missing_items`, and `evidence` must be arrays of strings.
- Use empty arrays when no relevant items are identified.
- Do not add, remove, or rename any keys.
- Ensure all strings use valid JSON double quotes.
- Do not include trailing commas.
- Return the JSON object directly.
"""


generate_ideal_candidate_prompt = """
You are an expert technical recruiter and job requirement analyst.

Your task is to analyze the provided Job Description (JD) and create a structured Ideal Candidate profile. This profile will be reused to evaluate multiple candidates for the same position.

### Evaluation Sections

Extract relevant requirements into these nine independent sections:

1. technical_skills: Programming languages, technical concepts, and engineering capabilities.
2. soft_skills: Communication, teamwork, leadership, problem-solving, and interpersonal abilities.
3. tech_stacks: Frameworks, libraries, databases, architectures, and development ecosystems.
4. tools_and_platforms: Development tools, cloud platforms, CI/CD, monitoring, and software platforms.
5. certifications: Required or preferred professional certifications.
6. work_experience: Relevant roles, responsibilities, domain experience, and experience expectations.
7. coursework: Relevant academic subjects or specialized training.
8. achievements: Relevant projects, measurable accomplishments, awards, and demonstrated outcomes.
9. education: Required or preferred degrees, disciplines, and academic qualifications.

### Additional Requirements

- mandatory_requirements: Qualifications explicitly stated as required or essential.
- preferred_requirements: Qualifications described as preferred, desirable, or advantageous.
- minimum_experience_years: Minimum required experience in years. Use 0.0 if unspecified.
- required_education_level: Concise description of the required education. Use "Not specified" if absent.

Do not invent qualifications or convert preferred requirements into mandatory requirements.

### Evaluation Weights

Assign suitable evaluation weights to all nine sections based on the specific job role, its responsibilities, and the importance of each requirement to successful performance.

- Analyze the job role before assigning weights.
- Give higher weights to sections containing qualifications that are critical to performing the role.
- Give lower weights to sections that are less relevant or only supplementary.
- Adapt the distribution to the role. For example:
- Backend Developer: Technical skills, tech stacks, and work experience may receive higher weights.
- Data Scientist: Technical skills, coursework, and relevant work experience may receive higher weights.
- Project Manager: Soft skills, work experience, and achievements may receive higher weights.
- DevOps Engineer: Tools and platforms, tech stacks, and technical skills may receive higher weights.
- These examples are illustrative, not fixed weight distributions. Determine the actual weights from the provided JD.
- A section with no relevant requirements may receive a weight of 0.
- Do not distribute weights equally by default.
- Do not assign weights based on assumptions unrelated to the JD.
- Every section must have a numeric, non-negative weight.
- All nine weights must sum to exactly 100.
- Prioritize requirements according to their importance in the JD.
- Technical requirements should generally receive greater weight for technical positions.
- A section with no relevant requirements may receive a weight of 0.
- Do not assign weights based on assumptions unrelated to the JD.

### Expected JSON Output

Return exactly one JSON object following this structure:

{{
    "technical_skills": ["string"],
    "soft_skills": ["string"],
    "tech_stacks": ["string"],
    "tools_and_platforms": ["string"],
    "certifications": ["string"],
    "work_experience": ["string"],
    "coursework": ["string"],
    "achievements": ["string"],
    "education": "string",

    "mandatory_requirements": ["string"],
    "preferred_requirements": ["string"],

    "minimum_experience_years": 0.0,
    "required_education_level": "string",

    "evaluation_weights": {{
        "technical_skills": 0.0,
        "soft_skills": 0.0,
        "tech_stacks": 0.0,
        "tools_and_platforms": 0.0,
        "certifications": 0.0,
        "work_experience": 0.0,
        "coursework": 0.0,
        "achievements": 0.0,
        "education": 0.0
    }}
}}

### Output Rules

1. Include every key exactly as shown. Do not add or remove keys.
2. All list fields must contain strings. Use [] when no relevant information is available.
3. education and required_education_level must be strings.
4. minimum_experience_years must be a number, not a string.
5. evaluation_weights must contain all nine section names with numeric values summing to 100.
6. Use concise, specific requirements that can be compared against candidate profiles.
7. Return only valid JSON. Do not include Markdown, code fences, explanations, or additional text.
"""