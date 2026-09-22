#!/usr/bin/env python3
import argparse,json,re,shutil
from pathlib import Path
try:
    from scripts.common import save_json,utc_now
except ImportError:
    from common import save_json,utc_now
SUPPORTED={"remove_silkscreen","resize_via","change_track_width"}
ap=argparse.ArgumentParser(); ap.add_argument('operation'); ap.add_argument('pcb'); ap.add_argument('--output'); ap.add_argument('--parameters',default='{}'); a=ap.parse_args()
if a.operation not in SUPPORTED: raise SystemExit('Unsupported operation: '+a.operation)
src=Path(a.pcb); out=Path(a.output) if a.output else src.with_name(src.stem+'_modified'+src.suffix); text=src.read_text(encoding='utf-8'); params=json.loads(a.parameters); changed=0
if a.operation=='remove_silkscreen':
    layers=set(params.get('layers',['F.SilkS','B.SilkS']))
    lines=text.splitlines(True); keep=[]; current_layer=None
    # Remove complete top-level graphic records conservatively by line-block tracking.
    i=0
    while i<len(lines):
        line=lines[i]
        if re.search(r'\(fp_(line|rect|circle|arc|poly|text)\b',line) or re.search(r'\(gr_(line|rect|circle|arc|poly|text)\b',line):
            depth=line.count('(')-line.count(')'); block=[line]; j=i+1
            while depth>0 and j<len(lines): block.append(lines[j]); depth+=lines[j].count('(')-lines[j].count(')'); j+=1
            blocktxt=''.join(block); lm=re.search(r'\(layer\s+"?([^\s")]+)',blocktxt)
            if lm and lm.group(1) in layers: changed+=1; i=j; continue
            keep.extend(block); i=j; continue
        keep.append(line); i+=1
    text=''.join(keep)
elif a.operation=='resize_via':
    diameter=str(params.get('diameter_mm',params.get('diameter',0.8))); drill=str(params.get('drill_mm',params.get('drill',0.4)))
    def repl(m):
        nonlocal_changed[0]+=1; return m.group(1)+diameter+m.group(2)+drill+m.group(3)
    nonlocal_changed=[0]
    pattern=r'(\(via\s+\(at\s+[^\n]+?\)\s+\(size\s+)([0-9.]+)(\)\s+\(drill\s+)([0-9.]+)(\))'
    text,n=re.subn(pattern,lambda m:m.group(1)+diameter+m.group(3)+drill+m.group(5),text)
    changed=n
elif a.operation=='change_track_width':
    width=str(params.get('width_mm',params.get('width',0.25))); text,n=re.subn(r'(\(segment\s+[^\n]*?\n\s*\(width\s+)[0-9.]+(\))',r'\g<1>'+width+r'\2',text); changed=n
if changed==0: raise SystemExit('No matching geometry was changed')
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding='utf-8')
r={'status':'complete','timestamp':utc_now(),'operation':a.operation,'input':str(src),'output':str(out),'parameters':params,'changed_objects':changed}
save_json(out.with_suffix(out.suffix+'.operation.json'),r); print(json.dumps(r,indent=2))
