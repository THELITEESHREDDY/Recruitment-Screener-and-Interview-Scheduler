from .graph import resume_graph 
from fastapi import UploadFile

async def process_resume(
    pdf: UploadFile,
    candidate_id: str,
    pep_score:int,
    pep_priority:int
):
    pdf_bytes = await pdf.read()
    initial_state = {
        "id": candidate_id,
        
        "user_input": {
            "candidate_resume": {
                "filename": pdf.filename,
                "content_type": "application/pdf",
                "data": pdf_bytes,
                "PEP_score": pep_score,
                "PEP_priority": pep_priority
            },
            "candidate_id": candidate_id,
            "resume_content": []
        },

        "graph_output": {
            "id": candidate_id,
            "name": "",
            "mobile_number": "",
            "email": "",
            "linkedin_url": "",

            "technical_skills": [],
            "soft_skills": [],

            "tech_stacks": [],
            "technologies": [],
            "tools_and_platforms": [],

            "certifications": [],
            "work_experience": [],
            "coursework": [],
            "achievements": [],

            "education": "",

            "PEP_score": pep_score,
            "PEP_priority": pep_priority
        }
    }

    result = await resume_graph.ainvoke(initial_state)

    return result["graph_output"]






