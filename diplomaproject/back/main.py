from fastapi import FastAPI, File, UploadFile, Query
from typing import Optional
from pydantic import BaseModel
import os
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,FileResponse,HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

COPYFILES_DIR = "./copyfiles"

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
    "http://192.168.31.77:5500" # укажите ip:порт вашего фроненд сервера
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т. д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Скачиваем файлы на сервер
@app.post("/files")
async def upload_file(file: UploadFile = File(...)):
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
        write_log(f"Files was copy: copy1{ext}, copy2{ext}", "INFO")
    except Exception as e:
        write_log(f"Error while files copy: {type(e).__name__} - {e}", "ERROR")
        return {"error": "Ошибка при загрузке файла"}

    # Возвращаем JSON с URL
    return JSONResponse(content={"download_url": f"http://localhost:8000/download?file1=copy1{ext}&file2=copy2{ext}"})

app.mount("/static", StaticFiles(directory="static"), name="static") # маунт стилей

# Страница скачивания файлов
@app.get("/download", response_class=FileResponse)
async def download_page(file1: str, file2: str, _nocache: float = Query(default=None)):
    copy1_url = f"http://192.168.31.77:8000/files/{file1}?_nocache={_nocache}"
    copy2_url = f"http://192.168.31.77:8000/files/{file2}?_nocache={_nocache}"

# Не забудьте указать ваш фронтенд сервер в <a href
    html_content = f"""
    <html>
    <head>
        <title>Скачивание файлов</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <a href="http://192.168.31.77:5500/index.html" class="home-link">🏠 Вернуться на главную</a>
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
@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(COPYFILES_DIR, filename)
    if not os.path.isfile(file_path):
        return {"error": "Файл не найден"}

    return FileResponse(
        file_path,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
