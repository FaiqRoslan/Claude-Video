import json,sys
sys.path.insert(0,'.')
from cues import CUES
W=json.load(open('words.json')); DUR=703.58
prev=-1
for i,(a,b,*_) in enumerate(CUES):
    assert a==prev+1,(i,a,prev); prev=b
assert prev==len(W)-1
def span(a,b,nxt):
    st=W[a]['s']; return st, min(nxt, max(W[b]['e'],st+1.0)+1.2)
# greedy merge of consecutive speech cues when too fast
C=[list(c) for c in CUES]
def nxt_start(i,L): return W[L[i+1][0]]['s'] if i+1<len(L) else DUR
changed=True
while changed:
    changed=False
    for i in range(len(C)-1):
        a,b,k,ar,ms,ref=C[i]; a2,b2,k2,ar2,ms2,ref2=C[i+1]
        if k!='s' or k2!='s': continue
        st,en=span(a,b,nxt_start(i,C)); cps=len(ms)/(en-st)
        st2,en2=span(a2,b2,nxt_start(i+1,C)); cps2=len(ms2)/(en2-st2)
        merged=ms+' '+ms2
        if max(cps,cps2)>23 and len(merged)<=100 and (en2-st)<=7.5:
            C[i]=[a,b2,'s','',merged,'']; del C[i+1]; changed=True; break
out=[]
for i,(a,b,k,ar,ms,ref) in enumerate(C):
    st,en=span(a,b,nxt_start(i,C))
    out.append(dict(start=round(st,2),end=round(en,2),kind=k,ar=ar,ms=ms,ref=ref,w=[a,b]))
json.dump(out,open('cues.json','w'),ensure_ascii=False,indent=1)
def ts(t): return f"{int(t//60)}:{t%60:05.2f}"
fast=0
for c in out:
    d=c['end']-c['start']; cps=len(c['ms'])/d; fast+=cps>23
    print(f"{ts(c['start'])}–{ts(c['end'])} [{c['kind']}] {cps:4.0f}cps | {c['ms']}")
print(len(out),'cues; fast>23cps:',fast)
