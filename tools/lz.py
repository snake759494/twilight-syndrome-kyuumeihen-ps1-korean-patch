# 게임 압축 (CAP*.EXE 0x8007681c)
def dec(b,o=0):
    out=bytearray()
    while True:
        c=b[o]; o+=1
        if c<0x80:
            n=c+1; out+=b[o:o+n]; o+=n
        elif c<0xc0:
            n=c-0x7d; out+=bytes([b[o]])*n; o+=1
        elif c<0xe0:
            n=c-0xbc; d=b[o]<<8|b[o+1]; o+=2; s=len(out)-d
            for k in range(n): out.append(out[s+k])
        elif c<0xf0:
            n=c-0xdc; st=b[o]; v=b[o+1]; o+=2
            for k in range(n): out.append(v&0xff); v+=st
        elif c==0xff: return bytes(out),o
def comp_tokens(data):
    """탐욕 압축 토큰: ('L',바이트) / ('R',길이,값) / ('M',길이,거리). 3바이트 해시 체인"""
    n=len(data); toks=[]; heads={}; prev=[-1]*n; i=0
    def ins(p):
        if p+3<=n:
            k=data[p:p+3]; prev[p]=heads.get(k,-1); heads[k]=p
    while i<n:
        r=1
        while i+r<n and data[i+r]==data[i] and r<66: r+=1
        bl=0;bd=0
        if r<35 and i+3<=n:
            s_=heads.get(data[i:i+3],-1); tries=0
            while s_>=0 and i-s_<=0xffff and tries<512:
                L=0
                while i+L<n and L<35 and data[s_+L]==data[i+L]: L+=1
                if L>bl: bl=L;bd=i-s_
                if bl==35: break
                s_=prev[s_]; tries+=1
        if r>=3 and r>=bl: toks.append(('R',r,data[i])); k=r
        elif bl>=4: toks.append(('M',bl,bd)); k=bl
        else: toks.append(('L',data[i])); k=1
        for p in range(i,i+k): ins(p)
        i+=k
    return toks
def encode(toks,lit_chunks=None):
    out=bytearray(); lit=bytearray()
    def flush():
        nonlocal lit
        while lit:
            k=lit[:128]; out.append(len(k)-1); out.extend(k); lit=lit[128:]
    for t in toks:
        if t[0]=='L': lit.append(t[1]); continue
        flush()
        if t[0]=='R': out+=bytes([0x7d+t[1],t[2]])
        else: out+=bytes([0xbc+t[1],t[2]>>8,t[2]&0xff])
    flush(); out.append(0xff); return bytes(out)
def comp(data): return encode(comp_tokens(data))
def _cost(toks):
    c=0; run=0
    for t in toks:
        if t[0]=='L': run+=1; continue
        if run: c+=run+(run+127)//128; run=0
        c+=2 if t[0]=='R' else 3
    if run: c+=run+(run+127)//128
    return c
def comp_fit(d,target):
    """압축 결과 길이를 정확히 target으로 맞춤(뒤쪽 토큰을 리터럴로 풀고 리터럴 덩어리를 쪼개 채움)"""
    toks=comp_tokens(d); n=len(d)
    if _cost(toks)+1>target: raise ValueError('too big')
    # 앞 i개 토큰 유지, 나머지는 리터럴(m바이트)
    pos=[0]
    for t in toks: pos.append(pos[-1]+(1 if t[0]=='L' else t[1]))
    pre=[0]; run=0; c=0
    # 접두부 비용(리터럴 연속 고려)은 직접 계산
    for i in range(len(toks),-1,-1):
        head=toks[:i]; m=n-pos[i]
        # head 끝의 리터럴과 꼬리 리터럴은 별도 덩어리로 둔다
        A=_cost(head)
        lo=A+m+(m+127)//128+1; hi=A+2*m+1
        if lo<=target<=hi: break
    else: raise ValueError('fit fail')
    out=bytearray(encode(head)[:-1]); rest=d[pos[i]:]
    nch=(m+127)//128+(target-lo); sizes=[1]*nch; rem=m-nch
    for j in range(nch):
        a=min(127,rem); sizes[j]+=a; rem-=a
    k=0
    for s_ in sizes: out.append(s_-1); out+=rest[k:k+s_]; k+=s_
    out.append(0xff); assert len(out)==target and dec(bytes(out))[0]==d
    return bytes(out)
