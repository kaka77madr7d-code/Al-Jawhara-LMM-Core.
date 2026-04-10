from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# =========================
# 📦 Model
# =========================

class CommandModel(BaseModel):
    command: str

# =========================
# 🧠 Generator
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
    elif "احسب" in command:
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
"""
    else:
        return "# لم يتم التعرف على الأمر"

# =========================
# 🔥 API توليد
# =========================

@app.post("/generate-api")
async def generate_api(cmd: CommandModel):
    code = generate_api_code(cmd.command)
    return {
        "command": cmd.command,
        "generated_code": code
    }

# =========================
# 🌐 Home
# =========================

@app.get("/")
def home():
    return {"message": "مولد APIs جاهز 🔥"}
