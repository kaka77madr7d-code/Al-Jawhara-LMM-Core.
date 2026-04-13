from fastapi import FastAPI
from pydantic import BaseModel
import requests, base64, random, os

app = FastAPI()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
GITHUB_USERNAME = "kaka77madr7d-code"

# =========================
# 1. LMM (وزنك الحقيقي مبسط)
# =========================
def detect_pattern(word):
    if word.startswith("ي") and "ّ" in word:
        return "يُفَعِّل"
    if word.startswith("أ"):
        return "أَفْعَلَ"
    if word.startswith("اس"):
        return "اسْتَفْعَلَ"
    return "UNKNOWN"

PATTERN_TO_TASK = {
    "يُفَعِّل": "PROCESS",
    "أَفْعَلَ": "OUTPUT",
    "اسْتَفْعَلَ": "SOURCE"
}

def infer(word):
    p = detect_pattern(word)
    return PATTERN_TO_TASK.get(p, "UNKNOWN")

# =========================
# 2. Compiler
# =========================
def compile_pipeline(sentence):
    pipeline = []
    for w in sentence.split():
        t = infer(w)
        if t != "UNKNOWN":
            pipeline.append(t)
    return pipeline

# =========================
# 3. توليد Backend
# =========================
def generate_backend(pipeline):

    steps = ""

    for step in pipeline:
        if step == "SOURCE":
            steps += "data = {'value': 'data from source'}\n"
        elif step == "PROCESS":
            steps += "data['value'] = data['value'].upper()\n"
        elif step == "OUTPUT":
            steps += "result = data\n"

    return f"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/api")
def run():
    {steps}
    return result if 'result' in locals() else data

@app.get("/")
def ui():
    return HTMLResponse(open("index.html").read())
"""

# =========================
# 4. توليد UI 🔥
# =========================
def generate_ui():

    return """
<html>
<body style="background:#111;color:white;text-align:center;font-family:sans-serif">
<h1>🔥 AI Generated App</h1>
<button onclick="run()">تشغيل</button>
<pre id="out"></pre>

<script>
async function run(){
 let r = await fetch('/api')
 let d = await r.json()
 document.getElementById('out').innerText = JSON.stringify(d, null, 2)
}
</script>
</body>
</html>
"""

# =========================
# 5. GitHub
# =========================
def create_repo(repo):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.post(url, headers=headers, json={"name": repo})
    return r.status_code == 201

def push(repo, files):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for name, content in files.items():
        requests.put(
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/contents/{name}",
            headers=headers,
            json={
                "message": f"add {name}",
                "content": base64.b64encode(content.encode()).decode()
            }
        )

# =========================
# 6. Render Deploy 🔥
# =========================
def deploy_render(repo):

    url = "https://api.render.com/v1/services"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "type": "web_service",
        "name": repo,
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo}",
        "branch": "main",
        "startCommand": "uvicorn app:app --host 0.0.0.0 --port 10000"
    }

    r = requests.post(url, headers=headers, json=data)
    return r.json()

# =========================
# 7. API النهائي 🔥🔥🔥
# =========================
class Req(BaseModel):
    sentence: str

@app.post("/build-and-deploy")
def build(req: Req):

    pipeline = compile_pipeline(req.sentence)

    repo = f"ai-full-{random.randint(1000,9999)}"

    files = {
        "app.py": generate_backend(pipeline),
        "index.html": generate_ui(),
        "requirements.txt": "fastapi\nuvicorn\n"
    }

    if not create_repo(repo):
        return {"error": "GitHub failed"}

    push(repo, files)

    render = deploy_render(repo)

    return {
        "sentence": req.sentence,
        "pipeline": pipeline,
        "repo": f"https://github.com/{GITHUB_USERNAME}/{repo}",
        "render": render
    }
