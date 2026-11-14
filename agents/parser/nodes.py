from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pymupdf
from io import BytesIO
import json
from shared.llm.provider import llm_service
from .state import OverallState
from .prompts import get_contact_details_prompt,get_skills_prompt,domain_skills_prompt,academic_details_prompt,get_professional_details_prompt
from .schemas import get_contact_details_output,get_technical_skills_output,get_skills_output,academic_skills_output,get_professional_details_output


def parse_resume_content(state: OverallState):

    pdf_bytes = state["user_input"]["candidate_resume"]["data"]

    document = pymupdf.open(
        stream=BytesIO(pdf_bytes),
        filetype="pdf"
    )

    resume_content = [
        page.get_text("text")
        for page in document
    ]

    document.close()

    return {
        "user_input": {
            **state["user_input"],
            "resume_content": resume_content
        }
    }

def get_contact_details(state: OverallState):
    """
    Extract name, mobile number, email and LinkedIn.
    """

    resume = state["user_input"]["resume_content"]

    parser = JsonOutputParser(pydantic_object=get_contact_details_output)
    

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_contact_details_prompt),
        ("user", "Resume: {input}")
    ])

    # Create the chain that guarantees JSON output
    chain = prompt | llm_service | parser

    result = chain.invoke({"input": resume})
    print(json.dumps(result, indent=2))

    # TODO: Call your extraction service.

    return {
        "graph_output": {
            "id": state["id"],
            "name": result["name"],
            "mobile_number": result["mobile_number"],
            "email": result["email"],
            "linkedin_url": result["linkedin_url"]
        }
    }


def get_skills(state: OverallState):
    """
    Extract technical and soft skills.
    """

    resume = state["user_input"]["resume_content"]

    # TODO: Call your extraction service.

    parser = JsonOutputParser(pydantic_object=get_skills_output)
        
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_skills_prompt),
        ("user", "Resume: {input}")
    ])
    
        # Create the chain that guarantees JSON output
    chain = prompt | llm_service | parser
    
    result = chain.invoke({"input": resume})
    print(json.dumps(result, indent=2))
    

    return {
        "graph_output": {
            "technical_skills": result["technical_skills"],
            "soft_skills": result["soft_skills"]
        }
    }


def get_domain_skills(state: OverallState):
    """
    Extract domain-specific technologies and tools.
    """

    resume = state["user_input"]["resume_content"]

    # TODO: Call your extraction service.

    parser = JsonOutputParser(pydantic_object=get_technical_skills_output)
            
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", domain_skills_prompt),
        ("user", "Resume: {input}")
    ])
        
            # Create the chain that guarantees JSON output
    chain = prompt | llm_service | parser
        
    result = chain.invoke({"input": resume})
    print(json.dumps(result, indent=2))


    return {
        "graph_output": {
            "tech_stacks": result["tech_stacks"],
            "tools_and_platforms": result["tools_and_platforms"]
        }
    }


def get_academic_details(state: OverallState):
    """
    Extract education and coursework.
    """

    resume = state["user_input"]["resume_content"]

    # TODO: Call your extraction service.

    parser = JsonOutputParser(pydantic_object=academic_skills_output)
                
            
    prompt = ChatPromptTemplate.from_messages([
        ("system", academic_details_prompt),
        ("user", "Resume: {input}")
    ])
            
    
    chain = prompt | llm_service | parser
            
    result = chain.invoke({"input": resume})
    print(json.dumps(result, indent=2))

    return {
        "graph_output": {
            "education": result["education"],
            "coursework": result["coursework"]
        }
    }


def get_professional_details(state: OverallState):
    """
    Extract professional experience and achievements.
    """

    resume = state["user_input"]["resume_content"]

    # TODO: Call your extraction service.

    parser = JsonOutputParser(pydantic_object=get_professional_details_output)
                
            
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_professional_details_prompt),
        ("user", "Resume: {input}")
    ])
            

    chain = prompt | llm_service | parser
            
    result = chain.invoke({"input": resume})
    print(json.dumps(result, indent=2))

    return {
        "graph_output": {
            "work_experience": result["work_experience"],
            "achievements": result["achievements"],
            "certifications": result["certifications"]
        }
    }
