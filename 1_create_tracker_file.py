# 1_create_tracker_file.py

import pandas as pd
import os

# --- الإعدادات الرئيسية ---
# اسم المجلد الذي سيحتوي على ملف البيانات
DATA_DIR = "data"
# اسم ملف الإكسل
FILE_NAME = "SeekingJobs.xlsx"
# المسار الكامل للملف
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

# قائمة الأعمدة المتفق عليها بالترتيب النهائي
COLUMNS = [
    'Status',
    'Application Date',
    'Company',
    'Job Title',
    'Platform',
    'Location',
    'Job Description',
    'Company Description',
    'Technical Skills',
    'Soft Skills',
    'Contact Person',
    'Contact Email',
    'Cover Letter/Message'
]

def create_tracker_file():
    """
    هذه الدالة تقوم بإنشاء ملف إكسل لتتبع الوظائف إذا لم يكن موجوداً.
    """
    print("Starting the script...")

    # الخطوة 1: التحقق من وجود مجلد البيانات، وإنشاؤه إذا لم يكن موجوداً
    # هذا يضمن أن الكود منظم ويعمل بشكل صحيح
    if not os.path.exists(DATA_DIR):
        print(f"Data directory '{DATA_DIR}' not found. Creating it...")
        os.makedirs(DATA_DIR)
        print(f"Directory '{DATA_DIR}' created successfully.")

    # الخطوة 2: التحقق مما إذا كان ملف الإكسل موجوداً بالفعل
    if os.path.exists(FILE_PATH):
        print(f"File '{FILE_PATH}' already exists.")
        print("No new file was created.")
        return

    # الخطوة 3: إذا لم يكن الملف موجوداً، قم بإنشائه
    print(f"File '{FILE_PATH}' not found. Creating a new tracker file...")
    
    # إنشاء DataFrame فارغ باستخدام الأعمدة المحددة
    # DataFrame هو الهيكل الأساسي للجدول في مكتبة Pandas
    df = pd.DataFrame(columns=COLUMNS)
    
    # الخطوة 4: حفظ الـ DataFrame كملف إكسل
    try:
        # index=False تمنع إضافة عمود إضافي للفهرس في ملف الإكسل
        df.to_excel(FILE_PATH, index=False)
        print("-" * 50)
        print(f"Successfully created the Excel file at: {FILE_PATH}")
        print("The file contains the following columns:")
        for col in COLUMNS:
            print(f"- {col}")
        print("-" * 50)
    except Exception as e:
        print(f"An error occurred while creating the file: {e}")

if __name__ == "__main__":
    # هذه هي نقطة انطلاق البرنامج
    # الكود داخل هذا الشرط يعمل فقط عند تشغيل الملف مباشرة
    create_tracker_file()

