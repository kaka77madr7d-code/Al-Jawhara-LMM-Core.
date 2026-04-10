from fastapi import FastAPI
from pydantic import BaseModel
import requests
import base64

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "API شغال 🔥"}


# =========================
# ⚙️ إعداداتك (عدليها)
# =========================

GITHUB_TOKEN = "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"
GITHUB_USERNAME = "kaka77madr7d-code"

# =========================
# 📦 Model
# =========================

class CommandModel(BaseModel):
    command: str

# =========================
# 🧠 توليد الكود
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
    return {"message": "API شغال 🔥"}

@app.post("/encrypt")
def encrypt(data: Text):
    result = "".join(chr(ord(c)+1) for c in data.text)
    return {"result": result}
"""
    return "# unknown command"

# =========================
# 🚀 إنشاء Repo
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

    # 🔥 طباعة الرد الحقيقي
    print("GitHub response:", r.status_code, r.text)

    if r.status_code == 201:
        return True
    else:
        return False

# =========================
# 📤 رفع ملف
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

    requests.put(url, json=data, headers=headers)

# =========================
# 🔥 API الرئيسي
# =========================

@app.post("/deploy")
async def deploy(cmd: CommandModel):

    repo_name = "ai-generated-api"

    code = generate_api_code(cmd.command)

    # 1. إنشاء repo
created = create_repo(repo_name)

if not created:
    return {
        "error": "❌ فشل إنشاء الريبو",
        "solution": "تأكدي من GitHub Token أو اسم الريبو"
    }

    # 2. رفع الملفات
    upload_file(repo_name, "app.py", code)
    upload_file(repo_name, "requirements.txt", "fastapi\nuvicorn")

    return {
        "message": "تم رفع المشروع على GitHub 🚀",
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo_name}",
        "next_step": "اربطه بـ Render وبيشتغل تلقائي 🔥"
    }

# =========================
# 🌐 Home
# =========================

@app.get("/")
def home():
    return {"message": "AI Deployer جاهز 😈"}
