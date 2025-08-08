from modules import config_handler, excel_handler
import sys

def main():
    """
    الدالة الرئيسية لتشغيل مساعد البحث عن عمل.
    """
    print("--- Starting AI Job Assistant ---")

    # الخطوة 1: قراءة ملف الإعدادات
    try:
        config = config_handler.load_config()
        # استخراج المسار من الإعدادات
        excel_path = config['PATHS']['EXCEL_FILE_PATH']
    except Exception as e:
        # طباعة الخطأ وإيقاف البرنامج إذا فشلت هذه الخطوة
        print(f"Fatal Error: Could not load configuration. {e}", file=sys.stderr)
        sys.exit(1)

    # الخطوة 2: قراءة ملف الإكسل
    try:
        jobs_df = excel_handler.read_excel_file(excel_path)
    except Exception as e:
        print(f"Fatal Error: Could not read the Excel file. {e}", file=sys.stderr)
        sys.exit(1)

    # الخطوة 3: فلترة الصفوف التي تحتاج إلى معالجة
    # .str.lower() لجعل المقارنة غير حساسة لحالة الأحرف (Pending, pending, PENDING)
    # .copy() لتجنب التحذيرات عند تعديل البيانات لاحقاً
    pending_jobs_df = jobs_df[jobs_df['Status'].str.lower() == 'pending'].copy()
    
    if pending_jobs_df.empty:
        print("\nNo jobs with 'Pending' status found. Nothing to process right now.")
        print("Exiting.")
        sys.exit(0)
    
    print(f"\nFound {len(pending_jobs_df)} job(s) with 'Pending' status. Starting process...")
    
    # --- الخطوات التالية (التفاعل مع الذكاء الاصطناعي وإرسال الإيميلات) ستتم إضافتها هنا ---
    
    print("\n--- Process completed ---")


if __name__ == "__main__":
    main()