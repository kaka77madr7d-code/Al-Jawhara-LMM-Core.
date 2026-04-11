from fastapi import FastAPI
from pydantic import BaseModel
import requests, base64, random, os, re
from enum import Enum, auto

app = FastAPI()

# =========================
# 🔐 ENV
# =========================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = "kaka77madr7d-code"

# =========================
# 📦 Model
# =========================
class CommandModel(BaseModel):
    command: str

# =========================
# 🧠 LMM (تحليل صرفي مبسط)
# =========================

CONSONANTS = set("بتثجحخدذرزسشصضطظعغفقكلمنهوي")
SLOT_CHARS = set("فعل")

PATTERNS = {
    "فَعَّلَ": "FALLAL",
    "اسْتَفْعَلَ": "ISTAF_AL",
    "تَفَاعَلَ": "TAFAA_AL",
}

def normalize(w):
    return re.sub(r"[\u064B-\u065F]", "", w)

def match(word, pattern):
    w = normalize(word)
    p = normalize(pattern)
    if len(w) != len(p):
        return False
    for wc, pc in zip(w, p):
        if pc in SLOT_CHARS:
            if wc not in CONSONANTS:
                return False
        elif wc != pc:
            return False
    return True

def detect_pattern(word):
    for pat, tag in PATTERNS.items():
        if match(word, pat):
            return tag
    return None

# =========================
# 🧠 أكسيومات
# =========================

class P(Enum):
    TRANSFORM = auto()
    REQUEST = auto()
    RECIPROCAL = auto()

TAG_MAP = {
    "FALLAL": {P.TRANSFORM},
    "ISTAF_AL": {P.REQUEST},
    "TAFAA_AL": {P.RECIPROCAL},
}

def infer_task(tag):
    props = TAG_MAP.get(tag, set())

    if P.TRANSFORM in props:
        return "ENCRYPT_API"

    if P.REQUEST in props:
        return "REQUEST_API"

    if P.RECIPROCAL in props:
        return "SOCKET_API"

    return "UNKNOWN"

# =========================
# ⚙️ توليد API
# =========================

def generate_api(task):

    if task == "ENCRYPT_API":
        return """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Text(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Encrypt API 🔥"}

@app.post("/encrypt")
def encrypt(data: Text):
    return {"result": "".join(chr(ord(c)+1) for c in data.text)}
"""

    if task == "REQUEST_API":
        return """
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Request API 🔥"}

@app.get("/fetch")
def fetch():
    return {"status": "request sent"}
"""

    if task == "SOCKET_API":
        return """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Socket API 🔥"}

@app.get("/socket")
def socket():
    return {"message": "socket running"}
"""

    return "# unknown"

# =========================
# 🚀 GitHub
# =========================

def create_repo(name):
    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.post(url, json={"name": name, "auto_init": True}, headers=headers)

    print("CREATE:", r.status_code, r.text)

    return r.status_code == 201

def upload(repo, path, content):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "message": f"add {path}",
        "content": base64.b64encode(content.encode()).decode()
    }

    r = requests.put(url, json=data, headers=headers)

    print("UPLOAD:", path)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    if r.status_code not in [200, 201]:
        print(f"❌ فشل رفع {path}")
        return False

    return True

# =========================
# 🔥 Deploy
# =========================

@app.post("/deploy")
def deploy(cmd: CommandModel):

    word = cmd.command.split()[0]

    tag = detect_pattern(word)
    task = infer_task(tag)

    if task == "UNKNOWN":
        return {"error": "❌ لم يتم فهم الكلمة"}

    code = generate_api(task)

    if not code or code.strip() == "# unknown":
        return {"error": "❌ لم يتم توليد كود صالح"}

    repo = f"lmm-api-{random.randint(1000,9999)}"

    if not create_repo(repo):
        return {"error": "❌ فشل إنشاء repo"}

    # 🔥 ملفات المشروع
    requirements = "fastapi\nuvicorn\nrequests"

    render_yaml = """
services:
  - type: web
    name: lmm-auto-api
    env: python
    buildCommand: ""
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    plan: free
"""

    # 🚨 رفع مع تحقق
    if not upload(repo, "app.py", code):
        return {"error": "❌ فشل رفع app.py"}

    if not upload(repo, "requirements.txt", requirements):
        return {"error": "❌ فشل رفع requirements"}

    if not upload(repo, "render.yaml", render_yaml):
        return {"error": "❌ فشل رفع render.yaml"}

    return {
        "word": word,
        "pattern": tag,
        "task": task,
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo}",
        "status": "🔥 جاهز للربط مع Render (Blueprint)"
    }

# =========================
# 🌐 Home
# =========================

@app.get("/")
def home():
    return {"message": "LMM + Auto Deploy شغال 😈 ادخلي /docs"}
