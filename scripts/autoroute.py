import argparse,json,os,subprocess,tempfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pcb'); ap.add_argument('--output',required=True); ap.add_argument('--passes',type=int,default=500); ap.add_argument('--timeout',type=int,default=1200); a=ap.parse_args()
    jar=Path(os.getenv('FREEROUTING_JAR','/opt/freerouting/freerouting.jar'))
    if not jar.exists(): raise SystemExit(f'FreeRouting JAR missing: {jar}')
    work=Path(tempfile.mkdtemp(prefix='circuitvortex-route-')); dsn=work/'input.dsn'; ses=work/'routed.ses'
    def run(cmd, timeout=None):
        r=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        if r.returncode: raise SystemExit((r.stderr or r.stdout or f'command failed: {cmd[0]}').strip())
        return r
    run(['python3','scripts/export_dsn.py',a.pcb,str(dsn)],300)
    run(['java','-jar',str(jar),'-de',str(dsn),'-do',str(ses),'-inc','GND','-mp',str(a.passes)],a.timeout)
    if not ses.exists() or ses.stat().st_size == 0: raise SystemExit('FreeRouting completed without a session file')
    run(['python3','scripts/import_ses.py',a.pcb,str(ses),a.output],300)
    print(json.dumps({'status':'complete','output':a.output,'dsn':str(dsn),'ses':str(ses)}))

if __name__ == '__main__': main()
