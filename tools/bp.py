import struct,re
HEX=re.compile(r'^[0-9a-fA-Fx]+$')
def regs():
    for k in range(5):
        r=e.cmd('g')
        if HEX.match(r) and len(r)>=38*8: break
    return [struct.unpack('<I',bytes.fromhex(r[i*8:i*8+8].replace('x','0')))[0] for i in range(len(r)//8)]
def wait_stop(timeout=60):
    e.sock.settimeout(timeout)
    try: return e._recv()
    finally: e.sock.settimeout(None)
