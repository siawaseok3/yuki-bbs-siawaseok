import json
import requests
import urllib.parse
import time
import datetime
import random
import os
import base64
from cache import cache

max_api_wait_time = 3
max_time = 10
url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()
version = "1.0"

def get_info(request):
    global version
    #return json.dumps()
    return json.dumps([version,os.environ.get('RENDER_EXTERNAL_URL'),str(request.scope["headers"]),str(request.scope['router'])[39:-2]])
    

from fastapi import FastAPI, Depends
from fastapi import Response, Cookie, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.responses import RedirectResponse as redirect
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Union

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.templating import Jinja2Templates
template = Jinja2Templates(directory='views').TemplateResponse

@app.get("/", response_class=HTMLResponse)
def home(response: Response, request: Request, yuki: Union[str] = Cookie(None)):
    return redirect("/bbs")

@app.get("/bbs", response_class=HTMLResponse)
def view_bbs(request: Request, name: Union[str, None] = "", seed: Union[str, None] = "", channel: Union[str, None] = "main", verify: Union[str, None] = "false", yuki: Union[str] = Cookie(None)):
    return template("bbs.html", {"request": request})

@app.get("/bbs/info", response_class=HTMLResponse)
def view_bbs_info(request: Request):
    res = HTMLResponse(requests.get(f"{url}bbs/info").text)
    return res

@cache(seconds=5)
def bbsapi_cached(verify, channel, from_param):
    return requests.get(f"{url}bbs/api?t={urllib.parse.quote(str(int(time.time() * 1000)))}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}&from={from_param}", cookies={"yuki": "True"}).text

@app.get("/bbs/api", response_class=HTMLResponse)
def view_bbs_api(request: Request, t: str, channel: Union[str, None] = "main", verify: Union[str, None] = "false", from_param: int = 0):
    return bbsapi_cached(verify, channel, from_param)

@app.get("/bbs/result")
def write_bbs(request: Request, name: str = "", message: str = "", seed: Union[str, None] = "", channel: Union[str, None] = "main", verify: Union[str, None] = "false"):
    message = base64.b64decode(message).decode('utf-8')
    print(f"name:{name}, seed:{seed}, channel:{channel}, message:{message}")
    t = requests.get(f"{url}bbs/result?name={urllib.parse.quote(name)}&message={urllib.parse.quote(message)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}&info={urllib.parse.quote(get_info(request))}", cookies={"yuki": "True"}, allow_redirects=False)
    if t.status_code != 307:
        return HTMLResponse(t.text)
    return redirect(f"/bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}")

@cache(seconds=30)
def how_cached():
    return requests.get(f"{url}bbs/how").text

@app.get("/bbs/how", response_class=PlainTextResponse)
def view_commonds(request: Request, yuki: Union[str] = Cookie(None)):
    return how_cached()

@app.get("/load_instance")
def load_instance():
    global url
    url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()
