# 재빌드

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 쓰고, **그 상위 폴더**에서 원본 디스크와 글꼴을 찾습니다.

```
<상위 폴더>/
  Twilight Syndrome - Kyuumei-hen (Japan).bin   ← README의 해시와 일치해야 함
  NanumSquareNeo-cBd.ttf  NanumSquareNeo-dEb.ttf  SeoulHangangM.ttf  SeoulHangangEB.ttf
  <이 저장소>/
    fonts/Galmuri11.ttf
```

- Python 3.13, `numpy`, `Pillow`, `keystone-engine`
- 글꼴 출처는 `docs/FONT_CREDITS.md`
- xdelta3 (배포 파일을 만들 때만)

## 빌드

저장소 폴더에서 실행합니다.

```powershell
python -I tools/extract.py "../Twilight Syndrome - Kyuumei-hen (Japan).bin" orig   # 디스크 파일 → orig/
python build.py "../Twilight Syndrome - Kyuumei-hen (Korean).bin"
```

`keystone-engine`을 사용자 site-packages에 설치했다면 `build.py`는 `-I` 없이 실행하세요. 결과 BIN의 SHA-256이 `release_manifest.json`의 `output_bin_sha256`과 같아야 합니다. 챕터 타이틀 카드를 다시 압축하는 데 몇 분 걸립니다(`NOGFX=1`이면 그림 글자를 건너뜁니다).

## 배포 파일

```powershell
xdelta3 -e -0 -S none -A -s "Twilight Syndrome - Kyuumei-hen (Japan).bin" "Twilight Syndrome - Kyuumei-hen (Korean).bin" TwilightSyndrome_Kyuumeihen_PS1_KO_v1.1.xdelta
```

## 번역 수정

- 대사: `text/ko/<챕터>_<파일>_<엔트리>.json`의 `ko`. 원문은 `python -I tools/extract_text.py`로 `text/ja/`에 뽑아 같은 `id`끼리 대조합니다(게임 글꼴을 OCR로 읽으므로 한자 오인식이 섞입니다). `\n`은 줄바꿈, `{....}`는 제어 태그이며 원문과 같은 순서·개수로 둬야 합니다. 검사는 `python tools/chk.py <이름>`. 번역 규칙은 `docs/TRANSLATION_GUIDE.md`.
- 그림 글자: `tools/gfxpatch.py`의 `CARDS`·`MENU`·`MEM`·`LABELS` 사전.

## 화면 확인

`tools/emu.py`·`tools/run.py`는 DuckStation 휴대용 복사본을 백그라운드로 띄워 키 입력·메모리 읽기·스크린샷을 합니다. 에뮬레이터는 저장소에 넣지 않았습니다.
