from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import time
import random
import string

app = FastAPI()

# 🔐 Environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")

# 👇 حطي اسمك هنا فقط
GITHUB_USERNAME = "kaka77madr7d-code"

# =========================
# 🧠 تحليل لغوي (أوزان → مهام)
# =========================

PATTERN_MAP = {
    "يستخرج": "HTTP_CLIENT",
    "يعالج": "DATA_PROCESSOR",
    "يشفر": "DATA_PROCESSOR",
    "يعرض": "UI_GENERATOR",
    "يرسل": "FACTORY"
}

def analyze_sentence(sentence: str):
    words = sentence.split()
    pipeline = []

    for w in words:
        for key in PATTERN_MAP:
            if key in w:
                pipeline.append(PATTERN_MAP[key])

    return pipeline

# =========================
# 🧠 GitHub
# =========================

def create_github_repo(repo_name):

    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    data = {
        "name": repo_name,
        "private": False
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code not in [200, 201]:
        return None, r.text

    return r.json()["clone_url"], None


def push_files(repo_name):

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/app.py"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    code = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Generated App 🚀"}
"""

    import base64
    content = base64.b64encode(code.encode()).decode()

    data = {
        "message": "init app",
        "content": content
    }

    r = requests.put(url, json=data, headers=headers)

    return r.status_code in [200, 201]


# =========================
# 🧠 Render
# =========================

def get_render_owner_id():
    url = "https://api.render.com/v1/owners"

    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return None

    return r.json()[0]["id"]


def create_render_service(repo_url, name):

    owner_id = get_render_owner_id()

    url = "https://api.render.com/v1/services"

    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "type": "web_service",
        "name": name,
        "ownerId": owner_id,
        "repo": repo_url,
        "branch": "main",
        "runtime": "python",
        "buildCommand": "pip install fastapi uvicorn",
        "startCommand": "uvicorn app:app --host 0.0.0.0 --port 10000"
    }

    r = requests.post(url, json=payload, headers=headers)

    if r.status_code != 201:
        return None, r.text

    data = r.json()
    slug = data["service"]["slug"]

    return f"https://{slug}.onrender.com", None


# =========================
# 🚀 API الرئيسي
# =========================

class RequestData(BaseModel):
    sentence: str


@app.post("/build-and-deploy")
def build_and_deploy(req: RequestData):

    sentence = req.sentence

    # 🧠 تحليل
    pipeline = analyze_sentence(sentence)

    # 🧠 اسم عشوائي
    repo_name = "ai-app-" + ''.join(random.choices(string.digits, k=4))

    # 🧠 GitHub
    repo_url, err = create_github_repo(repo_name)

    if err:
        return {"error": "GitHub Failed", "details": err}

    push_files(repo_name)

    # 🧠 Render
    live_url, err = create_render_service(repo_url, repo_name)

    if err:
        return {"error": "Render Failed", "details": err}

    # ⏳ وقت البناء
    time.sleep(10)

    return {
        "sentence": sentence,
        "pipeline": pipeline,
        "repo": repo_url,
        "live_url": live_url,
        "message": "🚀 التطبيق قيد التشغيل"
    }
