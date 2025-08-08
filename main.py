from modules import config_handler, excel_handler, ai_handler, file_handler
import sys
import json

def main():
    print("--- Starting AI Job Assistant ---")

    # الخطوة 1: قراءة الإعدادات والأوامر والسيرة الذاتية
    try:
        config = config_handler.load_config()
        prompts = ai_handler.load_prompts()
        
        excel_path = config['PATHS']['EXCEL_FILE_PATH']
        master_cv_path = config['PATHS']['MASTER_CV_PATH']
        openai_api_key = config['API_KEYS']['OPENAI_API_KEY']
        
        cv_content = file_handler.read_text_file(master_cv_path)
    except Exception as e:
        print(f"Fatal Error: Could not complete initial setup. {e}", file=sys.stderr)
        sys.exit(1)
        
    if 'YOUR_OPENAI_API_KEY_HERE' in openai_api_key or not openai_api_key:
        print("Fatal Error: Please set your OpenAI API key in 'config.ini'.", file=sys.stderr)
        sys.exit(1)

    # الخطوة 2: قراءة ملف الإكسل
    try:
        jobs_df = excel_handler.read_excel_file(excel_path)
    except Exception as e:
        print(f"Fatal Error: Could not read the Excel file. {e}", file=sys.stderr)
        sys.exit(1)

    # الخطوة 3: فلترة الصفوف
    pending_jobs_df = jobs_df[jobs_df['Status'].str.lower() == 'pending'].copy()
    if pending_jobs_df.empty:
        print("\nNo jobs with 'Pending' status found. Exiting.")
        sys.exit(0)
    print(f"\nFound {len(pending_jobs_df)} job(s) with 'Pending' status. Starting process...\n")

    # --- بداية منطق المعالجة ---
    for index, row in pending_jobs_df.iterrows():
        print(f"--- Processing Job: {row['Job Title']} at {row['Company']} ---")
        
        # استخراج المهارات (كما كان في السابق)
        job_description = row['Job Description']
        if not isinstance(job_description, str) or not job_description.strip():
            print("  > Skipping due to empty Job Description.")
            continue
            
        extracted_skills = ai_handler.extract_skills_from_description(openai_api_key, job_description, prompts)
        if not extracted_skills:
            print("  > Could not extract skills. Skipping email generation for this job.")
            continue
        
        tech_skills_str = ", ".join(extracted_skills.get('technical_skills', []))
        soft_skills_str = ", ".join(extracted_skills.get('soft_skills', []))
        jobs_df.loc[index, 'Technical Skills'] = tech_skills_str
        jobs_df.loc[index, 'Soft Skills'] = soft_skills_str
        print(f"  > Skills extracted successfully.")
            
        # --- بداية المنطق الجديد للتعامل مع عدة أشخاص ---
        contact_persons = [p.strip() for p in str(row.get('Contact Person', '')).split(',') if p.strip()]
        contact_emails = [e.strip() for e in str(row.get('Contact Email', '')).split(',') if e.strip()]

        if not contact_persons or not contact_emails:
            print("  > No contact person or email found. Skipping email generation.")
            continue

        if len(contact_persons) != len(contact_emails):
            print(f"  > Warning: Mismatch between number of contact persons ({len(contact_persons)}) and emails ({len(contact_emails)}). Skipping email generation for this row.")
            continue
            
        generated_emails_list = []
        for i, person_name in enumerate(contact_persons):
            person_email = contact_emails[i]
            print(f"  > Generating email for: {person_name} ({person_email})")
            
            job_details_for_prompt = {
                "contact_person": person_name,
                "job_title": row['Job Title'],
                "company_name": row['Company'],
                "job_description": job_description[:1500],
                "technical_skills": tech_skills_str,
                "cv_content": cv_content
            }
            
            generated_email = ai_handler.generate_email(openai_api_key, job_details_for_prompt, prompts)
            if generated_email:
                generated_emails_list.append(generated_email)
            else:
                print(f"    > Failed to generate email for {person_name}.")

        if generated_emails_list:
            # نحفظ قائمة الرسائل بالكامل كنص JSON واحد في الخلية
            jobs_df.loc[index, 'Cover Letter/Message'] = json.dumps(generated_emails_list, indent=2, ensure_ascii=False)
            print(f"  > Successfully generated {len(generated_emails_list)} email(s) for {row['Company']}.")
        
        print("-" * 50)

    # الخطوة 4: حفظ التغييرات
    print("\nProcess finished. Saving all changes back to the Excel file...")
    try:
        excel_handler.write_excel_file(jobs_df, excel_path)
    except Exception as e:
        print(f"Fatal Error: Could not save the Excel file. {e}", file=sys.stderr)

    print("\n--- AI Job Assistant finished its run. ---")

if __name__ == "__main__":
    main()

