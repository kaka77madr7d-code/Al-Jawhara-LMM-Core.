from fastapi import FastAPI
from pydantic import BaseModel
import requests
import base64
import random
import os

app = FastAPI()

# =========================
# 🔐 قراءة التوكن من Render
# =========================

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = "kaka77madr7d-code"

# =========================
# 📦 Model
# =========================

class CommandModel(BaseModel):
    command: str

# =========================
# 🧠 توليد كود API
# =========================

def generate_api_code(command: str):
    if "شفر" in command:
        return """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Text(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "API تشفير شغال 🔥"}

@app.post("/encrypt")
def encrypt(data: Text):
    result = "".join(chr(ord(c)+1) for c in data.text)
    return {"result": result}
"""
    else:
        return "# لم يتم التعرف على الأمر"

# =========================
# 🚀 إنشاء Repo
# =========================

def create_repo(repo_name):

    if not GITHUB_TOKEN:
        print("❌ TOKEN NOT FOUND")
        return False

    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "name": repo_name,
        "auto_init": True,
        "private": False
    }

    r = requests.post(url, json=data, headers=headers)

    print("=== CREATE REPO DEBUG ===")
    print("Status:", r.status_code)
    print("Response:", r.text)

    return r.status_code == 201

# =========================
# 📤 رفع الملفات
# =========================

def upload_file(repo, path, content):

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    encoded = base64.b64encode(content.encode()).decode()

    data = {
        "message": f"add {path}",
        "content": encoded
    }

    r = requests.put(url, json=data, headers=headers)

    print(f"=== UPLOAD {path} ===")
    print("Status:", r.status_code)
    print("Response:", r.text)

# =========================
# 🔥 API: Deploy
# =========================

@app.post("/deploy")
async def deploy(cmd: CommandModel):

    repo_name = f"ai-api-{random.randint(1000,9999)}"

    code = generate_api_code(cmd.command)

    created = create_repo(repo_name)

    if not created:
        return {
            "error": "❌ فشل إنشاء الريبو",
            "hint": "تأكدي إن GITHUB_TOKEN موجود في Render Environment"
        }

    upload_file(repo_name, "app.py", code)
    upload_file(repo_name, "requirements.txt", "fastapi\nuvicorn")

    return {
        "message": "✅ تم إنشاء API ورفعه على GitHub",
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
        "status": "جاهز للربط مع Render 🔥"
    }

# =========================
# 🌐 Home
# =========================

@app.get("/")
def home():
    return {
        "message": "AI DevOps System شغال 😈 استخدمي /docs"
    }
