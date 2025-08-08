from modules import config_handler, excel_handler, ai_handler, file_handler, email_handler, ui_handler
import sys
import json
import os
from datetime import datetime

def create_html_signature(config):
    """
    Creates a reusable HTML signature string from the config file details.
    """
    try:
        details = config['USER_DETAILS']
        signature = f"""
        <p style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc;">
            <b style="font-size: 1.1em;">{details['FULL_NAME']}</b><br>
            {details['PHONE_NUMBER']}<br><br>
            <a href="{details['PORTFOLIO_URL']}" style="text-decoration: none; color: #007bff;">Portfolio</a> | 
            <a href="{details['LINKEDIN_URL']}" style="text-decoration: none; color: #007bff;">LinkedIn</a> | 
            <a href="{details['GITHUB_URL']}" style="text-decoration: none; color: #007bff;">GitHub</a>
        </p>
        """
        return signature
    except KeyError as e:
        raise KeyError(f"Missing key in [USER_DETAILS] section of config.ini: {e}")

def initial_checks(config):
    """
    Performs initial checks for required files and folders.
    Returns the DataFrame if successful, otherwise None.
    """
    excel_path = config['PATHS']['EXCEL_FILE_PATH']
    data_dir = os.path.dirname(excel_path)

    if not os.path.exists(data_dir):
        ui_handler.print_error(f"The data directory '{data_dir}' does not exist.")
        ui_handler.print_info("Please create it, or run '1_create_tracker_file.py' to generate it automatically.")
        return None

    if not os.path.exists(excel_path):
        ui_handler.print_error(f"The Excel file '{excel_path}' does not exist in the data directory.")
        ui_handler.print_info("Please run '1_create_tracker_file.py' to generate it.")
        return None
    
    if not excel_handler.check_file_writable(excel_path):
        ui_handler.print_error("The Excel file 'SeekingJobs.xlsx' is currently open or locked.")
        ui_handler.print_info("Please close it and run the script again.")
        return None
        
    jobs_df = excel_handler.read_excel_file(excel_path)
    if jobs_df.empty:
        ui_handler.print_warning("The Excel file is empty.")
        ui_handler.print_info("Please add at least one job application with the status 'Pending' to get started.")
        return None
        
    return jobs_df

def main():
    ui_handler.print_header("AI Job Assistant")
    
    # --- 1. Initial Setup & Checks ---
    try:
        config = config_handler.load_config()
        jobs_df = initial_checks(config)
        if jobs_df is None:
            sys.exit(1) # Exit if checks fail

        prompts = ai_handler.load_prompts()
        cv_content = file_handler.read_text_file(config['PATHS']['MASTER_CV_PATH'])
        html_signature = create_html_signature(config)
        openai_api_key = config['API_KEYS']['OPENAI_API_KEY']
    except Exception as e:
        ui_handler.print_error(f"An error occurred during setup: {e}")
        sys.exit(1)

    # --- 2. User Interaction & Mode Selection ---
    pending_count = len(jobs_df[jobs_df['Status'].str.lower() == 'pending'])
    approved_count = len(jobs_df[jobs_df['Status'].str.lower() == 'approved'])

    ui_handler.print_subheader("Current Tracker Status")
    ui_handler.print_info(f"Found {pending_count} job(s) with 'Pending' status.")
    ui_handler.print_info(f"Found {approved_count} job(s) with 'Approved' status.")

    if pending_count == 0 and approved_count == 0:
        ui_handler.print_warning("No jobs to process. Please set a job's status to 'Pending' or 'Approved'.")
        sys.exit(0)

    chosen_mode = ui_handler.get_user_choice(config['SETTINGS']['AUTOMATION_MODE'])
    
    # --- 3. Main Processing Loop ---
    changes_made = False
    df_to_process = jobs_df.copy()

    for index, row in df_to_process.iterrows():
        status = str(row.get('Status', '')).strip().lower()

        if status == 'pending':
            ui_handler.print_subheader(f"Processing 'Pending' Job: '{row['Job Title']}'")
            changes_made = True
            
            job_description = row.get('Job Description', '')
            extracted_skills = ai_handler.extract_skills_from_description(openai_api_key, job_description, prompts)
            if extracted_skills:
                df_to_process.loc[index, 'Technical Skills'] = ", ".join(extracted_skills.get('technical_skills', []))
                df_to_process.loc[index, 'Soft Skills'] = ", ".join(extracted_skills.get('soft_skills', []))
                ui_handler.print_success("Skills extracted.")
            
            contacts = [p.strip() for p in row['Contact Person'].split(',') if p.strip()]
            if contacts:
                email_list = []
                for person in contacts:
                    details = {"contact_person": person, "job_title": row['Job Title'], "company_name": row['Company'], "platform": row['Platform'], "company_description": row['Company Description'], "job_description": job_description[:1500], "technical_skills": df_to_process.loc[index, 'Technical Skills'], "soft_skills": df_to_process.loc[index, 'Soft Skills'], "cv_content": cv_content}
                    email_content = ai_handler.generate_email(openai_api_key, details, prompts)
                    if email_content:
                        full_email_body = email_content['body'] + html_signature
                        email_list.append({"subject": email_content['subject'], "body": full_email_body})
                
                if email_list:
                    df_to_process.loc[index, 'Cover Letter/Message'] = json.dumps(email_list, indent=2, ensure_ascii=False)
                    ui_handler.print_success(f"Generated {len(email_list)} email(s).")

            if chosen_mode == 'REVIEW':
                df_to_process.loc[index, 'Status'] = 'Ready to Send'
                ui_handler.print_success("Status updated to 'Ready to Send'.")
            elif chosen_mode == 'FULL':
                df_to_process.loc[index, 'Status'] = 'Approved'
                ui_handler.print_success("Status updated to 'Approved' for immediate sending.")

        if df_to_process.loc[index, 'Status'].strip().lower() == 'approved':
            ui_handler.print_subheader(f"Processing 'Approved' Job: '{row['Job Title']}'")
            changes_made = True
            
            contact_emails = [e.strip() for e in str(row.get('Contact Email', '')).split(',') if e.strip()]
            message_content = row.get('Cover Letter/Message', '')

            if not contact_emails or not message_content:
                df_to_process.loc[index, 'Status'] = 'Failed'
                ui_handler.print_warning("Skipping email dispatch due to missing contact email or message content.")
                continue

            gmail_service = email_handler.get_gmail_service()
            if not gmail_service: continue

            try:
                cover_letters = json.loads(message_content)
                if len(contact_emails) != len(cover_letters):
                    df_to_process.loc[index, 'Status'] = 'Failed'
                    continue
            except json.JSONDecodeError:
                df_to_process.loc[index, 'Status'] = 'Failed'
                continue

            sent_at_least_one = False
            for i, email_address in enumerate(contact_emails):
                sender_email = config['USER_DETAILS']['EMAIL']
                message = email_handler.create_message_with_attachment(sender_email, email_address, cover_letters[i]['subject'], cover_letters[i]['body'], config['PATHS']['PDF_CV_PATH'])
                
                if message and email_handler.send_message(gmail_service, 'me', message):
                    sent_at_least_one = True

            if sent_at_least_one:
                df_to_process.loc[index, 'Status'] = 'Applied'
                df_to_process.loc[index, 'Application Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ui_handler.print_success("Email(s) sent. Status updated to 'Applied'.")
            else:
                df_to_process.loc[index, 'Status'] = 'Failed'
                ui_handler.print_error("Email sending failed. Status updated to 'Failed'.")

    # --- 4. Save Changes ---
    if changes_made:
        ui_handler.print_subheader("Saving Changes")
        try:
            excel_handler.write_excel_file(df_to_process, config['PATHS']['EXCEL_FILE_PATH'])
            ui_handler.print_success("All changes have been saved to the Excel file.")
        except Exception as e:
            ui_handler.print_error(f"An unexpected error occurred while saving the file: {e}")
    else:
        ui_handler.print_info("No changes were made in this run.")

    ui_handler.print_header("AI Job Assistant Finished")

if __name__ == "__main__":
    main()
