from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import whisper
import shutil
import os

model = whisper.load_model("small")  # "tiny", "base", "small", "medium", "large"
transcriberouter = APIRouter()

@transcriberouter.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Simpan file sementara
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Proses dengan whisper
    result = model.transcribe(temp_file, language="en")

    # Hapus file setelah transkripsi
    os.remove(temp_file)

    return {"text": result["text"]}
