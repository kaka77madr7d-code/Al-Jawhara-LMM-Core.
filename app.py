from fastapi import FastAPI
from pydantic import BaseModel
import requests, base64, random, os, re
from dataclasses import dataclass
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
# 🧠 LMM — صرف
# =========================

CONSONANTS = set("بتثجحخدذرزسشصضطظعغفقكلمنهوي")
SLOT_CHARS  = set("فعل")

PATTERNS = {
    "فَعَلَ": {"tag":"FAL"},
    "فَعَّلَ": {"tag":"FALLAL"},
    "فَاعَلَ": {"tag":"FA_AL"},
    "أَفْعَلَ": {"tag":"AF_AL"},
    "تَفَعَّلَ": {"tag":"TAFA_AL"},
    "تَفَاعَلَ": {"tag":"TAFAA_AL"},
    "انْفَعَلَ": {"tag":"INFA_AL"},
    "افْتَعَلَ": {"tag":"IFTA_AL"},
    "اسْتَفْعَلَ": {"tag":"ISTAF_AL"},
}

def norm(w):
    w = re.sub(r"[\u064B-\u065F]", "", w)
    return w

def match(word, pat):
    if len(word) != len(pat): return False
    for wc, pc in zip(word, pat):
        if pc in SLOT_CHARS:
            if wc not in CONSONANTS: return False
        elif wc != pc:
            return False
    return True

def detect(word):
    for pat, info in PATTERNS.items():
        if match(norm(word), norm(pat)):
            return info["tag"]
    return None

# =========================
# 🧠 أكسيومات
# =========================

class P(Enum):
    TRANSFORM=auto()
    REQUEST=auto()
    RECIPROCAL=auto()
    STATE=auto()

TAG_MAP = {
    "FALLAL": {P.TRANSFORM},
    "ISTAF_AL": {P.REQUEST},
    "TAFAA_AL": {P.RECIPROCAL, P.STATE},
}

# =========================
# 🧠 استنتاج → مهمة
# =========================

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

@app.post("/encrypt")
def encrypt(data: Text):
    return {"result": "".join(chr(ord(c)+1) for c in data.text)}
"""

    if task == "REQUEST_API":
        return """
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/fetch")
def fetch():
    return {"status": "request sent"}
"""

    if task == "SOCKET_API":
        return """
from fastapi import FastAPI

app = FastAPI()

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

    r = requests.post(url, json={"name":name,"auto_init":True}, headers=headers)
    print(r.status_code, r.text)
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

    requests.put(url, json=data, headers=headers)

# =========================
# 🔥 API
# =========================

@app.post("/deploy")
def deploy(cmd: CommandModel):

    word = cmd.command.split()[0]  # أول كلمة

    tag = detect(word)
    task = infer_task(tag)

    if task == "UNKNOWN":
        return {"error": "❌ لم يتم فهم الكلمة"}

    code = generate_api(task)

    repo = f"lmm-api-{random.randint(1000,9999)}"

    if not create_repo(repo):
        return {"error":"❌ GitHub فشل"}

    upload(repo, "app.py", code)
    upload(repo, "requirements.txt", "fastapi\nuvicorn")

    return {
        "word": word,
        "pattern": tag,
        "task": task,
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo}"
    }

@app.get("/")
def home():
    return {"message": "LMM + DevOps 🔥 استخدمي /docs"}
