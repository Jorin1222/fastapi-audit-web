
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from utils import parse_html
import re

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def format_thousands(val):
    if isinstance(val, (int, float)):
        return f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
    return val

templates.env.filters["format_thousands"] = format_thousands

def extract_number_from_filename(filename):
    m = re.search(r"(\d+)", filename)
    return int(m.group(1)) if m else 9999

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(request: Request, files: list[UploadFile]):
    results = []
    for file in files:
        parsed = parse_html(await file.read())
        parsed["檔名"] = file.filename
        # 預防公司名稱不存在時 fallback
        parsed["公司名稱"] = parsed.get("公司名稱", file.filename)
        results.append(parsed)

    # 依檔名中的數字排序
    results.sort(key=lambda x: extract_number_from_filename(x["檔名"]))

    df = pd.DataFrame(results)
    df.to_excel("result.xlsx", index=False)
    return templates.TemplateResponse("index.html", {"request": request, "results": results})

@app.get("/download")
async def download_excel():
    return FileResponse("result.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="result.xlsx")
