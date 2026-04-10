from fastapi import FastAPI
from pydantic import BaseModel
import requests
import base64
import random

app = FastAPI()

# =========================
# ⚙️ إعدادات GitHub (عدليها)
# =========================

GITHUB_TOKEN = "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"  # 🔐 حطي التوكن هنا
GITHUB_USERNAME = "kaka77madr7d-code"   # 👈 اسم حسابك

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
# 🚀 إنشاء Repo (مع تحقق)
# =========================

def create_repo(repo_name):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    data = {
        "name": repo_name,
        "auto_init": True
    }

    r = requests.post(url, json=data, headers=headers)

    print("GitHub create repo response:", r.status_code, r.text)

    if r.status_code == 201:
        return True
    else:
        return False

# =========================
# 📤 رفع ملف إلى GitHub
# =========================

def upload_file(repo, path, content):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    encoded = base64.b64encode(content.encode()).decode()

    data = {
        "message": f"add {path}",
        "content": encoded
    }

    r = requests.put(url, json=data, headers=headers)

    print("Upload file response:", r.status_code, r.text)

# =========================
# 🔥 API: Deploy كامل
# =========================

@app.post("/deploy")
async def deploy(cmd: CommandModel):

    # 💣 اسم عشوائي عشان ما يتكرر
    repo_name = f"ai-api-{random.randint(1000,9999)}"

    code = generate_api_code(cmd.command)

    # 1️⃣ إنشاء repo
    created = create_repo(repo_name)

    if not created:
        return {
            "error": "❌ فشل إنشاء الريبو",
            "solution": "تأكدي من GitHub Token وصلاحياته (repo)"
        }

    # 2️⃣ رفع الملفات
    upload_file(repo_name, "app.py", code)
    upload_file(repo_name, "requirements.txt", "fastapi\nuvicorn")

    return {
        "message": "✅ تم إنشاء API ورفعه على GitHub",
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
        "next_step": "اربطيه في Render وبيشتغل 🔥"
    }

# =========================
# 🌐 Home
# =========================

@app.get("/")
def home():
    return {"message": "AI DevOps شغال 😈 استخدمي /docs"}
