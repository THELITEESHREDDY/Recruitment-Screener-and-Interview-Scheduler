from agents.matcher.graph import matcher_graph

initial_state = {
    "jd_id": "JD001",
    "job_description": """Job Description
Job Details*

- We require someone who comes with a wide range of experience in the LAMP stack. Our software can be very complex, so be prepared.

- We mainly use Javascript/jQuery for our frontend mainstay, so you would be required to gain proficiency in this as well.

- We use a couple of database systems, MySQL and Apache Solr. You would be expected to become comfortable with their use, deployment, and scaling.

- Our devs are mini-server admins as well and you would need to learn how to work through a Linux terminal.

- We rigorously document our entire codebase, so you will be expected to document A LOT!

- We would prefer a candidate who can demonstrate creative live projects and has a Github profile they can show off. Although, this is not required.

Job Summary*

We're building automated customer service software and we need a full-stack developer to join our technological roller coaster. Join us and watch your product go through the entire life cycle. Plan it, build it, test it, deploy it, scale it, and sip coffee while you watch it grow!

Currently open to Indian Applicants Only.

Education
Bachelor Of Technology (B.Tech/B.E), Bachelor of Dental Surgery (B.D.S), Bachelor of Homeopathic Medicine and Surgery (BHMS), Bachelor of Science (B.Sc), Bachelors of Law (B.L/L.L.B), Bachelor in General Studies (BGS), Bachelor of Arts (B.A), Bachelor of Applied Science (BAS), Bachelor of Education (B.Ed), Bachelor of Ayurvedic Medicine and Surgery (BAMS), Bachelor of Business Administration (B.B.A), Bachelor of Interdisciplinary Studies, Bachelor of Commerce (B.Com), Bachelor in Hotel Management (B.H.M), Bachelor of Architecture (B.Arch), Bachelor Of Pharmacy (B.Pharm), Bachelor of Music Education (B.M.E.), Bachelor of Social Work (B.S.W), MBBS, Bachelor of Health Science, Bachelor Of Computer Application (B.C.A), Bachelor of Liberal Arts (BLA/ALB), Bachelor of Music

More Info
Job Type:
Permanent Job, Work From Home
Industry:
Information Technology, SaaS, Software
Role:
Software Developer, Technical Architect, Product Management, Devops
Function:
IT/Software Development - Application Programming/Maintenance
Employment Type:
Full time
Key Skills
HTML/CSS

Full-Stack Development

Code Documentation

Deployment
Problem Solving
Php
MySQL
Javascript
jQuery
Lamp Stack
Linux
Github
Debugging
Server Management
Rest Apis
Scalability
Agile Development
Apache Solr""",
    "candidate": candidate_data,
    "retry_count": 0,
    "validation_errors": []
}

result = matcher_graph.invoke(initial_state)