from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    sentence: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # هنا نضع كود الـ HTML الخاص بالتصميم الذهبي الذي ظهر في صورتك
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>الجوهرة LMM v2.0</title>
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: auto; border: 1px solid #30363d; padding: 20px; border-radius: 10px; }
            .gold-text { color: #d4af37; font-size: 24px; font-weight: bold; }
            textarea { width: 100%; background: #161b22; color: white; border: 1px solid #30363d; border-radius: 5px; padding: 10px; margin-top: 20px; }
            .btn { background-color: #d4af37; color: black; border: none; padding: 15px; width: 100%; border-radius: 5px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            .tag { display: inline-block; padding: 5px 10px; border: 1px solid #30363d; border-radius: 20px; margin: 5px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="gold-text">✦ الجوهرة ✦</div>
            <p>AL-JAWHARA · LARGE MORPHOLOGY MODEL · v2.0</p>
            <div class="tag">أول LMM عربي</div> <div class="tag">Zero GPU</div>
            
            <textarea id="inputText" rows="4" placeholder="أدخل جملة أو كلمة عربية..."></textarea>
            
            <button class="btn" onclick="analyze()">تحليل وتوليد الكود ←</button>
            
            <div id="result" style="margin-top:20px; white-space: pre-wrap; text-align: right;"></div>
        </div>

        <script>
            async def analyze() {
                const text = document.getElementById('inputText').value;
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sentence: text})
                });
                const data = await response.json();
                document.getElementById('result').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    # هنا نضع منطق استخراج الكود بناءً على الكلمة
    return {
        "sentence": request.sentence,
        "status": "success",
        "generated_code": f"// Generated code for: {request.sentence}"
    }
