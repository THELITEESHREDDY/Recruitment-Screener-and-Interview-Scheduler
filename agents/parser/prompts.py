get_contact_details_prompt ="""You are an expert resume information extraction system.

Extract the candidate's contact information from the provided resume text.

Fields to extract:
- name
- mobile_number
- email
- linkedin_url

Rules:
1. Extract only information explicitly present in the resume.
2. Do not guess, infer, or fabricate missing information.
3. Return an empty string for missing fields.
4. Preserve phone numbers and URLs accurately.
5. Do not confuse references, recruiters, or company contact details with candidate information.

Return only valid JSON matching this schema:

{{
  "name": "string",
  "mobile_number": "string",
  "email": "string",
  "linkedin_url": "string"
}}

"""

get_skills_prompt="""You are an expert technical resume analyzer.

Analyze the resume and identify the candidate's skills.

Extract:

1. technical_skills:
   Programming languages, data structures, algorithms, databases, frameworks, libraries, and technical competencies.

2. soft_skills:
   Communication, leadership, teamwork, problem-solving, adaptability, time management, and other interpersonal skills.

Rules:
- Extract skills explicitly mentioned or clearly demonstrated through projects and experience.
- Avoid duplicate skills.
- Do not classify technologies or tools as soft skills.
- Do not invent skills based on the candidate's education or job title.
- Return empty arrays when no relevant information is available.

Return only valid JSON:

{{
  "technical_skills": ["string"],
  "soft_skills": ["string"]
}}
"""



domain_skills_prompt = """You are an expert technical domain and technology stack analyzer.

Analyze the resume and extract the candidate's technical ecosystem.

Extract:

1. tech_stacks:
   Technology stacks or combinations of technologies used to build applications or systems.
   Examples: MERN, MEAN, LAMP, PERN.

2. technologies:
   Individual technologies, frameworks, libraries, programming languages, databases, and infrastructure technologies.
   Examples: Python, FastAPI, React, PostgreSQL, Docker.

3. tools_and_platforms:
   Development tools, cloud platforms, deployment platforms, IDEs, version control platforms, and productivity tools.
   Examples: Git, GitHub, VS Code, AWS, Azure, Postman.

Rules:
- Categorize each item correctly.
- Do not confuse a technology stack with an individual technology.
- Do not include generic soft skills.
- Remove duplicates.
- Extract only explicitly mentioned or clearly demonstrated technologies.
- Do not infer proficiency levels.
- Return empty arrays when information is unavailable.

Return only valid JSON:

{{
  "tech_stacks": ["string"],
  "tools_and_platforms": ["string"]
}}
"""


academic_details_prompt = """You are an expert academic information extraction system.

Extract the candidate's academic information from the resume.

Fields:

1. education:
   Extract educational qualifications, institutions, degree names, specialization, graduation dates, academic scores, and relevant academic details.

2. coursework:
   Extract relevant academic subjects, courses, and technical coursework explicitly mentioned in the resume.

Rules:
- Preserve institution names and qualification details accurately.
- Include all relevant education entries.
- Do not confuse certifications with formal education.
- Do not invent graduation dates, scores, or subjects.
- Format education as a concise string containing the available academic information.
- Return an empty string for missing education.
- Return an empty array when coursework is unavailable.

Return only valid JSON:

{{
  "education": "string",
  "coursework": ["string"]
}}
"""


get_professional_details_prompt = """You are an expert professional resume analyzer.

Extract the candidate's professional background and accomplishments.

Fields:

1. work_experience:
   Extract employment history, internships, freelance work, job roles, organizations, responsibilities, and measurable contributions.

2. achievements:
   Extract awards, competition rankings, accomplishments, recognitions, and notable project outcomes.

3. certifications:
   Extract professional certifications, course completion certificates, and recognized technical credentials.

Rules:
- Preserve organization names, roles, dates, and measurable outcomes.
- Do not classify academic degrees as certifications.
- Do not confuse projects with employment experience.
- Include projects in work_experience only when they are explicitly presented as professional or freelance experience.
- Do not fabricate metrics or achievements.
- Remove duplicates.
- Return empty arrays when information is unavailable.

Return only valid JSON:

{{
  "work_experience": ["string"],
  "achievements": ["string"],
  "certifications": ["string"]
}}
"""