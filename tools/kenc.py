# 한국어 문자열 -> 게임 바이트 (한글은 0x889F부터 순차 SJIS 코드에 배정)
from hook import code_for_index, small_code
class Charset:
    def __init__(s,chars):
        s.chars=sorted(set(c for c in chars if '\uac00'<=c<='\ud7a3'))
        s.code={c:code_for_index(i) for i,c in enumerate(s.chars)}
    def enc(s,text):
        out=bytearray()
        for c in text:
            if c in s.code: out+=s.code[c].to_bytes(2,'big')
            else:
                b=c.encode('cp932')
                out+=b
        return bytes(out)


class SmallCharset:
    def __init__(s, chars):
        s.chars = sorted(set(c for c in chars if '가' <= c <= '힣'))
        s.code = {c: small_code(i) for i, c in enumerate(s.chars)}

    def enc(s, text):
        out = bytearray()
        for c in text:
            if c in s.code:
                out += s.code[c].to_bytes(2, 'big')
            else:
                b = c.encode('ascii')
                out += b
        return bytes(out)


BYTE_CODES = list(range(0x01, 0x20)) + list(range(0x60, 0x100))


class ByteCharset:
    """전술(GN_MAIN) 반각 이름: 음절당 1바이트(8x8 셀 번호)"""
    def __init__(s, chars):
        s.chars = sorted(set(c for c in chars if '가' <= c <= '힣'))
        assert len(s.chars) <= len(BYTE_CODES), len(s.chars)
        s.code = {c: BYTE_CODES[i] for i, c in enumerate(s.chars)}

    def enc(s, text):
        out = bytearray()
        for c in text:
            if c in s.code:
                out.append(s.code[c])
            else:
                b = c.encode('ascii'); assert 0x20 <= b[0] < 0x60, c
                out += b
        return bytes(out)
