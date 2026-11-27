import os
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Literal
from app.engine import Document, run

app = FastAPI(title='VAF AI Agent Starter Kit', version='0.1.2')
ROOT = Path(__file__).resolve().parents[1]
class InputDocument(BaseModel):
    id: str = Field(min_length=1,max_length=100)
    text: str = Field(min_length=1,max_length=12000)
class AgentRequest(BaseModel):
    question: str = Field(min_length=1,max_length=2000)
    mode: Literal['research','document','task'] = 'research'
    provider: Literal['demo','openai','ollama','gemini'] = 'demo'
    documents: list[InputDocument] | None = Field(default=None,max_length=20)
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/',response_class=HTMLResponse)
def home(): return (ROOT/'app'/'demo.html').read_text(encoding='utf-8')
@app.post('/v1/agents/run')
def execute(req: AgentRequest):
    if req.provider != 'demo' and os.getenv('ENABLE_LLM','false').lower() != 'true':
        raise HTTPException(403,'External/local model calls are disabled by server configuration')
    docs = [Document(**d.model_dump()) for d in req.documents] if req.documents is not None else [Document(**d) for d in json.loads((ROOT/'examples/documents.json').read_text(encoding='utf-8'))]
    if len({d.id for d in docs}) != len(docs): raise HTTPException(422,'Document IDs must be unique')
    try: return run(req.question,docs,req.mode,req.provider)
    except ValueError as e: raise HTTPException(400,str(e))
    except Exception: raise HTTPException(502,'Model provider request failed')
