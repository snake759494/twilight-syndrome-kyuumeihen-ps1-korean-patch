import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from cmap import ROWS
COMMON='　'+''.join(ROWS)
def nargs(t):
    if (t&0xc000) in (0x4000,0xc000):
        sub=(t>>8)&0x3f; lo=t&0xff
        if sub in (1,8,0xd,0x10,0x11,0x12): return 1
        if sub in (0x16,0x17,0x18) and lo<2: return 1
        if sub==0xe and lo in (1,3,4): return 1
    return 0
def parse(tk):
    """[(kind,value)] kind: H header, G glyph, C control, A arg, E end"""
    res=[('H',tk[0])]; i=1
    while i<len(tk):
        t=tk[i]
        if t==0xffff: res.append(('E',t)); i+=1; res+= [('X',x) for x in tk[i:]]; break
        if (t&0xc000)==0: res.append(('G',t))
        else:
            res.append(('C',t)); n=nargs(t)
            for k in range(n): i+=1; res.append(('A',tk[i]))
        i+=1
    return res
def render(p,cmap):
    s=''
    for k,v in p:
        if k=='G':
            c=v&0xfff
            s+= cmap.get(c,'{%03x}'%c) if c>=len(COMMON) else COMMON[c]
            if v&0xf000: s+='<g%04x>'%v
        elif k=='C':
            if v==0x8100: s+='\n'
            else: s+='[%04x]'%v
        elif k=='A': s+='(%04x)'%v
        elif k=='H': s+='#%x '%v
        elif k=='E': s+='[END]'
        else: s+='~%04x'%v
    return s
