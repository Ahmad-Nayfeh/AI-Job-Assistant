import pandas as pd
import os

def read_excel_file(file_path):
    """
    تقوم بقراءة ملف الإكسل وتحويله إلى pandas DataFrame.

    Args:
        file_path (str): مسار ملف الإكسل.

    Returns:
        pd.DataFrame: جدول البيانات.

    Raises:
        FileNotFoundError: إذا لم يتم العثور على الملف.
        IOError: في حالة حدوث خطأ أثناء القراءة.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Excel tracker file not found at '{file_path}'")
    
    try:
        # قراءة الملف
        df = pd.read_excel(file_path)
        print(f"Excel file '{file_path}' loaded successfully. Found {len(df)} rows.")
        return df
    except Exception as e:
        raise IOError(f"An error occurred while reading the Excel file: {e}")

def write_excel_file(df, file_path):
    """
    تقوم بحفظ الـ DataFrame المحدث مرة أخرى في ملف الإكسل.

    Args:
        df (pd.DataFrame): الجدول المحدث.
        file_path (str): مسار ملف الإكسل.
    
    Raises:
        IOError: في حالة حدوث خطأ أثناء الكتابة.
    """
    try:
        # حفظ الملف بدون إضافة عمود الفهرس
        df.to_excel(file_path, index=False)
        print(f"Successfully saved changes to '{file_path}'.")
    except Exception as e:
        raise IOError(f"An error occurred while writing to the Excel file: {e}")