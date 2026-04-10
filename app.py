from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "API شغال 🔥"}


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

@app.post("/encrypt")
def encrypt(data: Text):
    result = "".join(chr(ord(c)+1) for c in data.text)
    return {"result": result}
"""

    elif "احسب" in command or "حاسب" in command:
        return """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    a: float
    b: float

@app.post("/add")
def add(data: Numbers):
    return {"result": data.a + data.b}

@app.post("/multiply")
def multiply(data: Numbers):
    return {"result": data.a * data.b}
"""

    elif "ترجم" in command:
        return """
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Text(BaseModel):
    text: str

@app.post("/translate")
def translate(data: Text):
    return {
        "original": data.text,
        "translated": "hello" if data.text == "مرحبا" else "unknown"
    }
"""

    else:
        return "# لم يتم التعرف على الأمر"

# =========================
# 🔥 API: توليد + حفظ
# =========================

@app.post("/generate-api")
async def generate_api(cmd: CommandModel):

    code = generate_api_code(cmd.command)

    # 💾 حفظ الملف
    filename = "generated_api.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "command": cmd.command,
        "message": "تم توليد API وحفظه 🔥",
        "file": filename,
        "generated_code": code
    }

# =========================
# 🌐 الصفحة الرئيسية
# =========================

@app.get("/")
def home():
    return {
        "message": "LMM Generator شغال 🔥 استخدمي /docs"
    }
