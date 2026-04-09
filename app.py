"""
Al-Jawhara LMM — Single File Demo
كل شيء في ملف واحد — بدون مشاكل imports
"""
from __future__ import annotations
import re
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import FrozenSet

# ══════════════════════════════════════════════════════
# § 1 — المُحلِّل الصرفي
# ══════════════════════════════════════════════════════

CONSONANTS = set("بتثجحخدذرزسشصضطظعغفقكلمنهوي")
SLOT_CHARS  = set("فعل")

PATTERNS = {
    "فَعَلَ":      {"bab":1,    "tag":"FAL",      "ar":"الباب الأول — المجرد"},
    "فَعَّلَ":     {"bab":2,    "tag":"FALLAL",   "ar":"الباب الثاني — التفعيل"},
    "فَاعَلَ":     {"bab":3,    "tag":"FA_AL",    "ar":"الباب الثالث — المفاعلة"},
    "أَفْعَلَ":    {"bab":4,    "tag":"AF_AL",    "ar":"الباب الرابع — الإفعال"},
    "تَفَعَّلَ":   {"bab":5,    "tag":"TAFA_AL",  "ar":"الباب الخامس — التفعُّل"},
    "تَفَاعَلَ":   {"bab":6,    "tag":"TAFAA_AL", "ar":"الباب السادس — التفاعل"},
    "انْفَعَلَ":   {"bab":7,    "tag":"INFA_AL",  "ar":"الباب السابع — الانفعال"},
    "افْتَعَلَ":   {"bab":8,    "tag":"IFTA_AL",  "ar":"الباب الثامن — الافتعال"},
    "اسْتَفْعَلَ": {"bab":10,   "tag":"ISTAF_AL", "ar":"الباب العاشر — الاستفعال"},
    "فَاعِل":      {"bab":"AP1","tag":"FA_IL",    "ar":"اسم فاعل — الباب الأول"},
    "مُفَعِّل":    {"bab":"AP2","tag":"MUFA_IL",  "ar":"اسم فاعل — الباب الثاني"},
    "مُتَفَعِّل":  {"bab":"AP5","tag":"MUTAFA",   "ar":"اسم فاعل — الباب الخامس"},
    "مُتَفَاعِل":  {"bab":"AP6","tag":"MUTAFAA",  "ar":"اسم فاعل — الباب السادس"},
    "يُفَعِّل":    {"bab":"PR2","tag":"YUFA_IL",  "ar":"مضارع — الباب الثاني"},
    "مَفْعُول":    {"bab":"PP1","tag":"MAF_UL",   "ar":"اسم مفعول — الباب الأول"},
    "مُفَعَّل":    {"bab":"PP2","tag":"MUFA_AL",  "ar":"اسم مفعول — الباب الثاني"},
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
    for p in sorted(["يت","مت","است","انت","افت","مس","من","ان","اس","ي","ت","ن","م"], key=len, reverse=True):
        if w.startswith(p) and len(w)-len(p) >= 3: w = w[len(p):]; break
    for s in sorted(["ون","ات","ين","تم","ان","ه","ك","ي","ها","نا","وا"], key=len, reverse=True):
        if w.endswith(s) and len(w)-len(s) >= 3: w = w[:-len(s)]; break
    return w

@dataclass
class MorphUnit:
    original: str
    root: str
    pattern: str | None
    tag: str | None
    bab_ar: str | None
    position: int

def distill(sentence: str) -> list[MorphUnit]:
    units = []
    for i, word in enumerate(sentence.split()):
        word = word.strip("،.؟!\"'()[]")
        if not word: continue
        root = extract_root(word)
        pat, info = detect_pattern(word)
        units.append(MorphUnit(
            original=word, root=root,
            pattern=pat,
            tag=info["tag"] if info else None,
            bab_ar=info["ar"] if info else None,
            position=i,
        ))
    return units

# ══════════════════════════════════════════════════════
# § 2 — الأكسيومات والاستدلال
# ══════════════════════════════════════════════════════

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
    (90,"DATA_PROCESSOR",
     frozenset({P.TRANSITIVE,P.TRANSFORMS,P.HAS_INPUT,P.HAS_OUTPUT,P.ONGOING}),
     frozenset({P.RECIPROCAL,P.REFLEXIVE}),
     "التعدية + التحويل + الاستمرار = DataProcessor [Q.E.D.]"),
    (90,"NETWORK_SOCKET",
     frozenset({P.RECIPROCAL,P.BINARY,P.TRANSMITS,P.STATEFUL,P.ONGOING,P.REFLEXIVE}),
     frozenset({P.PATIENTIVE}),
     "تبادلية + انعكاسية + ثنائية = NetworkSocket [Q.E.D.]"),
    (85,"UI_GENERATOR",
     frozenset({P.REFLEXIVE,P.STATE_CHANGE,P.STATEFUL,P.HAS_INPUT,P.ONGOING,P.AGENTIVE}),
     frozenset({P.RECIPROCAL,P.TRANSMITS}),
     "انعكاسية + تغيير حالة + فاعلية = Reactive UI [Q.E.D.]"),
    (80,"FACTORY",
     frozenset({P.CAUSATIVE,P.GENERATES,P.HAS_OUTPUT}),
     frozenset({P.RECIPROCAL,P.REFLEXIVE}),
     "تسببية + إيجاد = Factory [Q.E.D.]"),
    (80,"HTTP_CLIENT",
     frozenset({P.REQUESTIVE,P.BINARY,P.HAS_INPUT,P.HAS_OUTPUT}),
     frozenset({P.RECIPROCAL,P.INTENSIVE}),
     "طلبية + ثنائية = HTTP Client [Q.E.D.]"),
    (75,"STATE_MACHINE",
     frozenset({P.REFLEXIVE,P.STATE_CHANGE,P.PATIENTIVE,P.INTRANSITIVE}),
     frozenset({P.AGENTIVE,P.RECIPROCAL}),
     "مفعولية + تغيير حالة = State Machine [Q.E.D.]"),
    (70,"MESSAGE_BROKER",
     frozenset({P.RECIPROCAL,P.BINARY,P.TRANSITIVE,P.STATEFUL}),
     frozenset({P.REFLEXIVE}),
     "تبادلية حالية بلا انعكاسية = Message Broker [Stateful Reciprocity Law Q.E.D.]"),
    (65,"BACKGROUND_AGENT",
     frozenset({P.AGENTIVE,P.INTENSIVE,P.ONGOING,P.STATEFUL}),
     frozenset({P.RECIPROCAL,P.REFLEXIVE,P.PRESENT_ACTIVE}),
     "فاعلية + تكثيف + استمرار = Background Agent [Q.E.D.]"),
    (60,"DATA_OBJECT",
     frozenset({P.PATIENTIVE,P.STATEFUL}),
     frozenset({P.AGENTIVE,P.ONGOING}),
     "مفعولية + حالة بلا فاعلية = Data Object [Q.E.D.]"),
    (10,"BASE_FUNCTION",
     frozenset({P.BASE,P.INSTANTANEOUS}),
     frozenset(),
     "أساسي + آني = Function Call [Q.E.D.]"),
]

def expand(primary):
    props, changed = set(primary), True
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
    conflict: str | None

def infer(tag: str | None) -> Inference:
    if not tag:
        return Inference("UNKNOWN","وزن غير معروف",0.0,frozenset(),None)
    primary  = TAG_PROPS.get(tag, frozenset())
    expanded = expand(primary)
    best, best_rule, best_p = None, None, -1
    for (pri,task,req,forb,proof) in RULES:
        if req.issubset(expanded) and not (forb & expanded):
            if pri > best_p:
                best_p, best, best_rule = pri, task, (pri,task,req,forb,proof)
    if best_rule:
        conf = len(best_rule[2] & expanded)/len(best_rule[2])
        return Inference(best, best_rule[4], conf, expanded, None)
    conflict = None
    for (pri,task,req,forb,proof) in sorted(RULES,key=lambda x:-x[0]):
        if req.issubset(expanded):
            blocked = forb & expanded
            if blocked:
                conflict = f"قاعدة {task} مرفوضة: {', '.join(p.name for p in blocked)}"
            break
    return Inference("UNKNOWN","لم يُطابق أي قاعدة",0.0,expanded,conflict)

# ══════════════════════════════════════════════════════
# § 3 — مولِّد الكود
# ══════════════════════════════════════════════════════

def _cls(root: str) -> str:
    ar = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    en = "abthjhkddrzssdttaagfqklmnhwyi"
    length = min(len(ar), len(en))
    tr = str.maketrans(ar[:length], en[:length])
    name = (root.translate(tr) or "X").strip()
    return name.capitalize() if name else "X"

def generate_code(task: str, word: str, root: str, pattern: str | None) -> str:
    cls  = _cls(root)
    pat  = pattern or "unknown"
    fn   = _norm(root).lower() or "func"

    if task == "DATA_PROCESSOR":
        return f'''from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class {cls}Processor:
    """
    محرك معالجة البيانات
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: التعدية + التحويل + الاستمرار [Q.E.D.]
    """
    name: str = "{word}"
    pipeline: list = field(default_factory=list)

    def step(self, fn: Callable, label: str = "") -> "{cls}Processor":
        self.pipeline.append((label or fn.__name__, fn))
        return self

    def run(self, data: Any) -> Any:
        for label, fn in self.pipeline:
            data = fn(data)
        return data

    def stream(self, items) -> Any:
        for item in items:
            yield self.run(item)

# مثال فوري
proc = (
    {cls}Processor()
    .step(str.strip,  label="تنظيف")
    .step(str.upper,  label="تحويل")
)
print(proc.run("  {word}  "))'''

    if task == "NETWORK_SOCKET":
        return f'''import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class {cls}Message:
    event:   str
    payload: object
    sender:  str = "anon"
    ts:      str = field(default_factory=lambda: datetime.now().isoformat())

    def encode(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)

class {cls}Protocol(asyncio.Protocol):
    """
    بروتوكول شبكي ثنائي الاتجاه
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: Stateful Reciprocity Law [Q.E.D.]
    """
    def __init__(self):
        self._handlers: dict = {{}}
        self._transport = None

    def on(self, event: str):
        def dec(fn):
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return dec

    async def emit(self, event, payload, sender="server"):
        msg = {cls}Message(event, payload, sender)
        self._transport.write(msg.encode().encode() + b"\\n")

    async def dispatch(self, raw: str):
        d = json.loads(raw)
        for fn in self._handlers.get(d.get("event",""), []):
            await fn(d.get("sender","?"), d.get("payload"))

# مثال فوري
async def demo():
    proto = {cls}Protocol()

    @proto.on("ping")
    async def on_ping(sender, payload):
        print(f"ping from {{sender}}: {{payload}}")

    await proto.dispatch(
        \'{{"event":"ping","payload":{{"n":1}},"sender":"test"}}\'
    )

asyncio.run(demo())'''

    if task == "UI_GENERATOR":
        return f'''import json
from dataclasses import dataclass, field

@dataclass
class UIComponent:
    type:     str
    id:       str
    label:    str  = ""
    props:    dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def add(self, c: "UIComponent") -> "UIComponent":
        self.children.append(c)
        return self

    def to_dict(self) -> dict:
        return {{
            "type": self.type, "id": self.id,
            "label": self.label, "props": self.props,
            "children": [c.to_dict() for c in self.children]
        }}

class {cls}UIGenerator:
    """
    مولِّد الواجهة التفاعلية
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: الانعكاسية + تغيير الحالة [Q.E.D.]
    """
    def __init__(self, title="{word}"):
        self._root = UIComponent("container", "root", title)
        self._n = 0

    def uid(self, p):
        self._n += 1
        return f"{{p}}_{{self._n}}"

    def header(self, text):
        self._root.add(UIComponent("text", self.uid("h"), text,
                                   {{"style": "header"}}))
        return self

    def input(self, label, placeholder=""):
        self._root.add(UIComponent("input", self.uid("i"), label,
                                   {{"placeholder": placeholder}}))
        return self

    def button(self, label, action="submit"):
        self._root.add(UIComponent("button", self.uid("b"), label,
                                   {{"action": action}}))
        return self

    def build(self) -> dict:
        return self._root.to_dict()

# مثال فوري
ui = (
    {cls}UIGenerator()
    .header("{word}")
    .input("أدخل", placeholder="...")
    .button("تنفيذ")
)
print(json.dumps(ui.build(), ensure_ascii=False, indent=2))'''

    if task == "STATE_MACHINE":
        return f'''from enum import Enum
from dataclasses import dataclass, field
from typing import Callable

class {cls}State(Enum):
    IDLE       = "idle"
    PROCESSING = "processing"
    DONE       = "done"
    ERROR      = "error"

@dataclass
class {cls}StateMachine:
    """
    آلة الحالة
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: المفعولية + تغيير الحالة [Q.E.D.]
    """
    state: {cls}State = {cls}State.IDLE
    _transitions: dict = field(default_factory=dict)
    _log: list = field(default_factory=list)

    def on(self, from_s: {cls}State,
              to_s: {cls}State, fn: Callable):
        self._transitions[(from_s, to_s)] = fn
        return self

    def transition(self, to_s: {cls}State, **kwargs) -> bool:
        key = (self.state, to_s)
        if key not in self._transitions:
            self._log.append(f"مرفوض: {{self.state}} -> {{to_s}}")
            return False
        self._transitions[key](**kwargs)
        self._log.append(f"{{self.state}} -> {{to_s}}")
        self.state = to_s
        return True

# مثال فوري
sm = {cls}StateMachine()
sm.on({cls}State.IDLE, {cls}State.PROCESSING,
      lambda: print("بدء المعالجة"))
sm.on({cls}State.PROCESSING, {cls}State.DONE,
      lambda: print("اكتملت"))
sm.transition({cls}State.PROCESSING)
sm.transition({cls}State.DONE)
print(f"الحالة: {{sm.state.value}}")'''

    if task == "MESSAGE_BROKER":
        return f'''from dataclasses import dataclass, field
from typing import Callable, Any
from datetime import datetime

@dataclass
class {cls}Message:
    topic:   str
    payload: Any
    sender:  str = "anon"
    ts:      str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

class {cls}Broker:
    """
    وسيط الرسائل
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: فَاعَلَ -> Stateful (Reciprocity Law Q.E.D.)
    ملاحظة: الوسيط يحتفظ بسجل — ليس اختياراً بل ضرورة منطقية
    """
    def __init__(self):
        self._subs:    dict = {{}}
        self._history: list = []  # الحالة الداخلية الضرورية

    def subscribe(self, topic: str, fn: Callable) -> None:
        self._subs.setdefault(topic, []).append(fn)

    def publish(self, topic: str,
                payload: Any, sender: str = "anon") -> int:
        msg = {cls}Message(topic, payload, sender)
        self._history.append(msg)
        delivered = 0
        for fn in self._subs.get(topic, []):
            fn(msg)
            delivered += 1
        return delivered

    def history(self, topic: str | None = None) -> list:
        if topic:
            return [m for m in self._history
                    if m.topic == topic]
        return list(self._history)

# مثال فوري
broker = {cls}Broker()
broker.subscribe("{word}",
    lambda m: print(f"رسالة: {{m.payload}}"))
broker.publish("{word}", {{"data": "مرحباً"}})
print(f"السجل: {{len(broker.history())}} رسالة")'''

    if task == "FACTORY":
        return f'''from dataclasses import dataclass
from typing import Type, Any

class {cls}Factory:
    """
    مصنع الكائنات
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: التسببية + الإيجاد [Q.E.D.]
    """
    _registry: dict = {{}}

    @classmethod
    def register(cls, name: str):
        def dec(klass):
            cls._registry[name] = klass
            return klass
        return dec

    @classmethod
    def create(cls, name: str, **kwargs) -> Any:
        if name not in cls._registry:
            raise KeyError(f"النوع {{name!r}} غير مسجَّل")
        return cls._registry[name](**kwargs)

@{cls}Factory.register("{word}")
@dataclass
class {cls}Sample:
    value: str = "{word}"

obj = {cls}Factory.create("{word}", value="test")
print(obj)'''

    if task == "HTTP_CLIENT":
        return f'''import asyncio
from dataclasses import dataclass
from typing import Any

@dataclass
class {cls}Request:
    method:   str = "GET"
    endpoint: str = "/"
    payload:  Any = None

class {cls}Client:
    """
    عميل HTTP
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: الطلبية + الثنائية [Q.E.D.]
    """
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self._history: list = []

    async def send(self, req: {cls}Request) -> dict:
        response = {{
            "status": 200,
            "endpoint": req.endpoint,
            "method": req.method,
            "echo": req.payload
        }}
        self._history.append({{"req": req, "res": response}})
        return response

    async def get(self, path: str) -> dict:
        return await self.send({cls}Request("GET", path))

    async def post(self, path: str, data: Any) -> dict:
        return await self.send({cls}Request("POST", path, data))

async def demo():
    client = {cls}Client()
    res = await client.get("/api/{root}")
    print(res)

asyncio.run(demo())'''

    if task == "BACKGROUND_AGENT":
        return f'''import threading
import time
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class {cls}Agent:
    """
    العامل الخلفي المستمر
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: الفاعلية + التكثيف + الاستمرار [Q.E.D.]
    """
    name:     str   = "{word}"
    interval: float = 1.0
    _running: bool  = field(default=False, repr=False)
    _tasks:   list  = field(default_factory=list, repr=False)

    def add_task(self, fn: Callable) -> "{cls}Agent":
        self._tasks.append(fn)
        return self

    def start(self) -> None:
        self._running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        print(f"[{{self.name}}] بدأ التشغيل")

    def stop(self) -> None:
        self._running = False
        print(f"[{{self.name}}] توقف")

    def _loop(self) -> None:
        while self._running:
            for task in self._tasks:
                try: task()
                except Exception as e:
                    print(f"خطأ: {{e}}")
            time.sleep(self.interval)

counter = [0]
def tick():
    counter[0] += 1
    print(f"نبضة #{counter[0]}")

agent = {cls}Agent(interval=0.5).add_task(tick)
agent.start()
time.sleep(1.5)
agent.stop()'''

    if task == "DATA_OBJECT":
        return f'''from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class {cls}DTO:
    """
    كائن نقل البيانات
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: المفعولية + الحالة بلا فاعلية [Q.E.D.]
    frozen=True — غير قابل للتغيير بعد الإنشاء
    """
    id:         str
    data:       object
    source:     str = "{word}"
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def to_dict(self) -> dict:
        return {{
            "id": self.id, "data": self.data,
            "source": self.source,
            "created_at": self.created_at
        }}

dto = {cls}DTO(id="001", data={{"value": "{word}"}})
print(dto.to_dict())'''

    # BASE_FUNCTION أو UNKNOWN
    return f'''from typing import Any

def {fn}(*args: Any, **kwargs: Any) -> Any:
    """
    دالة أساسية
    الكلمة: {word} | الجذر: {root} | الوزن: {pat}
    القانون: أساسي + آني = Function Call [Q.E.D.]
    """
    result = args[0] if args else kwargs
    return result

# مثال فوري
print({fn}("{word}"))'''

# ══════════════════════════════════════════════════════
# § 4 — FastAPI
# ══════════════════════════════════════════════════════

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Al-Jawhara LMM", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

class AnalyzeRequest(BaseModel):
    sentence: str

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    sentence = req.sentence.strip()
    units    = distill(sentence)

    anchors   = []
    files     = []
    conflicts = []
    has_conflict = False

    for u in units:
        inf = infer(u.tag)
        if inf.task == "UNKNOWN":
            if inf.conflict:
                conflicts.append(f"[{u.original}] {inf.conflict}")
                has_conflict = True
            continue

        code = generate_code(inf.task, u.original, u.root, u.pattern)
        conf = round(inf.confidence * 100)

        anchors.append({
            "word":      u.original,
            "root":      u.root,
            "pattern":   u.pattern or "—",
            "bab":       u.bab_ar or "—",
            "task":      inf.task,
            "proof":     inf.proof,
            "confidence": conf,
            "stateful":  P.STATEFUL in inf.props,
        })
        files.append({
            "word":       u.original,
            "root":       u.root,
            "pattern":    u.pattern,
            "task":       inf.task,
            "proof":      inf.proof,
            "confidence": conf,
            "code":       code,
        })

    stateful_required = any(a["stateful"] for a in anchors)

    return {
        "sentence":          sentence,
        "anchors":           anchors,
        "files":             files,
        "has_conflict":      has_conflict,
        "conflicts":         conflicts,
        "stateful_required": stateful_required,
        "primary_task":      anchors[0]["task"] if anchors else "UNKNOWN",
    }

@app.get("/health")
async def health():
    return {"status": "ok", "model": "Al-Jawhara LMM v2.0"}

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>الجوهرة — أول نموذج LMM عربي</title>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--gold:#c9a84c;--dark:#0d1117;--blue:#0d3b6e;--card:#161b22;
  --border:#30363d;--text:#e6edf3;--dim:#8b949e;--green:#3fb950;--red:#f85149}
body{background:var(--dark);color:var(--text);font-family:"IBM Plex Mono",monospace;min-height:100vh}
header{background:linear-gradient(180deg,#0d1117,transparent);border-bottom:1px solid var(--gold);
  padding:32px 24px 24px;text-align:center;position:relative;overflow:hidden}
header::before{content:"";position:absolute;inset:0;opacity:.03;
  background-image:repeating-linear-gradient(0deg,var(--gold) 0,var(--gold) 1px,transparent 1px,transparent 48px),
    repeating-linear-gradient(90deg,var(--gold) 0,var(--gold) 1px,transparent 1px,transparent 48px)}
.logo-sym{font-size:52px;color:var(--gold);line-height:1;margin-bottom:6px}
.logo-t{font-family:"Amiri",serif;font-size:clamp(28px,6vw,52px);font-weight:700;
  color:var(--gold);text-shadow:0 0 40px #c9a84c55}
.logo-s{font-size:12px;color:var(--dim);margin-top:5px;letter-spacing:2px}
.badges{display:flex;gap:8px;justify-content:center;margin-top:12px;flex-wrap:wrap}
.badge{background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:4px 12px;font-size:11px;color:var(--dim)}
.badge.g{border-color:var(--gold);color:var(--gold)}
.main{max-width:880px;margin:0 auto;padding:28px 18px 80px}
.lbl{font-size:11px;color:var(--dim);letter-spacing:3px;margin-bottom:9px;text-align:right}
textarea{width:100%;background:var(--card);border:1px solid var(--border);border-radius:13px;
  padding:16px 18px;font-size:18px;color:var(--text);font-family:"Amiri",serif;
  direction:rtl;text-align:right;resize:none;outline:none;line-height:1.7;
  transition:border-color .3s,box-shadow .3s}
textarea:focus{border-color:var(--gold);box-shadow:0 0 0 1px #c9a84c33}
textarea::placeholder{color:#30363d}
.btn{margin-top:11px;width:100%;background:var(--gold);border:none;border-radius:10px;
  padding:14px;font-size:15px;font-weight:700;color:var(--dark);cursor:pointer;
  font-family:"IBM Plex Mono",monospace;transition:all .2s;letter-spacing:1px}
.btn:hover{background:#e0b85a;transform:translateY(-1px)}
.btn:disabled{background:#333;color:#666;cursor:not-allowed;transform:none}
.samples{margin-top:11px;display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}
.smp{background:#ffffff08;border:1px solid #ffffff12;border-radius:8px;padding:6px 13px;
  font-size:15px;color:var(--dim);cursor:pointer;font-family:"Amiri",serif;transition:all .2s}
.smp:hover{background:#c9a84c22;color:var(--gold);border-color:#c9a84c44}
#proc{display:none;margin:22px 0}
.pstep{background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:11px 15px;display:flex;align-items:center;gap:11px;margin-bottom:7px;
  opacity:0;transform:translateY(8px);transition:all .4s}
.pstep.on{opacity:1;transform:none;border-color:var(--gold)}
.pstep.dn{opacity:.6;border-color:var(--green)}
.picon{font-size:20px;width:26px;text-align:center;flex-shrink:0}
.ptxt{font-size:13px;direction:rtl;text-align:right}
.psub{font-size:11px;color:var(--gold);margin-top:2px}
#res{display:none}
.sumbar{background:var(--card);border:1px solid var(--gold);border-radius:13px;
  padding:18px 22px;margin-bottom:22px;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.stat{text-align:center}
.sv{font-size:24px;font-weight:700;color:var(--gold)}
.sl{font-size:10px;color:var(--dim);margin-top:3px}
.card{background:var(--card);border:1px solid var(--border);border-radius:15px;
  margin-bottom:18px;overflow:hidden;animation:si .4s ease}
@keyframes si{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.ch{padding:16px 18px;display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid var(--border);flex-wrap:wrap;gap:9px}
.wd{font-family:"Amiri",serif;font-size:30px;color:#fff;direction:rtl}
.tb{padding:5px 13px;border-radius:8px;font-size:11px;font-weight:600}
.cmeta{padding:12px 18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));
  gap:9px;border-bottom:1px solid var(--border)}
.mi{background:#ffffff06;border-radius:7px;padding:9px 12px}
.ml{font-size:10px;color:var(--dim);margin-bottom:2px}
.mv{font-size:13px;color:var(--gold);font-family:"Amiri",serif;direction:rtl}
.prf{padding:10px 18px;background:#c9a84c0d;border-right:3px solid var(--gold);
  margin:0 18px 14px;border-radius:3px;font-size:12px;color:#ccc;
  direction:rtl;text-align:right;line-height:1.6}
.cw{border-top:1px solid var(--border)}
.chead{background:#161b22;padding:7px 14px;display:flex;justify-content:space-between;align-items:center}
.dots{display:flex;gap:5px}
.dot{width:10px;height:10px;border-radius:50%}
.cn{font-size:10px;color:var(--dim);font-family:monospace}
.cpbtn{background:#ffffff11;border:1px solid #ffffff22;border-radius:5px;padding:3px 11px;
  color:var(--dim);cursor:pointer;font-size:10px;font-family:monospace;transition:all .2s}
.cpbtn:hover{background:var(--gold);color:var(--dark);border-color:var(--gold)}
pre{padding:18px;font-size:12px;line-height:1.75;overflow-x:auto;
  font-family:"IBM Plex Mono",monospace;color:#d4d4d4;max-height:380px;overflow-y:auto;
  direction:ltr;text-align:left}
.cflx{background:#f851490d;border:1px solid #f8514955;border-radius:11px;padding:14px 18px;margin-bottom:18px}
.cft{color:var(--red);font-size:13px;font-weight:600;margin-bottom:7px;direction:rtl}
.cfi{font-size:12px;color:#ccc;direction:rtl;margin-top:5px;padding-right:11px;border-right:2px solid var(--red)}
.empty{text-align:center;padding:56px 0;color:var(--dim)}
.empty-i{font-size:44px;margin-bottom:14px}
.spin{width:16px;height:16px;border:2px solid #333;border-top-color:var(--dark);
  border-radius:50%;animation:sp .7s linear infinite;display:inline-block;vertical-align:middle}
@keyframes sp{to{transform:rotate(360deg)}}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--dark)}
::-webkit-scrollbar-thumb{background:#333;border-radius:3px}
</style>
</head>
<body>
<header>
  <div class="logo-sym">✦</div>
  <div class="logo-t">الجوهرة</div>
  <div class="logo-s">AL-JAWHARA · LARGE MORPHOLOGY MODEL · v2.0</div>
  <div class="badges">
    <span class="badge g">أول LMM عربي</span>
    <span class="badge">Zero GPU</span>
    <span class="badge">Deterministic</span>
    <span class="badge">Q.E.D.</span>
  </div>
</header>

<div class="main">
  <div style="margin-bottom:28px">
    <div class="lbl">§ أدخِل جملة أو كلمة عربية</div>
    <textarea id="inp" rows="2"
      placeholder="مثال: نظام يُعالِج البيانات ويُرسِلها عبر بروتوكول مُتَفَاعِل"></textarea>
    <button class="btn" id="runBtn" onclick="run()">تحليل وتوليد الكود  ←</button>
    <div class="samples">
      <span class="smp" onclick="pick(this)">يُعالِج</span>
      <span class="smp" onclick="pick(this)">مُتَفَاعِل</span>
      <span class="smp" onclick="pick(this)">مُتَعَلِّم</span>
      <span class="smp" onclick="pick(this)">اسْتَخْرَجَ</span>
      <span class="smp" onclick="pick(this)">انْكَسَرَ</span>
      <span class="smp" onclick="pick(this)">شَفَّرَ</span>
      <span class="smp" onclick="pick(this)">نظام يُشَفِّر البيانات ويُرسِلها</span>
    </div>
  </div>

  <div id="proc">
    <div class="lbl">§ عقل الجوهرة يعمل</div>
    <div class="pstep" id="s1">
      <div class="picon">🔬</div>
      <div class="ptxt">طبقة التقطير<div class="psub" id="s1s">تجريد إلى جذور وأوزان...</div></div>
    </div>
    <div class="pstep" id="s2">
      <div class="picon">⚖️</div>
      <div class="ptxt">محرك الاستدلال<div class="psub" id="s2s">تطبيق قوانين سيبويه والمنطق...</div></div>
    </div>
    <div class="pstep" id="s3">
      <div class="picon">⚙️</div>
      <div class="ptxt">مترجم الأكواد<div class="psub" id="s3s">توليد الكود النظيف...</div></div>
    </div>
  </div>

  <div id="res"></div>

  <div class="empty" id="empty">
    <div class="empty-i">✦</div>
    <div>اكتب كلمة عربية ليُترجِمها الوزن الصرفي إلى كود</div>
    <div style="font-size:11px;color:#444;margin-top:7px">بُني بالمنطق، لا بالإحصاء</div>
  </div>
</div>

<script>
const COLORS={DATA_PROCESSOR:"#e8a317",NETWORK_SOCKET:"#3fb950",
UI_GENERATOR:"#58a6ff",FACTORY:"#bc8cff",HTTP_CLIENT:"#39d353",
STATE_MACHINE:"#f0883e",MESSAGE_BROKER:"#79c0ff",BACKGROUND_AGENT:"#ffa657",
DATA_OBJECT:"#a8b5d1",BASE_FUNCTION:"#8b949e",UNKNOWN:"#f85149"};
const AR={DATA_PROCESSOR:"معالج بيانات",NETWORK_SOCKET:"بروتوكول شبكي",
UI_GENERATOR:"مولِّد واجهة",FACTORY:"مصنع كائنات",HTTP_CLIENT:"عميل HTTP",
STATE_MACHINE:"آلة حالة",MESSAGE_BROKER:"وسيط رسائل",
BACKGROUND_AGENT:"عامل خلفي",DATA_OBJECT:"كائن بيانات",
BASE_FUNCTION:"دالة أساسية",UNKNOWN:"غير محلول"};

function pick(el){
  document.getElementById("inp").value=el.textContent.trim();
  document.getElementById("inp").focus();
}
function delay(ms){return new Promise(r=>setTimeout(r,ms));}
function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function hi(code){
  return code
    .replace(/(#[^\n]*)/g,'<span style="color:#6a9955">$1</span>')
    .replace(/\b(class|def|return|import|from|if|for|in|and|or|not|async|await|print|yield|while|try|except|with|as|pass|raise|lambda|True|False|None)\b/g,'<span style="color:#569cd6">$1</span>')
    .replace(/\b(self)\b/g,'<span style="color:#9cdcfe">$1</span>')
    .replace(/"([^"\\\\]*)"/g,'<span style="color:#ce9178">"$1"</span>')
    .replace(/'([^'\\\\]*)'/g,"<span style='color:#ce9178'>'$1'</span>")
    .replace(/\b(\d+\.?\d*)\b/g,'<span style="color:#b5cea8">$1</span>');
}

window.copyC=async function(i){
  const el=document.getElementById("code"+i);
  try{await navigator.clipboard.writeText(el.innerText);}
  catch(e){const r=document.createRange();r.selectNode(el);
    window.getSelection().removeAllRanges();window.getSelection().addRange(r);}
  const btn=el.closest(".cw").querySelector(".cpbtn");
  btn.textContent="✓ تم"; setTimeout(()=>btn.textContent="نسخ",2000);
};

async function run(){
  const sentence=document.getElementById("inp").value.trim();
  if(!sentence)return;
  document.getElementById("runBtn").disabled=true;
  document.getElementById("runBtn").innerHTML='<span class="spin"></span>  جاري...';
  document.getElementById("empty").style.display="none";
  document.getElementById("res").style.display="none";
  document.getElementById("proc").style.display="block";
  const steps=["s1","s2","s3"];
  const subs=[`تجريد "${sentence.substring(0,15)}"...`,"تطبيق القوانين الحتمية...","توليد الكود..."];
  for(let i=0;i<3;i++){
    await delay(350);
    document.getElementById(steps[i]).classList.add("on");
    document.getElementById(steps[i]+"s").textContent=subs[i];
    if(i>0)document.getElementById(steps[i-1]).classList.add("dn");
  }
  try{
    const r=await fetch("/api/analyze",{method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({sentence})});
    if(!r.ok)throw new Error("خطأ "+r.status);
    const data=await r.json();
    await delay(300);
    document.getElementById("s3").classList.add("dn");
    render(data);
  }catch(e){
    document.getElementById("res").innerHTML=
      `<div class="cflx"><div class="cft">✗ خطأ</div><div class="cfi">${e.message}</div></div>`;
    document.getElementById("res").style.display="block";
  }finally{
    document.getElementById("proc").style.display="none";
    steps.forEach(s=>{const el=document.getElementById(s);el.classList.remove("on","dn");});
    document.getElementById("runBtn").disabled=false;
    document.getElementById("runBtn").innerHTML="تحليل وتوليد الكود  ←";
  }
}

function render(data){
  let html="";
  if(data.has_conflict){
    html+=`<div class="cflx"><div class="cft">⚠ تعارض منطقي</div>${data.conflicts.map(c=>`<div class="cfi">${c}</div>`).join("")}</div>`;
  }
  if(data.anchors&&data.anchors.length>0){
    const sf=data.stateful_required;
    html+=`<div class="sumbar">
      <div class="stat"><div class="sv">${data.anchors.length}</div><div class="sl">مرساة صرفية</div></div>
      <div class="stat"><div class="sv" style="color:${sf?"#3fb950":"#8b949e"}">${sf?"نعم":"لا"}</div><div class="sl">Stateful مطلوب</div></div>
      <div class="stat"><div class="sv" style="color:var(--gold)">${data.files[0]?.confidence||0}%</div><div class="sl">الثقة</div></div>
      <div class="stat"><div class="sv" style="color:#3fb950">Q.E.D.</div><div class="sl">اشتقاق حتمي</div></div>
    </div>`;
  }
  (data.files||[]).forEach((f,i)=>{
    const col=COLORS[f.task]||"#888";
    const arT=AR[f.task]||f.task;
    html+=`<div class="card">
      <div class="ch">
        <div class="wd">${f.word}</div>
        <span class="tb" style="background:${col};color:#000">${arT}</span>
      </div>
      <div class="cmeta">
        <div class="mi"><div class="ml">الجذر</div><div class="mv">${f.root}</div></div>
        <div class="mi"><div class="ml">الوزن</div><div class="mv">${f.pattern||"—"}</div></div>
        <div class="mi"><div class="ml">المهمة</div><div class="mv" style="color:${col}">${f.task}</div></div>
        <div class="mi"><div class="ml">الثقة</div><div class="mv">${f.confidence}%</div></div>
      </div>
      <div class="prf">${f.proof}</div>
      <div class="cw">
        <div class="chead">
          <div class="dots">
            <div class="dot" style="background:#ff5f57"></div>
            <div class="dot" style="background:#ffbd2e"></div>
            <div class="dot" style="background:#28ca41"></div>
          </div>
          <span class="cn">${f.root}_${f.task.toLowerCase()}.py</span>
          <button class="cpbtn" onclick="copyC(${i})">نسخ</button>
        </div>
        <pre id="code${i}">${hi(esc(f.code))}</pre>
      </div>
    </div>`;
  });
  if(!data.files||data.files.length===0){
    html+=`<div class="empty"><div class="empty-i">❓</div><div>لم يُكتشَف وزن صرفي معروف</div></div>`;
  }
  const el=document.getElementById("res");
  el.innerHTML=html; el.style.display="block";
}

document.getElementById("inp").addEventListener("keydown",e=>{
  if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();run();}
});
</script>
</body>
</html>"""
