from uuid import uuid4
from fastapi import UploadFile
from pathlib import Path
from slugify import slugify

UPLOAD_DIR=Path("media")
UPLOAD_DIR.mkdir(exist_ok=True)

def generate_slug(text:str):
    return slugify(text)

async def save_upload_file(upload_file: UploadFile, sub_dir: str):
    # Check if upload_file is actually an UploadFile object and has a filename
    if not upload_file or not getattr(upload_file, 'filename', None):
        return None
    
    ext = Path(upload_file.filename).suffix
    filename = f"{uuid4().hex}{ext}"
    
    # Ensure sub-directory exists
    dir_path = UPLOAD_DIR / sub_dir
    dir_path.mkdir(parents=True, exist_ok=True) 
    
    file_path = dir_path / filename

    content = await upload_file.read()
    with file_path.open("wb") as f:
        f.write(content)
        
    # Return as a string for the database (e.g., "media/images/abc.jpg")
    return str(file_path).replace("\\", "/")