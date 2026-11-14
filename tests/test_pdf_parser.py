import pymupdf
import pytest
from fastapi import UploadFile
from io import BytesIO
from agents.parser.nodes import parse_resume_content
from agents.parser.main import process_resume

def test_pdf_parsing():

    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (50, 50),
        "Name: Liteesh Reddy\n"
        "Email: liteesh@example.com\n"
        "Skills: Python, FastAPI, SQL"
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    state = {
        "id": "candidate_001",
        "user_input": {
            "candidate_resume": {
                "filename": "resume.pdf",
                "content_type": "application/pdf",
                "data": pdf_bytes
            },
            "candidate_id": "candidate_001",
            "resume_content": []
        },
        "graph_output": {
            "id": "candidate_001"
        }
    }

    result = parse_resume_content(state)

    print(result["user_input"]["resume_content"])

    assert len(result["user_input"]["resume_content"]) > 0
    assert "Liteesh Reddy" in result["user_input"]["resume_content"][0]




def create_test_pdf():
    doc = pymupdf.open()
    page = doc.new_page()

    page.insert_text(
        (50, 50),
        """
        Liteesh Reddy
        Email: liteesh@example.com
        Phone: 9876543210
        LinkedIn: https://linkedin.com/in/liteesh

        Skills: Python, C++, FastAPI, SQL
        Technologies: React, PostgreSQL, LangGraph
        Tools: Git, GitHub, VS Code

        Education: B.Tech Computer Science
        Coursework: DBMS, Operating Systems

        Achievements: First Runner-Up in Perceptive Minds
        Certifications: hehe_cloud_certification
        work Experience: Internship at google, SWE at OpenAI
        """
    )

    pdf_bytes = doc.tobytes()
    doc.close()

    return pdf_bytes



@pytest.mark.asyncio
async def test_resume_graph():

    pdf_bytes = create_test_pdf()

    pdf = UploadFile(
        filename="test_resume.pdf",
        file=BytesIO(pdf_bytes)
    )
    
    result =  await process_resume(pdf,"1111111",99,1)


    print("\nRESUME EXTRACTION RESULT")
    print("=======================")
    print(result)

    assert result is not None