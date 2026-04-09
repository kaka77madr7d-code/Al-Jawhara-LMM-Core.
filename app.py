"""
Al-Jawhara LMM — Single File Demo (Render Optimized)
"""
from __future__ import annotations
import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import FrozenSet
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ══════════════════════════════════════════════════════
# § 1 — المُحلِّل الصرفي
# ══════════════════════════════════════════════════════

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
    "فَاعِل": {"tag":"FA_IL"},
    "مُفَعِّل": {"tag":"MUFA_IL"},
    "يُفَعِّل": {"tag":"YUFA_IL"},
    "مَفْعُول": {"tag":"MAF_UL"},
}

def _norm(w: str) -> str:
    w = re.sub(r"[\u064B-\u065F\u0670]", "", w)
    w = re.sub(r"[\u0625\u0623\u0622]", "\u0627", w)
    return w.replace("\u0629", "\u0647")

def _slot_match(word: str, pat: str) -> bool:
    wn, pn = _norm(word), _norm(pat)
    if len(wn) != len(pn): return False
    for wc, pc in zip(wn, pn):
        if pc in SLOT_CHARS:
            if wc not in CONSONANTS: return False
        elif wc != pc: return False
    return True

def detect_pattern(word: str):
    for pat, info in PATTERNS.items():
        if _slot_match(word, pat):
            return pat, info
    return None, None

def extract_root(word: str) -> str:
    w = _norm(word)
    return w[:3] if len(w) >= 3 else w

@dataclass
class MorphUnit:
    original: str
    root: str
    pattern: str | None
    tag: str | None
    position: int

def distill(sentence: str):
    units = []
    for i, word in enumerate(sentence.split()):
        root = extract_root(word)
        pat, info = detect_pattern(word)
        units.append(MorphUnit(word, root, pat, info["tag"] if info else None, i))
    return units

# ══════════════════════════════════════════════════════
# § 2 — الاستدلال
# ══════════════════════════════════════════════════════

class P(Enum):
    TRANSITIVE=auto()
    RECIPROCAL=auto()
    STATEFUL=auto()

TAG_PROPS = {
    "FAL": frozenset({P.TRANSITIVE}),
    "FA_AL": frozenset({P.RECIPROCAL}),
}

def infer(tag):
    if not tag:
        return "UNKNOWN"
    if tag == "FA_AL":
        return "NETWORK_SOCKET"
    if tag == "FAL":
        return "FUNCTION"
    return "UNKNOWN"

# ══════════════════════════════════════════════════════
# § 3 — API
# ══════════════════════════════════════════════════════

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    sentence: str

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    units = distill(req.sentence)
    result = []
    for u in units:
        task = infer(u.tag)
        result.append({
            "word": u.original,
            "root": u.root,
            "task": task
        })
    return {"results": result}

# ══════════════════════════════════════════════════════
# § 4 — واجهة تفاعلية 🔥
# ══════════════════════════════════════════════════════

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<title>Al-Jawhara LMM</title>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">

<h2>Al-Jawhara LMM 🚀</h2>

<input id="inputText" placeholder="اكتب جملة..." style="width:300px; padding:10px;">
<br><br>
<button onclick="analyze()">تحليل</button>

<pre id="output" style="margin-top:20px; text-align:left;"></pre>

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
    document.getElementById("output").textContent =
        JSON.stringify(data, null, 2);
}
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT
