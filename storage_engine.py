import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_document(file):
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)
    return path
