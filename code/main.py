import json
import base64
import os
import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import subprocess

VERSION = 0.2

app = FastAPI(debug=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/alpr")
async def alpr(payload: Dict[Any, Any]):
    try:
        base64Data = payload.get("base64")
        jpegData = base64.b64decode(base64Data)

        country = payload.get("country")
        procid = payload.get("procid")

        imgFilename = os.path.join(UPLOAD_FOLDER, f"pimg_{procid}.jpg")
        with open(imgFilename, "wb") as f:
            f.write(jpegData)

        osProc = subprocess.Popen(
            ['/usr/bin/alpr', '-c', country, '-n', '1', '-j', imgFilename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = osProc.communicate()

        if osProc.returncode == 0:
            try:
                if os.path.exists(imgFilename):
                    os.remove(imgFilename)

                return json.loads(stdout)
            except:
                return {"status": False, "results": []}
        else:
            return {"status": False}
    except:
        return {"status": False, "results": []}

@app.get("/check")
async def check():
    return {"status": "OK"}

@app.get("/version")
async def version():
    return {"versions": str(VERSION)}