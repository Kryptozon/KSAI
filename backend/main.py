from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import openai, uvicorn, uuid
from gtts import gTTS

from agents import agents
from tools import run_tool
from kb import add_to_kb, search_kb
from memory import add_message, get_memory
from crypto import get_crypto_guidelines
from admin import verify_admin, get_admin_dashboard

openai.api_key = "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"

app = FastAPI(title="KS-AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    agent_id = body.get("agent", "default")
    session_id = body.get("session", "global")
    message = body.get("message", "")

    add_message(session_id, "user", message)
    agent = agents.get(agent_id, agents["default"])
    kb_context = search_kb(message)
    memory_context = " ".join([m["content"] for m in get_memory(session_id)])

    extra_context = ""
    if agent_id == "crypto":
        extra_context = get_crypto_guidelines()

    system_prompt = f"""
    You are {agent['name']}.
    {agent['instructions']}
    Use this knowledge if useful: {kb_context}
    Past conversation: {memory_context}
    Extra domain knowledge: {extra_context}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}] + get_memory(session_id) + [{"role": "user", "content": message}]
    )

    reply = response.choices[0].message["content"]

    if reply.startswith("[TOOL:"):
        reply = run_tool(reply, session_id=session_id)

    add_message(session_id, "assistant", reply)
    return {"reply": reply}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8", errors="ignore")
    add_to_kb(text)
    return {"status": f"✅ {file.filename} added to KS-AI knowledge base."}

@app.post("/tts")
async def tts(request: Request):
    body = await request.json()
    text = body.get("text", "")
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text)
    tts.save(filename)
    return {"url": f"/voice/{filename}"}

@app.get("/voice/{filename}")
async def get_voice(filename: str):
    return FileResponse(filename, media_type="audio/mpeg")

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(filename, media_type="application/pdf", filename=filename)

# 🔐 Admin-only dashboard
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(user: str = Depends(verify_admin)):
    return get_admin_dashboard()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
