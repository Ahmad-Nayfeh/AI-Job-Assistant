
# AI Job Assistant 🤖

A semi-automated job application assistant powered by Python and AI. This tool streamlines the job-seeking process by parsing job descriptions, extracting key skills, generating hyper-personalized HTML cover letters, and automating email outreach through the Gmail API.

This project is designed to transform the repetitive and time-consuming task of applying for jobs into an efficient, strategic, and personalized workflow.

## ✨ Features

- **Interactive UI:** A user-friendly command-line interface that guides you through every step of the process.
    
- **AI-Powered Skill Extraction:** Reads job descriptions to identify the exact technical and soft skills employers are looking for.
    
- **Hyper-Personalized Email Generation:** Creates unique, tailored HTML emails that:
    
    - Mention the company by name and reference its mission from the company description.
        
    - State where you found the job posting (e.g., LinkedIn, Company Website).
        
    - Intelligently "bridges" your specific skills and projects from your CV to the job's requirements.
        
    - Includes a professional, clickable HTML signature with your contact details and links.
        
- **Automated Email Dispatch:** Securely sends application emails with your PDF CV attached directly from the script using the official Gmail API.
    
- **Flexible Workflow:** You are in control. Choose between:
    
    - **`REVIEW` mode:** The AI prepares everything, and you give the final approval in the Excel sheet before sending.
        
    - **`FULL` mode:** A completely automated "fire-and-forget" mode that processes and sends applications in one go.
        
- **Robust & Safe:** Includes comprehensive error handling, fail-fast checks for locked files, and keeps all your sensitive information (API keys, personal details) in a single, local configuration file that is ignored by Git.
    

## 🚀 Getting Started: A Step-by-Step Guide

Follow these steps to get the project running from zero to fully operational.

### Step 1: Clone the Repository

First, clone this repository to your local machine and navigate into the project directory.

```
git clone https://github.com/your-username/AI-Job-Assistant.git
cd AI-Job-Assistant
```

### Step 2: Set Up the Python Environment

It is crucial to use a virtual environment to keep your project dependencies isolated.

```
# Create the virtual environment
python -m venv venv

# Activate the environment on Windows
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

Install all the required Python libraries using the `requirements.txt` file.

```
pip install -r requirements.txt
```

### Step 4: Configure Your Assistant (The Most Important Step)

This project uses several critical files for configuration. You **must** set these up correctly.

#### A. Understanding the Key CV Files

Before configuring the paths, it's important to understand the role of the two CV files:

- **`Master_CV.md` (The AI's Brain 🧠):** This is your detailed, comprehensive master document in Markdown (`.md`) format. It should contain **everything** about your professional life—every project, skill, and course, even minor ones. **Its purpose is to be the single source of truth that the AI reads to find the perfect information for each job.** The Markdown format is simple text, making it extremely easy for the AI to parse.
    
- **`CV.pdf` (The Recruiter's Document 📄):** This is your polished, professionally designed, final CV. It's the visually appealing document that you actually send to recruiters. **Its only purpose is to be the attachment in the email.**
    

In short: the `.md` file is for the AI to read, and the `.pdf` file is for humans to read.

#### B. The `config.ini` File

This file is the control center for the assistant.

1. Find the file named `config.ini.example` in the project directory.
    
2. **Rename it** to `config.ini`.
    
3. Open `config.ini` with a text editor and carefully fill in **all** the required information:
    
    - `[PATHS]`: Provide the correct absolute paths to your `Master_CV.md` and your final `CV.pdf`.
        
    - `[API_KEYS]`: Paste your secret API key from OpenAI.
        
    - `[USER_DETAILS]`: Fill in all your personal details. This information will be used to create your email signature.
        

#### C. The `credentials.json` File (Google API)

This file is required to give the script permission to send emails on your behalf.

1. You must enable the Gmail API for your Google account and download the credentials file.
    
2. Follow the **official Google Cloud guide** to do this. It's a one-time setup.
    
    - **Official Guide:** [Google for Developers - Python Quickstart](https://developers.google.com/gmail/api/quickstart/python "null")
        
    - During the setup, when asked for the "Application type", choose **Desktop app**.
        
3. After following the guide, you will download a file. **Rename this file to `credentials.json`** and place it in the root directory of this project.
    

> **Security Note:** The `.gitignore` file is already configured to ignore `config.ini` and `credentials.json`, so your sensitive information will never be uploaded to GitHub.

## ⚙️ Usage Workflow

Once the setup is complete, using the assistant is a simple, repeatable process.

### 1. Create the Tracker File (First Time Only)

If the `data/SeekingJobs.xlsx` file doesn't exist, run this script once to create it with the correct columns.

```
python 1_create_tracker_file.py
```

### 2. Add Jobs to the Tracker

1. Open the `data/SeekingJobs.xlsx` file.
    
2. Add a new row for each job you want to apply for.
    
3. Fill in the details: `Company`, `Job Title`, `Job Description`, `Contact Person`, etc.
    
4. Most importantly, set the `Status` for all new jobs to **`Pending`**.
    

### 3. Run the Main Script

Execute the main script from your terminal.

```
python main.py
```

The script will then:

1. Welcome you and perform initial checks on your files.
    
2. Report how many `Pending` and `Approved` jobs it found.
    
3. Ask you to choose between `REVIEW` and `FULL` mode.
    
4. Process the jobs according to your choice.
    

Follow the on-screen instructions, and the assistant will handle the rest!

## 🔧 Customization: How to Modify the Email Signature

The system is designed to be easily customizable. If you want to add, remove, or change items in your email signature, it's a simple two-step process.

### Step 1: Edit the Data in `config.ini`

All the personal information is stored in the `[USER_DETAILS]` section of your `config.ini` file.

- **To remove an item (e.g., Portfolio):** Simply delete the entire line `PORTFOLIO_URL = ...`.
    
- **To add a new item (e.g., a Blog):** Add a new line like `BLOG_URL = https://my-blog.com`.
    

### Step 2: Edit the Template in `main.py`

After changing the data, you need to update the simple HTML template that arranges it.

1. Open the `main.py` file.
    
2. Find the function called `create_html_signature`.
    
3. Inside this function, you will see the HTML structure. You can easily edit the text and links.
    

**Example: Removing the portfolio and adding a blog link.**

**Before:**

```
signature = f"""
...
    <a href="{details['PORTFOLIO_URL']}">Portfolio</a> | 
    <a href="{details['LINKEDIN_URL']}">LinkedIn</a> | 
    <a href="{details['GITHUB_URL']}">GitHub</a>
...
"""
```

**After:**

```
signature = f"""
...
    <a href="{details['LINKEDIN_URL']}">LinkedIn</a> | 
    <a href="{details['GITHUB_URL']}">GitHub</a> |
    <a href="{details['BLOG_URL']}">My Blog</a>
...
"""
```

Just save the file, and the next time you run the script, it will use your new custom signature.