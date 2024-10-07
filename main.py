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


class OldSite:
    def __init__(self, timestamp:int = 1728284400, worker_time:int = 60,work_delay:int = 5, day_month_sync: bool = False,
            eras = [
                {
                    "name": "OldSiteVersion1",
                    "start_range_timestamp": 1728284400
                }
            ],
            app: FastAPI = None,
            templates: Jinja2Templates = None,
            worker: bool = False
        ): # Default timestamp is 2014-03-27
        self.base_timestamp = timestamp
        self.day_month_sync = day_month_sync
        self.name = "OldSite Template"
        self.work_queue = []
        self.worker_time = worker_time
        self.work_delay = 5
        self.fast_api_app = app
        self.fast_api_templates = templates
        self.current_era = None

        self.eras = []
        
        # Load all eras
        for era in eras:
            # Load era main function from ./versions/{era["name"]}.py
            era_module = __import__(f"versions.{era['name']}", fromlist=["main"])
            era_main = era_module.main
            era_info = era_module.info
            era_info(self.fast_api_app, era)
            if era["start_range_timestamp"] >= self.base_timestamp:
                self.current_era = (era, era_main)
            self.eras.append((era, era_main))
        print("Loaded Eras:",self.eras)
        self.current_era[1](self, self.current_era[0])

        self.worker_thread = None
        if worker:
            self.worker_thread = self.start_worker() # Runs every 5 seconds by default, checks for work, does work, then resumes checking for work
        print("OldSite Time:",datetime.datetime.fromtimestamp(self.timestamp/1000))

    def start_worker(self):
        return threading.Thread(target=self.worker, daemon=True).start()

    @property
    def timestamp(self):
        """Get the current timestamp of the OldSite instance -- Take the base timestamp and alter it to be the current month and day, but the base year. Example: 1728284400 -> 2024-10-07 00:00:00"""
        if self.day_month_sync:
            current_time = datetime.datetime.now()
            current_time = current_time.replace(year=datetime.datetime.fromtimestamp(self.base_timestamp/1000).year)
            return int(current_time.timestamp()*1000)
        return self.base_timestamp

    def worker(self):
        while True:
            try:
                time.sleep(self.worker_time + random.randint(5, 10)) # Sleep for worker_time + 5-10 seconds, offset to prevent all workers from running at the same time when running more than one worker
                print("Worker checking for work...")
                # Chec work_queue for work and do a task if there is anything in the queue
                if len(self.work_queue) > 0:
                    # print("Worker found work in queue.")
                    work = self.work_queue.pop(0)
                    print("Worker doing work:",work, "| Work Left:",len(self.work_queue))
                    # Do work based on the work["type"]
                    raise ValueError("Unknown work type: " + work["type"] + ". Discarding invalid work.")
            except Exception as e:
                print("Worker error:",e)
            time.sleep(self.work_delay)

        

app = FastAPI()

templates = Jinja2Templates(directory="./templates")

with open("timestamp") as f:
    timestamp = int(f.read())
    print("Loaded timestamp from file:",timestamp)

oldsite = OldSite(timestamp, day_month_sync=False, app=app, templates=templates, worker=False)

# GLOBAL ROUTES - These are the same for all versions of the site. Typically these should be control panels, information pages, shared APIs, etc.

# TEMPLATE
# @app.get("/")
# def home(request: Request):
#     search_query = ""
#     if "q" in request.query_params:
#         search_query = request.query_params["q"]
#     return templates.TemplateResponse("index.html", context={"request": request, "search_query": search_query})

@app.get("/info")
def info(request: Request):
    print("OldSite Timestamp:",oldsite.timestamp)
    return templates.TemplateResponse("info.html", context={"request": request, "oldsite": oldsite})

@app.get("/eras")
def eras():
    eras_list = []
    for era in oldsite.eras:
        eras_list.append(era[0])
    return {
        "current_timestamp": oldsite.timestamp,
        "eras": eras_list
    }

can_change_time = False

@app.post("/set_timestamp")
def set_timestamp(request: Request):
    global can_change_time
    timestamp = int(request.query_params["timestamp"])
    if can_change_time:
        oldsite.base_timestamp = timestamp
        return {"success": True}
    return {"success": False}

# Run the server
uvicorn.run(app, host="192.168.1.101", port=8000)