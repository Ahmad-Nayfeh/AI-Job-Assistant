def read_text_file(file_path):
    """
    يقرأ محتوى ملف نصي ويعيده كنص واحد.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Text file not found at '{file_path}'")
    except Exception as e:
        raise IOError(f"Error reading text file: {e}")