import re
TAG=re.compile(r'\{([0-9a-fg][0-9a-f:]*)\}')
def tokens(s,cmap):
    """태그 문자열 -> u16 토큰 목록"""
    out=[]; i=0
    while i<len(s):
        ch=s[i]
        if ch=='{':
            j=s.index('}',i); t=s[i+1:j]
            if t.startswith('g'): out.append(int(t[1:],16))
            else: out+= [int(x,16) for x in t.split(':')]
            i=j+1; continue
        if ch=='\n': out.append(0x8100)
        elif ch=='　': out.append(0)
        else: out.append(cmap[ch])
        i+=1
    return out
def tags(s): return [m.group(0) for m in TAG.finditer(s)]
def plain(s): return TAG.sub('',s)
