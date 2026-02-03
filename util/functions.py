from flask import request
import json
from util.logger import log
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app_config import UPLOAD_DIR
import re


def extract_payload():
    if request.method == 'GET':
        return request.args.to_dict()

    content_type = request.headers.get('Content-Type', '')
    log.info(f"📥 Content-Type: {content_type}")

    if 'application/json' in content_type:
        data = request.get_json(force=True)
        if isinstance(data, dict):
            return data
        else:
            log.info("⚠️ JSON не распарсен, пробуем вручную")
            try:
                return json.loads(request.data.decode('utf-8'))
            except Exception as e:
                log.info(f"❌ Ошибка при ручном JSON-декодировании: {e}" )
                return {}
    elif 'application/x-www-form-urlencoded' in content_type:
        return request.form.to_dict()
    else:
        log.info(f"⚠️ Неизвестный Content-Type: {content_type}, пробуем как JSON")
        try:
            return json.loads(request.data.decode('utf-8'))
        except Exception:
            return {}




def sanitize_filename(name: str) -> str:
    # Разрешаем кириллицу, латиницу, цифры, пробелы, дефис, подчёркивание, точку
    name = re.sub(r'[^0-9A-Za-zА-Яа-яЁё ._-]', '', name)
    return name.strip()
        

def upload_files(rfbn_id, files):
    yr = datetime.now().year
    UPLOAD_PATH = f"{UPLOAD_DIR}/{yr}/{rfbn_id}"

    os.makedirs(UPLOAD_PATH, exist_ok=True)

    # files = files.getlist("photo_report")
    list_path = []
    for f in files:
        if f.filename:
            filename = sanitize_filename(f.filename)
            path = os.path.join(UPLOAD_PATH, filename)
            list_path.append(path)
            f.save(path)
    return list_path
