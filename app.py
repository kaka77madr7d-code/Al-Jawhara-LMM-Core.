from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

# =========================
# 🧠 Data Structures
# =========================

class AnalyzeRequest(BaseModel):
    sentence: str

class Unit:
    def __init__(self, original, root, pattern, tag):
        self.original = original
        self.root = root
        self.pattern = pattern
        self.tag = tag

# =========================
# 🔬 Linguistic Rules
# =========================

TAG_PROPS = {
    "FA_AL": ["RECIPROCAL", "BINARY"],
    "UNKNOWN": []
}

def extract_root(word):
    # تبسيط شديد (تقدرين تطورينه)
    return word[:3] if len(word) >= 3 else word

def detect_pattern(word):
    if len(word) == 4 and word[1] == "ا":
        return "فاعل", "FA_AL"
    return None, "UNKNOWN"

def distill(sentence):
    words = sentence.split()
    units = []

    for w in words:
        root = extract_root(w)
        pattern, tag = detect_pattern(w)
        units.append(Unit(w, root, pattern, tag))

    return units

# =========================
# 🤖 Inference Engine
# =========================

def infer(tag):
    if tag == "FA_AL":
        return "NETWORK_SOCKET"
    return "UNKNOWN_TASK"

# =========================
# 🌐 API
# =========================

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    units = distill(req.sentence)
    results = []

    for u in units:
        props = TAG_PROPS.get(u.tag, [])

        results.append({
            "word": u.original,
            "root": u.root,
            "pattern": u.pattern,
            "tag": u.tag,
            "properties": props,
            "task": infer(u.tag)
        })

    return {"results": results}

# =========================
# 🎨 Frontend (HTML)
# =========================

@app.get("/")
async def home():
    return """
    <html>
    <head>
        <title>LMM System</title>
        <style>
            body {
                font-family: Arial;
                background: #0f172a;
                color: white;
                text-align: center;
                padding: 40px;
            }
            textarea {
                width: 80%;
                height: 100px;
                font-size: 18px;
                margin: 10px;
            }
            button {
                padding: 10px 20px;
                font-size: 18px;
                cursor: pointer;
            }
            pre {
                text-align: left;
                background: #1e293b;
                padding: 20px;
                margin-top: 20px;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <h1>🧠 LMM Linguistic Engine</h1>

        <textarea id="inputText" placeholder="اكتب جملة..."></textarea><br>
        <button onclick="analyze()">تحليل</button>

        <pre id="output"></pre>

        <script>
        async function analyze() {
            const sentence = document.getElementById("inputText").value;

            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ sentence })
            });

            const data = await res.json();

            let output = "";

            data.results.forEach(r => {
                output += `
🔹 الكلمة: ${r.word}
الجذر: ${r.root}
النمط: ${r.pattern || "—"}
النوع: ${r.tag || "—"}
الخصائص: ${r.properties.join(", ") || "—"}
⬇️
🎯 النتيجة: ${r.task}

-----------------------
`;
            });

            document.getElementById("output").textContent = output;
        }
        </script>
    </body>
    </html>
    """
