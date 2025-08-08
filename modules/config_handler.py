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
        # إيقاف البرنامج مع رسالة خطأ واضحة إذا لم يتم العثور على الملف
        raise FileNotFoundError(f"Error: Configuration file not found at '{config_path}'")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # يمكننا إضافة المزيد من عمليات التحقق هنا لاحقاً
    print("Configuration file 'config.ini' loaded successfully.")
    return config