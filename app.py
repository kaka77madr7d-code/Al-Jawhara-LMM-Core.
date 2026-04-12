# =========================================
# Al-Jawhara LMM — Full System
# تحليل صرفي + توليد UI + نشر تلقائي
# =========================================

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import requests
import os
import base64
import re

app = FastAPI(title="Al-Jawhara LMM v3 🔥")

# =========================================
# 1) تحليل بسيط للأوزان (STRICT)
# =========================================

PATTERNS = {
    "يُفَعِّل": "DATA_PROCESSOR",
    "فَعَّلَ": "DATA_PROCESSOR",

    "مُتَفَعِّل": "UI_GENERATOR",

    "مُتَفَاعِل": "NETWORK_SOCKET",
    "تَفَاعَلَ": "NETWORK_SOCKET",

    "مَفْعُول": "DATA_OBJECT",

    "فَاعِل": "ACTIVE_AGENT",

    "اسْتَفْعَلَ": "HTTP_CLIENT",
}

def detect_pattern(word):
    # تبسيط (بدون تشكيل)
    w = re.sub(r'[\u064B-\u065F]', '', word)

    if w.startswith("ي") and len(w) >= 5:
        return "يُفَعِّل"

    if w.startswith("مت") and "ا" in w:
        return "مُتَفَاعِل"

    if w.startswith("مت"):
        return "مُتَفَعِّل"

    if w.startswith("است"):
        return "اسْتَفْعَلَ"

    if "ّ" in word:
        return "فَعَّلَ"

    return None


def infer_task(pattern):
    return PATTERNS.get(pattern, "UNKNOWN")


# =========================================
# 2) توليد UI حقيقي (HTML)
# =========================================

def generate_ui(title):
    return f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{
    background:#0d1117;
    color:white;
    font-family:Arial;
    text-align:center;
    padding:50px;
}}
.container {{
    background:#161b22;
    padding:30px;
    border-radius:10px;
}}
input {{
    padding:10px;
    width:80%;
    margin:10px;
}}
button {{
    padding:10px 20px;
    background:#c9a84c;
    border:none;
}}
</style>
</head>
<body>

<div class="container">
<h1>{title}</h1>

<input id="text" placeholder="اكتب هنا">
<br>
<button onclick="send()">تنفيذ</button>

<p id="result"></p>

</div>

<script>
async function send() {{
    const text = document.getElementById("text").value;

    const res = await fetch("/encrypt", {{
        method:"POST",
        headers:{{"Content-Type":"application/json"}},
        body:JSON.stringify({{text}})
    }});

    const data = await res.json();
    document.getElementById("result").innerText = data.result;
}}
</script>

</body>
</html>
"""


# =========================================
# 3) توليد API
# =========================================

def generate_api_code(title):
    ui = generate_ui(title)

    return f'''
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI()

class Text(BaseModel):
    text: str

@app.post("/encrypt")
def encrypt(data: Text):
    result = "".join(chr(ord(c)+1) for c in data.text)
    return {{"result": result}}

@app.get("/", response_class=HTMLResponse)
def home():
    return """{ui}"""
'''


# =========================================
# 4) رفع على GitHub
# =========================================

def upload_to_github(repo_name, code):
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME")

    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {token}"
    }

    data = {
        "name": repo_name,
        "private": False
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code not in [200, 201]:
        return None

    file_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/app.py"

    content = base64.b64encode(code.encode()).decode()

    requests.put(file_url, json={
        "message": "initial commit",
        "content": content
    }, headers=headers)

    return f"https://github.com/{username}/{repo_name}"


# =========================================
# 5) API
# =========================================

class RequestModel(BaseModel):
    sentence: str


@app.post("/build-and-deploy")
def build_and_deploy(req: RequestModel):
    words = req.sentence.split()

    task_detected = "UNKNOWN"

    for w in words:
        pattern = detect_pattern(w)
        task = infer_task(pattern)

        if task != "UNKNOWN":
            task_detected = task
            break

    # توليد UI + API
    code = generate_api_code(req.sentence)

    # رفع GitHub
    repo_name = "ai-ui-" + str(abs(hash(req.sentence)) % 10000)
    repo = upload_to_github(repo_name, code)

    if not repo:
        return {"error": "فشل GitHub"}

    return {
        "message": "🔥 تم بناء التطبيق بالكامل",
        "task": task_detected,
        "repo": repo,
        "next": "اربطه بـ Render"
    }


# =========================================
# 6) واجهة بسيطة
# =========================================

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>Al-Jawhara LMM 🔥</h1>
    <p>اكتب جملة → يتحول لتطبيق كامل</p>
    """
