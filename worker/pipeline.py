from __future__ import annotations
import argparse,json,os,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def board(job):
    return next((p for p in (job/'input').rglob('*.kicad_pcb')),None)

def cmd(*args, timeout=900): return subprocess.run(args,text=True,capture_output=True,timeout=timeout)

def report(job,stage,data):
    p=job/'report.json'; old=json.loads(p.read_text()) if p.exists() else {}
    old[stage]=data; p.write_text(json.dumps(old,indent=2))

def inspect(job,b):
    r=cmd('python3',str(ROOT/'scripts/validate_pcb.py'),str(b))
    if r.returncode: raise RuntimeError(r.stderr or r.stdout)
    data=json.loads(r.stdout); report(job,'inspection',data); return data

def drc(job,b):
    out=job/'output'; out.mkdir(exist_ok=True); rpt=out/'drc.rpt'
    r=cmd('kicad-cli','pcb','drc','--exit-code-violations','-o',str(rpt),str(b),timeout=900)
    rpt.write_text(r.stdout+'\n'+r.stderr if not rpt.exists() else rpt.read_text())
    data={'returncode':r.returncode,'report':'output/drc.rpt','passed':r.returncode==0}
    report(job,'drc',data)
    if r.returncode not in (0,1): raise RuntimeError(r.stderr or 'KiCad DRC failed to execute')
    return data

def dfm(job,b):
    out=job/'output'/'dfm.json'; r=cmd('python3',str(ROOT/'scripts/dfm_check.py'),str(b))
    if r.returncode: raise RuntimeError(r.stderr or r.stdout)
    out.write_text(r.stdout); data=json.loads(r.stdout); report(job,'dfm',data); return data

def fix(job,b):
    out=job/'output'; target=out/'fixed.kicad_pcb';
    op='remove_silkscreen'; params='{}'
    r=cmd('python3',str(ROOT/'scripts/safe_edit.py'),op,str(b),'--output',str(target),'--parameters',params)
    if r.returncode: raise RuntimeError(r.stderr or r.stdout)
    data=json.loads(r.stdout); report(job,'fix',data); return target

def autoroute(job,b):
    out=job/'output'; target=out/'autorouted.kicad_pcb';
    r=cmd('python3',str(ROOT/'scripts/autoroute.py'),str(b),'--output',str(target),'--passes',os.getenv('FREEROUTING_PASSES','500'),'--timeout',os.getenv('FREEROUTING_TIMEOUT','1200'),timeout=1500)
    if r.returncode: raise RuntimeError(r.stderr or r.stdout)
    data=json.loads(r.stdout); report(job,'autoroute',data); return target

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--job',required=True); ap.add_argument('--action',required=True); a=ap.parse_args()
    job=Path(a.job); b=board(job)
    if not b: raise SystemExit('No board')
    if a.action in ('analyze','pipeline'): inspect(job,b); drc(job,b); dfm(job,b)
    if a.action=='drc': drc(job,b)
    if a.action=='dfm': dfm(job,b)
    if a.action=='fix':
        x=fix(job,b); drc(job,x); dfm(job,x)
    if a.action=='autoroute':
        x=autoroute(job,b); drc(job,x); dfm(job,x)
    if a.action=='verify': drc(job,b); dfm(job,b)
    if a.action=='pipeline':
        x=fix(job,b); y=autoroute(job,x); drc(job,y); dfm(job,y)
    (job/'output').mkdir(exist_ok=True); shutil.copy2(job/'report.json',job/'output'/'summary.json')
if __name__=='__main__': main()
