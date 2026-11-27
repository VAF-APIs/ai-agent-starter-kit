from fastapi.testclient import TestClient
from app.main import app
from app.engine import Document, run
c=TestClient(app)
def test_health(): assert c.get('/health').json()=={'status':'ok'}
def test_demo():
    r=c.post('/v1/agents/run',json={'question':'legacy migration'}); assert r.status_code==200 and 'migration-guide' in r.json()['sources']
def test_missing(): assert run('zebra',[Document('a','apple')])['sources']==[]
def test_plan(): assert run('send email',[],mode='task')['status']=='approval_required'
def test_invalid(): assert c.post('/v1/agents/run',json={'question':'x','mode':'unknown'}).status_code==422
def test_disabled(monkeypatch):
    monkeypatch.delenv('ENABLE_LLM',raising=False)
    assert c.post('/v1/agents/run',json={'question':'x','provider':'openai'}).status_code==403
def test_custom():
    r=c.post('/v1/agents/run',json={'question':'apple','mode':'document','documents':[{'id':'fruit','text':'apple is a fruit'}]});assert r.json()['sources']==['fruit']
def test_duplicate(): assert c.post('/v1/agents/run',json={'question':'x','documents':[{'id':'x','text':'one'},{'id':'x','text':'two'}]}).status_code==422
def test_ui(): assert 'AI Agent Studio' in c.get('/').text

def test_no_evidence_status():
    assert run('zebra',[Document('a','apple')])['status']=='no_evidence'

def test_blank_question():
    assert c.post('/v1/agents/run',json={'question':'   '}).status_code==400

def test_openai_missing_key(monkeypatch):
    monkeypatch.setenv('ENABLE_LLM','true')
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    assert c.post('/v1/agents/run',json={'question':'legacy migration','provider':'openai'}).status_code==400

def test_provider_contracts(monkeypatch):
    import json, io
    import app.engine as engine
    monkeypatch.setenv('ENABLE_LLM','true')
    monkeypatch.setenv('OPENAI_API_KEY','test-only-not-a-real-key')
    monkeypatch.setenv('OLLAMA_URL','http://localhost:11434')
    def fake(request, timeout):
        body=json.loads(request.data)
        assert body['messages'][0]['role']=='system'
        assert body['messages'][1]['role']=='user'
        assert timeout==30
        if request.full_url.startswith('https://api.openai.com/'):
            assert request.get_header('Authorization')=='Bearer test-only-not-a-real-key'
        else:
            assert request.full_url=='http://localhost:11434/v1/chat/completions'
            assert request.get_header('Authorization') is None
        return io.BytesIO(b'{"choices":[{"message":{"content":"Example [migration-guide]"}}]}')
    monkeypatch.setattr(engine,'urlopen',fake)
    for provider in ('openai','ollama'):
        r=c.post('/v1/agents/run',json={'question':'legacy migration','provider':provider})
        assert r.status_code==200 and r.json()['answer']=='Example [migration-guide]'

def test_provider_failure(monkeypatch):
    import app.engine as engine
    monkeypatch.setenv('ENABLE_LLM','true')
    def fail(*args,**kwargs): raise TimeoutError('private details')
    monkeypatch.setattr(engine,'urlopen',fail)
    r=c.post('/v1/agents/run',json={'question':'legacy migration','provider':'ollama'})
    assert r.status_code==502 and 'private details' not in r.text


def test_gemini_contract(monkeypatch):
    import json, io
    import app.engine as engine
    monkeypatch.setenv('ENABLE_LLM','true')
    monkeypatch.setenv('GEMINI_API_KEY','mock-key')
    monkeypatch.setenv('GEMINI_MODEL','gemini-flash-latest')
    def fake(request, timeout):
        assert request.full_url.endswith('/gemini-flash-latest:generateContent')
        assert request.get_header('X-goog-api-key') == 'mock-key'
        assert 'mock-key' not in request.full_url
        body = json.loads(request.data)
        assert body['systemInstruction']['parts'][0]['text']
        assert 'migration-guide' in body['contents'][0]['parts'][0]['text']
        return io.BytesIO(b'{"candidates":[{"content":{"parts":[{"text":"Example [migration-guide]"}]}}]}')
    monkeypatch.setattr(engine,'urlopen',fake)
    r=c.post('/v1/agents/run',json={'question':'legacy migration','provider':'gemini'})
    assert r.status_code==200 and r.json()['answer']=='Example [migration-guide]'

def test_gemini_missing_key(monkeypatch):
    monkeypatch.setenv('ENABLE_LLM','true')
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    assert c.post('/v1/agents/run',json={'question':'legacy migration','provider':'gemini'}).status_code==400

def test_gemini_disabled(monkeypatch):
    monkeypatch.delenv('ENABLE_LLM',raising=False)
    assert c.post('/v1/agents/run',json={'question':'legacy migration','provider':'gemini'}).status_code==403
