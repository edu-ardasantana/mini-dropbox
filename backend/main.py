from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

minio_client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="admin123",
    secure=False
)

BUCKET_NAME = "arquivos"

# Garante que o bucket exista
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Faz upload de um arquivo para o MinIO"""
    try:
        content = await file.read()
        stream = BytesIO(content) 

        minio_client.put_object(
            BUCKET_NAME,
            file.filename,
            data=stream,             
            length=len(content),
            content_type=file.content_type
        )
        return {"message": f"{file.filename} enviado com sucesso!"}
    except Exception as e:
        print("Erro ao enviar:", e)
        return {"error": str(e)}


@app.get("/files")
def list_files():
    """Lista os arquivos do bucket"""
    try:
        objects = minio_client.list_objects(BUCKET_NAME)
        files = [obj.object_name for obj in objects]
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}


@app.get("/download/{filename}")
def download(filename: str):
    """Baixa o arquivo especificado"""
    try:
        temp_path = f"temp_{filename}"
        minio_client.fget_object(BUCKET_NAME, filename, temp_path)
        return FileResponse(temp_path, filename=filename)
    except Exception as e:
        return {"error": str(e)}
