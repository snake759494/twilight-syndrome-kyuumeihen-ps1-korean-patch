import capstone,struct,sys
def load(p):
    b=open(p,'rb').read(); t0=struct.unpack_from('<I',b,0x18)[0]; return b[0x800:],t0
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
def dis(code,base,a,n):
    o=a-base
    for i in md.disasm(code[o:o+n*4],a): print('%08x  %s %s'%(i.address,i.mnemonic,i.op_str))
if __name__=='__main__':
    c,b=load(sys.argv[1]); dis(c,b,int(sys.argv[2],16),int(sys.argv[3]))
