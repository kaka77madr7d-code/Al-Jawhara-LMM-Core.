from fastapi import FastAPI
from pydantic import BaseModel
import os
import uvicorn

app = FastAPI()

# =========================
# 🧠 Models
# =========================

class TextModel(BaseModel):
    text: str

class CalcModel(BaseModel):
    a: float
    b: float

# =========================
# 🧠 تحليل الكلمة
# =========================

def detect_intent(word):
    if "شفر" in word:
        return "ENCRYPT"
    if "حسب" in word or "حاسب" in word:
        return "CALCULATE"
    if "ترجم" in word:
        return "TRANSLATE"
    return "UNKNOWN"

# =========================
# 🔐 API ثابتة (مهمة)
# =========================

@app.post("/encrypt")
async def encrypt(req: TextModel):
    result = "".join(chr(ord(c)+1) for c in req.text)
    return {"original": req.text, "encrypted": result}

@app.post("/add")
async def add(req: CalcModel):
    return {"result": req.a + req.b}

@app.post("/multiply")
async def multiply(req: CalcModel):
    return {"result": req.a * req.b}

@app.post("/translate")
async def translate(req: TextModel):
    return {
        "original": req.text,
        "translated": "hello" if req.text == "مرحبا" else "unknown"
    }

# =========================
# 🎯 API ذكي (يربط الكلمة)
# =========================

@app.post("/smart")
async def smart(word: str, text: str = "", a: float = 0, b: float = 0):
    intent = detect_intent(word)

    if intent == "ENCRYPT":
        result = "".join(chr(ord(c)+1) for c in text)
        return {"intent": intent, "result": result}

    elif intent == "CALCULATE":
        return {
            "intent": intent,
            "add": a + b,
            "multiply": a * b
        }

    elif intent == "TRANSLATE":
        return {
            "intent": intent,
            "translated": "hello" if text == "مرحبا" else "unknown"
        }

    else:
        return {"intent": "UNKNOWN"}

# =========================
# 🌐 واجهة
# =========================

@app.get("/")
async def home():
    return {"message": "LMM جاهز 🔥 استخدمي /docs"}

# =========================
# 🚀 تشغيل Render
# =========================
@app.get("/")
async def home():
    return {"message": "LMM جاهز 🔥 استخدمي /docs"}
