from uuid import uuid4

def recipe_image_file_path(instance, file_name):
    """Generate file name with uuid"""
    ext = file_name.split('.')[-1]
    file_name = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/recipe', file_name)

def get_filename(filename, request):
    print(filename)
    return filename.upper()