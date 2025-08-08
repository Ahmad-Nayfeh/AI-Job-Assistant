import openai
import json
import yaml
from pydantic import BaseModel, Field, ValidationError
from typing import List

# --- Pydantic Models for Data Validation ---
class Skills(BaseModel):
    technical_skills: List[str] = Field(description="A list of extracted technical skills.")
    soft_skills: List[str] = Field(description="A list of extracted soft skills.")

# ** الإضافة الجديدة: نموذج للتحقق من هيكل البريد الإلكتروني **
class GeneratedEmail(BaseModel):
    subject: str = Field(description="The suggested subject line for the email.")
    body: str = Field(description="The generated body content of the email.")


# --- Helper function to load prompts ---
def load_prompts(file_path='prompts.yaml'):
    """
    يقوم بتحميل الأوامر من ملف YAML.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Prompts file not found at '{file_path}'")
    except Exception as e:
        raise IOError(f"Error reading the prompts file: {e}")


# --- AI interaction functions ---
def extract_skills_from_description(api_key, job_description, prompts):
    # ... (هذه الدالة تبقى كما هي، لا تغيير)
    print("Connecting to OpenAI to extract skills...")
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt_template = prompts['skill_extraction']['user_prompt']
        system_message = prompts['skill_extraction']['system_message']
        formatted_prompt = prompt_template.format(job_description=job_description)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": formatted_prompt}],
            response_format={"type": "json_object"}
        )
        response_content = response.choices[0].message.content
        try:
            validated_skills = Skills.model_validate_json(response_content)
            print("Successfully extracted and validated skills from OpenAI.")
            return validated_skills.model_dump()
        except ValidationError as e:
            print(f"Pydantic Validation Error: The AI response did not match the expected format. {e}")
            return None
    except Exception as e:
        print(f"An error occurred while interacting with OpenAI: {e}")
        return None

# ** الإضافة الجديدة: دالة لإنشاء البريد الإلكتروني **
def generate_email(api_key, job_details, prompts):
    """
    يتصل بـ OpenAI API لإنشاء بريد إلكتروني مخصص.
    """
    print("Connecting to OpenAI to generate email...")
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt_template = prompts['email_generation']['user_prompt']
        system_message = prompts['email_generation']['system_message']

        # تعبئة القالب بكل المعلومات اللازمة
        formatted_prompt = prompt_template.format(**job_details)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": formatted_prompt}],
            response_format={"type": "json_object"}
        )

        response_content = response.choices[0].message.content
        try:
            validated_email = GeneratedEmail.model_validate_json(response_content)
            print("Successfully generated and validated email from OpenAI.")
            return validated_email.model_dump()
        except ValidationError as e:
            print(f"Pydantic Validation Error for email generation: {e}")
            return None
    except Exception as e:
        print(f"An error occurred during email generation with OpenAI: {e}")
        return None
