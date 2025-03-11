from fastapi import FastAPI, File, UploadFile, Query
from typing import Optional
from pydantic import BaseModel
import os
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,FileResponse,HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

COPYFILES_DIR = "./copyfiles"
STATIC_DIR = "/static"

def get_base_url(request: Request) -> str:
    host = request.headers.get("X-Forwarded-Host", request.headers.get("host", "localhost"))
    
    # Проверяем, есть ли порт в `X-Forwarded-Host`
    if ":" in host:
        return f"http://{host}"

    return f"http://{host}"  # Если порта нет, просто возвращаем host



# Логирование
def write_log(message,type_message):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_message = f"{current_datetime} {type_message} {message}"
    with open("./log/diplomprojectlog.txt","a") as log:
        log.write(out_message + "\n")
    log.close()

# Создание папки
def create_folder(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            write_log(f"folder {path} created succesfully", "INFO")
        except FileExistsError:
            write_log(f"folder {path} doesn't created", "ERROR")

create_folder("./log")
create_folder(COPYFILES_DIR)

app = FastAPI()
# Разрешаем фронту взаимодействовать с бэком
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т. д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

@app.get("/debug/headers")
async def debug_headers(request: Request):
    return dict(request.headers)
    
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Скачиваем файлы на сервер
@app.post("/api/files")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_data = await file.read()
    filename = file.filename
    base_name, ext = os.path.splitext(filename)

    file_path1 = os.path.join(COPYFILES_DIR, f"copy1{ext}")
    file_path2 = os.path.join(COPYFILES_DIR, f"copy2{ext}")

    try:
        with open(file_path1, "wb") as f:
            f.write(file_data)
        with open(file_path2, "wb") as f:
            f.write(file_data)
        write_log(f"Files copied: copy1{ext}, copy2{ext}", "INFO")
    except Exception as e:
        write_log(f"Error copying files: {type(e).__name__} - {e}", "ERROR")
        return JSONResponse(content={"error": "Ошибка при загрузке файла"}, status_code=500)

    base_url = get_base_url(request)

    # Формируем корректный URL для скачивания
    download_url = f"{base_url}/api/download?file1=copy1{ext}&file2=copy2{ext}"

    return JSONResponse(content={"download_url": download_url})

@app.get("/api/download", response_class=HTMLResponse)
async def download_page(request: Request, file1: str, file2: str, _nocache: float = Query(default=None)):
    base_url = get_base_url(request)
    home_url = base_url.replace("/api", "")

    # Генерируем ссылки для скачивания файлов
    copy1_url = f"{base_url}/api/files/{file1}?_nocache={_nocache}"
    copy2_url = f"{base_url}/api/files/{file2}?_nocache={_nocache}"

    html_content = f"""
    <html>
    <head>
        <title>Скачивание файлов</title>
        <link rel="stylesheet" href="{base_url}/static/style.css">
    </head>
    <body>
        <a href="{home_url}" class="home-link">🏠 Вернуться на главную</a>
        <div class="download-container">
            <h2>Файл успешно обработан!</h2> 
            <p><a class="download-link" href="{copy1_url}" download>Скачать {file1}</a></p>
            <p><a class="download-link" href="{copy2_url}" download>Скачать {file2}</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# 🔹 Раздача файлов для скачивания
@app.get("/api/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(COPYFILES_DIR, filename)
    if not os.path.isfile(file_path):
        return JSONResponse(content={"error": "Файл не найден"}, status_code=404)

    return FileResponse(
        file_path,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
