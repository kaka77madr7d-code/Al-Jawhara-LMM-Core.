from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# =========================
# 🧠 Request
# =========================

class RequestModel(BaseModel):
    text: str = ""

# =========================
# 🔬 تحليل الكلمة
# =========================

def detect_intent(word):
    if "شفر" in word:
        return "ENCRYPT_API"
    if "حسب" in word or "حاسب" in word:
        return "CALCULATOR_API"
    if "ترجم" in word:
        return "TRANSLATE_API"
    return "UNKNOWN"

# =========================
# 🤖 توليد API ديناميكي
# =========================

def build_api(intent):

    # 🔐 تشفير
    if intent == "ENCRYPT_API":

        @app.post("/encrypt")
        async def encrypt(req: RequestModel):
            result = "".join(chr(ord(c)+1) for c in req.text)
            return {"original": req.text, "encrypted": result}

        return "تم إنشاء API تشفير على /encrypt"

    # ➕ حاسبة
    elif intent == "CALCULATOR_API":

        class CalcModel(BaseModel):
            a: float
            b: float

        @app.post("/add")
        async def add(req: CalcModel):
            return {"result": req.a + req.b}

        @app.post("/multiply")
        async def multiply(req: CalcModel):
            return {"result": req.a * req.b}

        return "تم إنشاء API حاسبة على /add و /multiply"

    # 🌍 ترجمة (تجريبية)
    elif intent == "TRANSLATE_API":

        @app.post("/translate")
        async def translate(req: RequestModel):
            return {
                "original": req.text,
                "translated": "hello" if req.text == "مرحبا" else "unknown"
            }

        return "تم إنشاء API ترجمة على /translate"

    else:
        return "❌ لم يتم التعرف على الكلمة"

# =========================
# 🌐 API الرئيسي
# =========================

@app.post("/generate-api")
async def generate_api(word: str):
    intent = detect_intent(word)
    result = build_api(intent)

    return {
        "word": word,
        "intent": intent,
        "status": result
    }

# =========================
# 🎨 واجهة بسيطة
# =========================

@app.get("/")
async def home():
    return """
    <html>
    <head>
        <title>LMM API Generator</title>
        <style>
            body {
                background: #0f172a;
                color: white;
                text-align: center;
                font-family: Arial;
                padding: 40px;
            }
            input {
                width: 300px;
                padding: 10px;
                font-size: 18px;
            }
            button {
                padding: 10px 20px;
                font-size: 18px;
                margin-top: 10px;
            }
            pre {
                background: #1e293b;
                padding: 20px;
                margin-top: 20px;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <h1>🧠 LMM API Generator</h1>

        <input id="word" placeholder="اكتب كلمة...">
        <br>
        <button onclick="generate()">إنشاء API</button>

        <pre id="output"></pre>

        <script>
        async function generate() {
            const word = document.getElementById("word").value;

            const res = await fetch(`/generate-api?word=${word}`, {
                method: "POST"
            });

            const data = await res.json();

            document.getElementById("output").textContent =
                "🔹 الكلمة: " + data.word + "\\n" +
                "🧠 النية: " + data.intent + "\\n" +
                "🚀 الحالة: " + data.status + "\\n\\n" +
                "جربي الآن في /docs";
        }
        </script>
    </body>
    </html>
    """
