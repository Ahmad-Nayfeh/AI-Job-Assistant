from modules import config_handler, excel_handler, ai_handler, file_handler, email_handler
import sys
import json
from datetime import datetime

def main():
    """
    The main function to run the AI Job Assistant.
    """
    print("--- Starting AI Job Assistant ---")
    
    # --- 1. Initial Setup & Pre-checks ---
    try:
        config = config_handler.load_config()
        excel_path = config['PATHS']['EXCEL_FILE_PATH']

        # ** NEW: Fail-fast check for Excel file lock **
        if not excel_handler.check_file_writable(excel_path):
            raise PermissionError("The Excel file 'SeekingJobs.xlsx' is currently open or locked. Please close it and run the script again.")

        prompts = ai_handler.load_prompts()
        cv_content = file_handler.read_text_file(config['PATHS']['MASTER_CV_PATH'])
        jobs_df = excel_handler.read_excel_file(excel_path)
        
        print("--- Initial setup completed successfully. ---")
    except Exception as e:
        print(f"FATAL ERROR during setup: {e}", file=sys.stderr)
        sys.exit(1)

    openai_api_key = config['API_KEYS']['OPENAI_API_KEY']
    if 'YOUR_OPENAI_API_KEY_HERE' in openai_api_key or not openai_api_key:
        print("FATAL ERROR: Please set your OpenAI API key in 'config.ini'.", file=sys.stderr)
        sys.exit(1)
        
    changes_made = False
    df_to_process = jobs_df.copy()

    # --- 2. Main Processing Loop ---
    for index, row in df_to_process.iterrows():
        status = str(row.get('Status', '')).strip().lower()

        # --- Process 'Pending' Jobs ---
        if status == 'pending':
            # (The logic for processing 'Pending' jobs remains the same)
            print(f"\n--- [ACTION] Found 'Pending' Job: '{row['Job Title']}' ---")
            changes_made = True
            
            job_description = row.get('Job Description', '')
            extracted_skills = ai_handler.extract_skills_from_description(openai_api_key, job_description, prompts)
            if extracted_skills:
                df_to_process.loc[index, 'Technical Skills'] = ", ".join(extracted_skills.get('technical_skills', []))
                df_to_process.loc[index, 'Soft Skills'] = ", ".join(extracted_skills.get('soft_skills', []))
                print("  [SUCCESS] Skills extracted.")
            
            contacts = [p.strip() for p in row['Contact Person'].split(',') if p.strip()]
            if contacts:
                email_list = []
                for person in contacts:
                    details = {"contact_person": person, "job_title": row['Job Title'], "company_name": row['Company'], "job_description": job_description[:1500], "technical_skills": df_to_process.loc[index, 'Technical Skills'], "cv_content": cv_content}
                    email_content = ai_handler.generate_email(openai_api_key, details, prompts)
                    if email_content: email_list.append(email_content)
                df_to_process.loc[index, 'Cover Letter/Message'] = json.dumps(email_list, indent=2, ensure_ascii=False)
                print(f"  [SUCCESS] Generated {len(email_list)} email(s).")

            automation_mode = config['SETTINGS']['AUTOMATION_MODE'].strip().upper()
            if automation_mode == 'REVIEW':
                df_to_process.loc[index, 'Status'] = 'Ready to Send'
                print("  [STATUS CHANGE] Updated to 'Ready to Send'.")
            elif automation_mode == 'FULL':
                df_to_process.loc[index, 'Status'] = 'Approved'
                print("  [STATUS CHANGE] Updated to 'Approved'.")

        # --- Process 'Approved' Jobs ---
        if df_to_process.loc[index, 'Status'].strip().lower() == 'approved':
            # (The logic for processing 'Approved' jobs remains the same)
            print(f"\n--- [ACTION] Found 'Approved' Job: '{row['Job Title']}' ---")
            changes_made = True
            
            gmail_service = email_handler.get_gmail_service()
            if not gmail_service: continue

            contact_emails = [e.strip() for e in str(row.get('Contact Email', '')).split(',') if e.strip()]
            cover_letters = json.loads(row['Cover Letter/Message'])
            
            sent_at_least_one = False
            for i, email_address in enumerate(contact_emails):
                message = email_handler.create_message_with_attachment(config['SETTINGS']['USER_EMAIL'], email_address, cover_letters[i]['subject'], cover_letters[i]['body'], config['PATHS']['PDF_CV_PATH'])
                if message and email_handler.send_message(gmail_service, 'me', message):
                    sent_at_least_one = True

            if sent_at_least_one:
                df_to_process.loc[index, 'Status'] = 'Applied'
                df_to_process.loc[index, 'Application Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("  [STATUS CHANGE] Updated to 'Applied'.")
            else:
                df_to_process.loc[index, 'Status'] = 'Failed'
                print("  [STATUS CHANGE] Updated to 'Failed'.")

    # --- 3. Save Changes ---
    if changes_made:
        print("\nSaving all changes back to the Excel file...")
        try:
            excel_handler.write_excel_file(df_to_process, excel_path)
        except Exception as e:
            print(f"FATAL ERROR while saving: {e}", file=sys.stderr)
    else:
        print("\nNo jobs with 'Pending' or 'Approved' status found. No changes made.")

    print("\n--- AI Job Assistant finished its run. ---")

if __name__ == "__main__":
    main()
