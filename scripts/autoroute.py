#!/usr/bin/env python3
import argparse,json,os,subprocess,tempfile,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('pcb'); ap.add_argument('--output',required=True); ap.add_argument('--passes',type=int,default=500); a=ap.parse_args()
jar=os.getenv('FREEROUTING_JAR','/opt/freerouting/freerouting.jar')
if not Path(jar).exists(): raise SystemExit(f'FreeRouting JAR not found: {jar}')
work=Path(tempfile.mkdtemp(prefix='circuitvortex-route-')); dsn=work/'input.dsn'; ses=work/'routed.ses'

def run(cmd,timeout=1200):
    r=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
    if r.returncode: raise RuntimeError(r.stderr or r.stdout or f'command failed: {cmd}')
    return r
run(['python3',str(ROOT/'scripts/kicad_specctra_bridge.py'),'export',a.pcb,str(dsn)])
run(['java','-jar',jar,'-de',str(dsn),'-do',str(ses),'-inc','GND','-mp',str(a.passes)],timeout=1500)
if not ses.exists(): raise SystemExit('FreeRouting completed without a SES file')
run(['python3',str(ROOT/'scripts/kicad_specctra_bridge.py'),'import',a.pcb,str(ses),a.output])
print(json.dumps({'status':'complete','output':a.output,'dsn':str(dsn),'ses':str(ses),'passes':a.passes}))
