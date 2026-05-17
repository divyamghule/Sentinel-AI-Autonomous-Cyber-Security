from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path

from sentinel_ai.prevention.scanner import scan_url, scan_file_temp, scan_text, stats

app = FastAPI(title="Sentinel AI API")
TMP = Path("./tmp_uploads")
TMP.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan/url")
async def scan_url_endpoint(url: str = Form(...)):
    res = scan_url(url)
    return JSONResponse(res)


@app.post("/scan/file")
async def scan_file_endpoint(file: UploadFile = File(...)):
    dest = TMP / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    res = scan_file_temp(dest)
    return JSONResponse(res)


@app.post("/scan/text")
async def scan_text_endpoint(text: str = Form(...)):
    res = scan_text(text)
    return JSONResponse(res)


@app.get("/stats")
def get_stats():
    return stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
