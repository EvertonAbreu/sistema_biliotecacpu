from supabase import create_client
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")  # ex: https://xxxx.supabase.co
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")  # sb_secret_xxx

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "livros"  # nome do bucket no Supabase Storage

def upload_pdf(file_obj, filename):
    """
    Upload do PDF para o Supabase Storage e retorna URL pública.
    """
    # Upload
    response = supabase.storage.from_(BUCKET_NAME).upload(filename, file_obj)
    if response.get("error"):
        raise Exception(response["error"])
    
    # Retorna URL pública
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
    return public_url