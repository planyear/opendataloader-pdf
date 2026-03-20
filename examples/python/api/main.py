import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response

from opendataloader_pdf import convert

app = FastAPI(title="opendataloader-pdf API")


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!doctype html>
    <html>
    <head><title>opendataloader-pdf</title></head>
    <body>
      <h2>Upload a PDF to convert to Markdown</h2>
      <form action="/convert" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf" required />
        <button type="submit">Convert &amp; Download</button>
      </form>
    </body>
    </html>
    """


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / file.filename
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with input_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            convert(
                input_path=str(input_path),
                output_dir=str(output_dir),
                format="markdown",
                quiet=True,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        md_files = list(output_dir.glob("*.md"))
        if not md_files:
            raise HTTPException(status_code=500, detail="No markdown output was generated.")

        stem = Path(file.filename).stem
        content = md_files[0].read_bytes()

    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{stem}.md"'},
    )
