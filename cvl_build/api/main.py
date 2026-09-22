from __future__ import annotations
import json, os, shutil, subprocess, threading, uuid, zipfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT=Path(os.getenv('PCB_LAB_ROOT', Path(__file__).resolve().parents[1]))
JOBS=ROOT/'runtime'/'jobs'; JOBS.mkdir(parents=True,exist_ok=True)
MAX_UPLOAD=int(os.getenv('MAX_UPLOAD_BYTES', '52428800'))
app=FastAPI(title='CircuitVortex PCB Lab API', version='2.0.0')

class Action(BaseModel):
    action: str
    parameters: dict = {}


def safe_extract(z: zipfile.ZipFile, dest: Path):
    for info in z.infolist():
        p=(dest/info.filename).resolve()
        if not str(p).startswith(str(dest.resolve())+os.sep): raise ValueError('zip path traversal')
        if info.is_dir(): p.mkdir(parents=True,exist_ok=True)
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            with z.open(info) as src, open(p,'wb') as dst: shutil.copyfileobj(src,dst)


def job_json(jid):
    p=JOBS/jid/'job.json'
    return json.loads(p.read_text()) if p.exists() else None

def save(jid,d): (JOBS/jid/'job.json').write_text(json.dumps(d,indent=2))

def run(jid, action):
    job=job_json(jid); job['status']='running'; job['stage']=action; save(jid,job)
    try:
        cmd=['python3','-m','worker.pipeline','--job',str(JOBS/jid),'--action',action]
        proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=1800)
        (JOBS/jid/'stdout.log').write_text(proc.stdout); (JOBS/jid/'stderr.log').write_text(proc.stderr)
        if proc.returncode: raise RuntimeError(proc.stderr[-4000:] or f'worker exited {proc.returncode}')
        job=job_json(jid); job['status']='complete'; job['stage']='complete'; save(jid,job)
    except Exception as e:
        job=job_json(jid) or {}; job['status']='failed'; job['stage']='failed'; job['error']=str(e); save(jid,job)

@app.get('/health')
def health(): return {'status':'ok','service':'circuitvortex-pcb-lab'}

@app.post('/api/jobs')
async def create_job(file: UploadFile=File(...)):
    name=Path(file.filename or 'upload.kicad_pcb').name
    if not (name.lower().endswith('.kicad_pcb') or name.lower().endswith('.zip')): raise HTTPException(400,'Upload a .kicad_pcb or .zip')
    jid=uuid.uuid4().hex; root=JOBS/jid; root.mkdir(parents=True)
    raw=root/name; size=0
    with raw.open('wb') as f:
        while chunk:=await file.read(1024*1024):
            size+=len(chunk)
            if size>MAX_UPLOAD: shutil.rmtree(root); raise HTTPException(413,'Upload too large')
            f.write(chunk)
    if name.lower().endswith('.zip'):
        try:
            with zipfile.ZipFile(raw) as z: safe_extract(z,root/'input')
        except Exception as e: shutil.rmtree(root); raise HTTPException(400,f'Invalid zip: {e}')
    else:
        (root/'input').mkdir(); shutil.copy2(raw,root/'input'/name)
    board=next((p for p in (root/'input').rglob('*.kicad_pcb')),None)
    if not board: shutil.rmtree(root); raise HTTPException(400,'No .kicad_pcb found in upload')
    d={'id':jid,'filename':name,'board':str(board.relative_to(root)),'status':'queued','stage':'queued','actions':[]}
    save(jid,d)
    threading.Thread(target=run,args=(jid,'analyze'),daemon=True).start()
    return d

@app.get('/api/jobs/{jid}')
def get_job(jid):
    d=job_json(jid)
    if not d: raise HTTPException(404,'Job not found')
    report=JOBS/jid/'report.json'
    if report.exists(): d['report']=json.loads(report.read_text())
    return d

@app.post('/api/jobs/{jid}/actions')
def action(jid, body:Action):
    if not job_json(jid): raise HTTPException(404,'Job not found')
    allowed={'analyze','drc','dfm','fix','autoroute','verify','pipeline'}
    if body.action not in allowed: raise HTTPException(400,f'Unsupported action: {body.action}')
    job=job_json(jid); job['actions'].append({'action':body.action,'parameters':body.parameters}); save(jid,job)
    threading.Thread(target=run,args=(jid,body.action),daemon=True).start()
    return {'accepted':True,'job_id':jid,'action':body.action}

@app.get('/api/jobs/{jid}/download/{name}')
def download(jid,name):
    p=(JOBS/jid/'output'/Path(name).name).resolve(); out=(JOBS/jid/'output').resolve()
    if not str(p).startswith(str(out)+os.sep) or not p.exists(): raise HTTPException(404,'Artifact not found')
    return FileResponse(p,filename=p.name)
