from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

import os, uuid

app = FastAPI()

os.makedirs("uploads", exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    with open(f"uploads/{name}","wb") as f:
        f.write(await file.read())
    return {"filename": name}

@app.get("/file/{filename}")
async def get_file(filename:str):
    if not os.path.exists(f"uploads/{filename}"):
        raise HTTPException(404,"Not Found")
    return FileResponse(f"uploads/{filename}")

@app.delete("/files/{filename}")
async def delete_file(filename:str):
    if not os.path.exists(f"uploads/{filename}"):
        raise HTTPException(404,"Not Found")
    os.remove(f"uploads/{filename}")
    return{"message": "deleted"}

@app.get("/gallery", response_class=HTMLResponse)
async def gallery():
    files =  os.listdir("uploads")
    imgs = "".join(f'<img src="/file/{f}">' for f in files)
    return f"""
    <style>
    img{{
        width: 150px;
        height: 150px;
        object-fit: cover;
        margin: 5px;
        border-radius: 8px;
    }}
    </style>
    <h2>Gallery({len(files)})</h2>
    {imgs}"""