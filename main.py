from modules import config_handler, excel_handler, ai_handler, file_handler, email_handler
import sys
import json
from datetime import datetime

def main():
    """
    الدالة الرئيسية لتشغيل مساعد البحث عن عمل.
    """
    print("--- Starting AI Job Assistant ---")
    
    # --- 1. الإعداد الأولي ---
    try:
        config = config_handler.load_config()
        prompts = ai_handler.load_prompts()
        cv_content = file_handler.read_text_file(config['PATHS']['MASTER_CV_PATH'])
        jobs_df = excel_handler.read_excel_file(config['PATHS']['EXCEL_FILE_PATH'])
    except Exception as e:
        print(f"Fatal Error during setup: {e}", file=sys.stderr)
        sys.exit(1)

    # التحقق من مفتاح الـ API
    openai_api_key = config['API_KEYS']['OPENAI_API_KEY']
    if 'YOUR_OPENAI_API_KEY_HERE' in openai_api_key or not openai_api_key:
        print("Fatal Error: Please set your OpenAI API key in 'config.ini'.", file=sys.stderr)
        sys.exit(1)
        
    # متغير لتتبع ما إذا كانت هناك تغييرات لحفظها
    changes_made = False
    
    # --- 2. الحلقة الرئيسية لمعالجة كل صف في الجدول ---
    for index, row in jobs_df.iterrows():
        status = str(row.get('Status', '')).strip().lower()

        # --- معالجة الوظائف المعلقة (Pending) ---
        if status == 'pending':
            print(f"\n--- Found 'Pending' Job: {row['Job Title']} at {row['Company']} ---")
            changes_made = True # سيتم إجراء تغييرات
            
            # أ. استخراج المهارات
            job_description = row.get('Job Description', '')
            extracted_skills = ai_handler.extract_skills_from_description(openai_api_key, job_description, prompts)
            if not extracted_skills:
                print("  > Could not extract skills. Skipping this job.")
                continue

            tech_skills_str = ", ".join(extracted_skills.get('technical_skills', []))
            soft_skills_str = ", ".join(extracted_skills.get('soft_skills', []))
            jobs_df.loc[index, 'Technical Skills'] = tech_skills_str
            jobs_df.loc[index, 'Soft Skills'] = soft_skills_str
            print("  > Skills extracted successfully.")

            # ب. إنشاء البريد الإلكتروني
            contact_persons = [p.strip() for p in str(row.get('Contact Person', '')).split(',') if p.strip()]
            if not contact_persons:
                print("  > No contact person found. Skipping email generation.")
                continue

            email_list = []
            for person in contact_persons:
                details = {"contact_person": person, "job_title": row['Job Title'], "company_name": row['Company'], "job_description": job_description[:1500], "technical_skills": tech_skills_str, "cv_content": cv_content}
                email_content = ai_handler.generate_email(openai_api_key, details, prompts)
                if email_content:
                    email_list.append(email_content)
            
            jobs_df.loc[index, 'Cover Letter/Message'] = json.dumps(email_list, indent=2, ensure_ascii=False)
            print(f"  > Generated {len(email_list)} email(s).")
            
            # ج. تحديث الحالة بناءً على وضع التشغيل
            automation_mode = config['SETTINGS']['AUTOMATION_MODE'].upper()
            if automation_mode == 'REVIEW':
                jobs_df.loc[index, 'Status'] = 'Ready to Send'
                print("  > Status changed to 'Ready to Send'.")
            elif automation_mode == 'FULL':
                jobs_df.loc[index, 'Status'] = 'Approved'
                print("  > Status changed to 'Approved' for immediate sending.")
        
        # --- معالجة الوظائف المعتمدة (Approved) ---
        # سيتم تشغيل هذا الجزء في نفس الدورة إذا كان الوضع FULL، أو في دورة لاحقة إذا كان REVIEW
        if jobs_df.loc[index, 'Status'].strip().lower() == 'approved':
            print(f"\n--- Found 'Approved' Job: {row['Job Title']} at {row['Company']} ---")
            changes_made = True # سيتم إجراء تغييرات
            
            # الحصول على خدمة Gmail (سيطلب المصادقة في المرة الأولى)
            gmail_service = email_handler.get_gmail_service()
            if not gmail_service:
                print("  > Could not get Gmail service. Aborting email sending.")
                continue

            # إرسال الإيميلات
            contact_emails = [e.strip() for e in str(row.get('Contact Email', '')).split(',') if e.strip()]
            cover_letters = json.loads(row['Cover Letter/Message'])
            
            sent_at_least_one = False
            for i, email_address in enumerate(contact_emails):
                email_content = cover_letters[i]
                message = email_handler.create_message_with_attachment(config['SETTINGS']['USER_EMAIL'], email_address, email_content['subject'], email_content['body'], config['PATHS']['PDF_CV_PATH'])
                if message and email_handler.send_message(gmail_service, 'me', message):
                    sent_at_least_one = True

            if sent_at_least_one:
                jobs_df.loc[index, 'Status'] = 'Applied'
                jobs_df.loc[index, 'Application Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print("  > Status changed to 'Applied'.")
            else:
                jobs_df.loc[index, 'Status'] = 'Failed'
                print("  > Status changed to 'Failed'.")

    # --- 3. حفظ التغييرات ---
    if changes_made:
        print("\nSaving all changes back to the Excel file...")
        try:
            excel_handler.write_excel_file(jobs_df, config['PATHS']['EXCEL_FILE_PATH'])
        except Exception as e:
            print(f"Fatal Error: Could not save the Excel file. {e}", file=sys.stderr)
    else:
        print("\nNo jobs found with 'Pending' or 'Approved' status. No changes made.")

    print("\n--- AI Job Assistant finished its run. ---")

if __name__ == "__main__":
    main()
