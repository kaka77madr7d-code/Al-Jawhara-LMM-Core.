"""
Al-Jawhara LMM — Single File Demo
نظام الجوهرة - نسخة نظيفة خالية من الرموز المخفية
"""
from __future__ import annotations
import os
import re
import uvicorn
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import FrozenSet, Optional, List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==========================================
# § 1 — المُحلِّل الصرفي
# ==========================================

CONSONANTS = set("بتثجحخدذرزسشصضطظعغفقكلمنهوي")
SLOT_CHARS  = set("فعل")

PATTERNS = {
    "فَعَلَ":      {"bab": 1,    "tag": "FAL",      "ar": "الباب الأول — المجرد"},
    "فَعَّلَ":     {"bab": 2,    "tag": "FALLAL",   "ar": "الباب الثاني — التفعيل"},
    "فَاعَلَ":     {"bab": 3,    "tag": "FA_AL",      "ar": "الباب الثالث — المفاعلة"},
    "أَفْعَلَ":    {"bab": 4,    "tag": "AF_AL",      "ar": "الباب الرابع — الإفعال"},
    "تَفَعَّلَ":   {"bab": 5,    "tag": "TAFA_AL",    "ar": "الباب الخامس — التفعُّل"},
    "تَفَاعَلَ":   {"bab": 6,    "tag": "TAFAA_AL",   "ar": "الباب السادس — التفاعل"},
    "انْفَعَلَ":   {"bab": 7,    "tag": "INFA_AL",    "ar": "الباب السابع — الانفعال"},
    "افْتَعَلَ":   {"bab": 8,    "tag": "IFTA_AL",    "ar": "الباب الثامن — الافتعال"},
    "اسْتَفْعَلَ": {"bab": 10,   "tag": "ISTAF_AL",   "ar": "الباب العاشر — الاستفعال"},
    "فَاعِل":      {"bab": "AP1", "tag": "FA_IL",      "ar": "اسم فاعل — الباب الأول"},
    "مُفَعِّل":    {"bab": "AP2", "tag": "MUFA_IL",    "ar": "اسم فاعل — الباب الثاني"},
    "مُتَفَعِّل":  {"bab": "AP5", "tag": "MUTAFA",     "ar": "اسم فاعل — الباب الخامس"},
    "مُتَفَاعِل":  {"bab": "AP6", "tag": "MUTAFAA",    "ar": "اسم فاعل — الباب السادس"},
    "يُفَعِّلُ":    {"bab": "PR2", "tag": "YUFA_IL",    "ar": "مضارع — الباب الثاني"},
    "مَفْعُول":    {"bab": "PP1", "tag": "MAF_UL",     "ar": "اسم مفعول — الباب الأول"},
    "مُفَعَّل":    {"bab": "PP2", "tag": "MUFA_AL",    "ar": "اسم مفعول — الباب الثاني"},
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
        if _slot_match(word, pat): return pat, info
    return None, None

def extract_root(word: str) -> str:
    w = _norm(word)
    prefixes = ["يت","مت","است","انت","افت","مس","من","ان","اس","ي","ت","ن","م"]
    for p in sorted(prefixes, key=len, reverse=True):
        if w.startswith(p) and len(w)-len(p) >= 3:
            w = w[len(p):]; break
    suffixes = ["ون","ات","ين","تم","ان","ه","ك","ي","ها","نا","وا"]
    for s in sorted(suffixes, key=len, reverse=True):
        if w.endswith(s) and len(w)-len(s) >= 3:
            w = w[:-len(s)]; break
    return w

@dataclass
class MorphUnit:
    original: str
    root: str
    pattern: Optional[str]
    tag: Optional[str]
    bab_ar: Optional[str]
    position: int

def distill(sentence: str) -> list[MorphUnit]:
    units = []
    for i, word in enumerate(sentence.split()):
        word = word.strip("،.؟!\"'()[]")
        if not word: continue
        root = extract_root(word)
        pat, info = detect_pattern(word)
        units.append(MorphUnit(
            original=word, root=root, pattern=pat,
            tag=info["tag"] if info else None,
            bab_ar=info["ar"] if info else None,
            position=i
        ))
    return units

# ==========================================
# § 2 — الأكسيومات والاستدلال
# ==========================================

class P(Enum):
    TRANSITIVE=auto(); INTRANSITIVE=auto(); REFLEXIVE=auto()
    RECIPROCAL=auto(); CAUSATIVE=auto();   REQUESTIVE=auto()
    ONGOING=auto();    INSTANTANEOUS=auto();ITERATIVE=auto()
    INTENSIVE=auto();  BASE=auto();         UNARY=auto()
    BINARY=auto();     STATEFUL=auto();     STATELESS=auto()
    STATE_CHANGE=auto();HAS_INPUT=auto();   HAS_OUTPUT=auto()
    TRANSFORMS=auto(); GENERATES=auto();    TRANSMITS=auto()
    AGENTIVE=auto();   PATIENTIVE=auto();   PRESENT_ACTIVE=auto()

AXIOMS: dict = {
    P.TRANSITIVE:  frozenset({P.HAS_INPUT, P.TRANSFORMS, P.HAS_OUTPUT}),
    P.REFLEXIVE:   frozenset({P.STATEFUL, P.STATE_CHANGE, P.HAS_INPUT}),
    P.RECIPROCAL:  frozenset({P.BINARY, P.TRANSMITS, P.HAS_INPUT, P.HAS_OUTPUT, P.STATEFUL}),
    P.CAUSATIVE:   frozenset({P.GENERATES, P.HAS_OUTPUT, P.TRANSITIVE}),
    P.REQUESTIVE:  frozenset({P.HAS_INPUT, P.HAS_OUTPUT, P.TRANSMITS, P.BINARY}),
    P.INTENSIVE:   frozenset({P.ITERATIVE, P.ONGOING, P.TRANSITIVE}),
    P.AGENTIVE:    frozenset({P.STATEFUL, P.ONGOING}),
}

TAG_PROPS: dict = {
    "FAL":      frozenset({P.BASE, P.INSTANTANEOUS, P.UNARY, P.STATELESS}),
    "FALLAL":   frozenset({P.INTENSIVE, P.TRANSITIVE, P.ONGOING}),
    "FA_AL":    frozenset({P.RECIPROCAL, P.BINARY, P.TRANSITIVE}),
    "AF_AL":    frozenset({P.CAUSATIVE, P.TRANSITIVE, P.GENERATES}),
    "TAFA_AL":  frozenset({P.REFLEXIVE, P.STATE_CHANGE, P.STATEFUL, P.ONGOING}),
    "TAFAA_AL": frozenset({P.RECIPROCAL, P.REFLEXIVE, P.BINARY, P.STATEFUL, P.ONGOING}),
    "INFA_AL":  frozenset({P.REFLEXIVE, P.STATE_CHANGE, P.PATIENTIVE, P.INTRANSITIVE}),
    "IFTA_AL":  frozenset({P.REFLEXIVE, P.INTENSIVE, P.TRANSITIVE}),
    "ISTAF_AL": frozenset({P.REQUESTIVE, P.TRANSITIVE, P.BINARY, P.HAS_INPUT, P.HAS_OUTPUT}),
    "FA_IL":    frozenset({P.AGENTIVE, P.PRESENT_ACTIVE, P.ONGOING, P.STATEFUL}),
    "MUFA_IL":  frozenset({P.AGENTIVE, P.INTENSIVE, P.TRANSITIVE, P.ONGOING, P.STATEFUL}),
    "MUTAFA":   frozenset({P.AGENTIVE, P.REFLEXIVE, P.STATE_CHANGE, P.STATEFUL, P.ONGOING, P.HAS_INPUT}),
    "MUTAFAA":  frozenset({P.AGENTIVE, P.RECIPROCAL, P.REFLEXIVE, P.BINARY, P.STATEFUL, P.TRANSMITS, P.ONGOING}),
    "YUFA_IL":  frozenset({P.PRESENT_ACTIVE, P.INTENSIVE, P.TRANSITIVE, P.ONGOING, P.HAS_INPUT, P.TRANSFORMS, P.HAS_OUTPUT}),
    "MAF_UL":   frozenset({P.PATIENTIVE, P.STATEFUL, P.STATE_CHANGE}),
    "MUFA_AL":  frozenset({P.PATIENTIVE, P.STATEFUL, P.STATE_CHANGE}),
}

RULES = [
    (90,"DATA_PROCESSOR", frozenset({P.TRANSITIVE,P.TRANSFORMS,P.HAS_INPUT,P.HAS_OUTPUT,P.ONGOING}), frozenset({P.RECIPROCAL,P.REFLEXIVE}), "التعدية + التحويل + الاستمرار = DataProcessor [Q.E.D.]"),
    (90,"NETWORK_SOCKET", frozenset({P.RECIPROCAL,P.BINARY,P.TRANSMITS,P.STATEFUL,P.ONGOING,P.REFLEXIVE}), frozenset({P.PATIENTIVE}), "تبادلية + انعكاسية + ثنائية = NetworkSocket [Q.E.D.]"),
    (85,"UI_GENERATOR", frozenset({P.REFLEXIVE,P.STATE_CHANGE,P.STATEFUL,P.HAS_INPUT,P.ONGOING,P.AGENTIVE}), frozenset({P.RECIPROCAL,P.TRANSMITS}), "انعكاسية + تغيير حالة + فاعلية = Reactive UI [Q.E.D.]"),
    (80,"FACTORY", frozenset({P.CAUSATIVE,P.GENERATES,P.HAS_OUTPUT}), frozenset({P.RECIPROCAL,P.REFLEXIVE}), "تسببية + إيجاد = Factory [Q.E.D.]"),
    (80,"HTTP_CLIENT", frozenset({P.REQUESTIVE,P.BINARY,P.HAS_INPUT,P.HAS_OUTPUT}), frozenset({P.RECIPROCAL,P.INTENSIVE}), "طلبية + ثنائية = HTTP Client [Q.E.D.]"),
    (75,"STATE_MACHINE", frozenset({P.REFLEXIVE,P.STATE_CHANGE,P.PATIENTIVE,P.INTRANSITIVE}), frozenset({P.AGENTIVE,P.RECIPROCAL}), "مفعولية + تغيير حالة = State Machine [Q.E.D.]"),
    (70,"MESSAGE_BROKER", frozenset({P.RECIPROCAL,P.BINARY,P.TRANSITIVE,P.STATEFUL}), frozenset({P.REFLEXIVE}), "تبادلية حالية بلا انعكاسية = Message Broker [Q.E.D.]"),
    (65,"BACKGROUND_AGENT", frozenset({P.AGENTIVE,P.INTENSIVE,P.ONGOING,P.STATEFUL}), frozenset({P.RECIPROCAL,P.REFLEXIVE,P.PRESENT_ACTIVE}), "فاعلية + تكثيف + استمرار = Background Agent [Q.E.D.]"),
    (60,"DATA_OBJECT", frozenset({P.PATIENTIVE,P.STATEFUL}), frozenset({P.AGENTIVE,P.ONGOING}), "مفعولية + حالة بلا فاعلية = Data Object [Q.E.D.]"),
    (10,"BASE_FUNCTION", frozenset({P.BASE,P.INSTANTANEOUS}), frozenset(), "أساسي + آني = Function Call [Q.E.D.]"),
]

def expand(primary):
    props = set(primary)
    changed = True
    while changed:
        changed = False
        for p in list(props):
            new = AXIOMS.get(p, frozenset()) - props
            if new: props |= new; changed = True
    return frozenset(props)

@dataclass
class Inference:
    task: str
    proof: str
    confidence: float
    props: frozenset
    conflict: Optional[str]

def infer(tag: str | None) -> Inference:
    if not tag: return Inference("UNKNOWN","وزن غير معروف",0.0,frozenset(),None)
    expanded = expand(TAG_PROPS.get(tag, frozenset()))
    best_task, best_proof, best_p, best_rule = "UNKNOWN", "لم يُطابق أي قاعدة", -1, None
    for (pri,task,req,forb,proof) in RULES:
        if req.issubset(expanded) and not (forb & expanded):
            if pri > best_p:
                best_p, best_task, best_proof, best_rule = pri, task, proof, (req,forb)
    if best_rule:
        conf = len(best_rule[0] & expanded)/len(best_rule[0]) if best_rule[0] else 1.0
        return Inference(best_task, best_proof, conf, expanded, None)
    return Inference("UNKNOWN", "لم يُطابق أي قاعدة", 0.0, expanded, None)

# ==========================================
# § 3 — مولِّد الكود والواجهة
# ==========================================

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AnalyzeRequest(BaseModel):
    sentence: str

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    units = distill(req.sentence)
    anchors, files = [], []
    for u in units:
        inf = infer(u.tag)
        if inf.task == "UNKNOWN": continue
        conf = round(inf.confidence * 100)
        anchors.append({"word":u.original,"root":u.root,"task":inf.task,"confidence":conf,"stateful":P.STATEFUL in inf.props})
        files.append({"word":u.original,"root":u.root,"pattern":u.pattern,"task":inf.task,"proof":inf.proof,"confidence":conf,"code":f"# Generated Code for {u.original}\nclass {u.root.capitalize()}Logic:\n    pass"})
    return {"sentence":req.sentence, "anchors":anchors, "files":files, "stateful_required": any(a["stateful"] for a in anchors)}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>الجوهرة LMM</title></head>
    <body style="background:#0d1117;color:#c9a84c;text-align:center;padding:50px;font-family:sans-serif;">
    <h1>✦ الجوهرة v2.0 ✦</h1><p>النظام يعمل وجاهز لاستقبال الطلبات عبر API</p></body></html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
