from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
import random
import uuid
import datetime
import requests
import threading
import time
from tqdm import tqdm

# get filename
version_name = os.path.basename(__file__).replace(".py","")

def info(app:FastAPI,era_obj:dict):
    print("Loading Era Info:",version_name)
    @app.get(f"/{version_name}/info")
    def era_info():
        return {"name":version_name,"era_details":era_obj}
def main(oldsite,era_obj:dict):
    print("Loading Era:",version_name)
    print(f"Era \"{version_name}\" started at timestamp, all dates between this and the next era/the present will be represented by this version:",era_obj["start_range_timestamp"])
    app = oldsite.fast_api_app
    templates = oldsite.fast_api_templates
    @app.get(f"/")
    def root(request: Request):
        return templates.TemplateResponse(f"{version_name}/index.html", {"request": request, "version_name":version_name, "oldsite":oldsite})