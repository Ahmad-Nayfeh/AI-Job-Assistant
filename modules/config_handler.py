import configparser
import os

def load_config(config_path='config.ini'):
    """
    تقوم هذه الدالة بقراءة ملف الإعدادات والتحقق من وجوده.
    
    Args:
        config_path (str): مسار ملف الإعدادات.

    Returns:
        configparser.ConfigParser: كائن يحتوي على جميع الإعدادات.
    
    Raises:
        FileNotFoundError: إذا لم يتم العثور على ملف الإعدادات.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Error: Configuration file not found at '{config_path}'")
    
    config = configparser.ConfigParser()
    
    # --- هذا هو السطر الذي تم تعديله ---
    # لقد أضفنا ترميز UTF-8 بشكل صريح لضمان قراءة صحيحة على ويندوز
    config.read(config_path, encoding='utf-8')
    # --- نهاية التعديل ---
    
    print("Configuration file 'config.ini' loaded successfully.")
    return config

