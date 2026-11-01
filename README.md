# 트와일라잇 신드롬 ~구명편~ PS1 한글패치

PS1 일본판 **トワイライトシンドローム ～救命編～ (SLPS-00405)**용 비공식 한국어 패치입니다. 다섯 번째 소문부터 열 번째 소문, 종장까지 **모든 챕터의 대사·선택지**를 한국어로 바꿨습니다. **챕터 타이틀 카드, 타이틀 메뉴, 진행 메뉴, 장소 이름, 엔딩 문구, 메모리 카드 안내 같은 그림 글자**도 한글로 다시 그렸습니다. 현재 배포판은 **v1.0 (2026-11-01)**입니다.

[패치 다운로드](https://github.com/snake759494/twilight-syndrome-kyuumeihen-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 한글패치 **TwilightSyndrome_Kyuumeihen_PS1_KO_v1.0.xdelta**뿐입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 원본·완성 디스크 이미지, 추출한 게임 파일, 일본어 원문, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

전편 『~탐색편~』 한글패치는 [twilight-syndrome-tansakuhen-ps1-korean-patch](https://github.com/snake759494/twilight-syndrome-tansakuhen-ps1-korean-patch)에 있습니다.

## 게임 소개 및 대상 버전

『トワイライトシンドローム ～救命編～』은 휴먼이 1996년에 PS1으로 낸 호러 어드벤처 게임으로, 『~탐색편~』의 후편입니다. 히나시로 고교의 유카리·치사토·미카가 또다시 소문을 쫓으며 사건의 진상에 다가갑니다. 탐색편의 세이브 데이터를 이어받을 수 있습니다.

이 패치는 **PS1 일본판 SLPS-00405의 BIN/CUE 이미지(단일 트랙, MODE2/2352)**에만 적용됩니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SLPS-00405 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 1개) |
| 원본 BIN 크기 | 747,296,256 바이트 |
| **원본 BIN MD5** | `2039ce4c20617f8dfce6d0ded0835ebb` |
| 원본 BIN SHA-1 | `30c5a44525a73cf3690062f0937bac102ac4acc0` |
| 원본 BIN SHA-256 | `b832142fc8cf20ca039c177e3f5c1548d8326791ef4b57aa8d66dd59f2f53e57` |
| xdelta 파일 크기 | 5,944,930 바이트 |
| xdelta SHA-256 | `7b7c0deac3ef9b0367cbd24dee39df980794099f45168c9f22d96f11a04325ef` |
| 적용 결과 BIN 크기 | 747,296,256 바이트 (원본과 같음) |
| 적용 결과 BIN SHA-1 | `d0cd9affa9241c5b35ccf18d1b55b1b954bc42e2` |
| 적용 결과 BIN SHA-256 | `f4308bbdeba07d14977f33e230285124bd40e242e6cdc81f964c4402dfb2abb2` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Twilight Syndrome - Kyuumei-hen (Japan).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `TwilightSyndrome_Kyuumeihen_PS1_KO_v1.0.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Twilight Syndrome - Kyuumei-hen (Korean).bin`).
5. 원본 `.cue`를 복사해 결과 BIN과 같은 이름으로 바꾸고, 안의 `FILE "..."` 줄을 결과 BIN 파일 이름으로 고칩니다.

```
FILE "Twilight Syndrome - Kyuumei-hen (Korean).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
```

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Twilight Syndrome - Kyuumei-hen (Japan).bin' '.\TwilightSyndrome_Kyuumeihen_PS1_KO_v1.0.xdelta' '.\Twilight Syndrome - Kyuumei-hen (Korean).bin'
```

해시를 자동으로 검사하고 CUE까지 만들어 주는 도구도 있습니다. Python 3과 xdelta3가 필요하며, 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Twilight Syndrome - Kyuumei-hen (Japan).bin' --patch '.\TwilightSyndrome_Kyuumeihen_PS1_KO_v1.0.xdelta' --output '.\Twilight Syndrome - Kyuumei-hen (Korean).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일과 데이터 내용이 다릅니다). 메모리 카드 세이브는 원본판과 같은 형식이라 그대로 쓸 수 있을 것으로 보지만, 직접 확인하지는 못했습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 대사·선택지 | 다섯~열 번째 소문과 종장, 대본 13개, 대사 블록 1,964개 |
| 글꼴 | 대사창 16×16 한글 비례폭 글꼴(나눔스퀘어 네오 Bold), 챕터별 321~723자 |
| 그림 글자 | 챕터 시작 타이틀 카드 6장(18프레임 애니메이션), 타이틀 「시작/준비」, 진행 메뉴, 장소 이름 28개, 엔딩 문구 4종, 메모리 카드 안내 18종 |

일본어 전용 게임에 한글을 표시하기 위해 챕터별 글꼴 데이터를 새로 만들고, 실행파일의 글꼴 표 참조와 대본 블록 포인터를 고쳤습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다(`docs/TRANSLATION_GUIDE.md`).
- 인명은 일본어 발음대로 적었습니다(하세가와 유카리, 이쓰시마 치사토, 기시이 미카 등).
- 대사창 폭과 원문의 줄 수·제어 코드에 맞춰 줄을 나눴습니다.

### 번역하지 않은 것

- 음성, 동영상
- 로딩 화면의 「タンケン ジュンビチュウ」 애니메이션
- 스태프 크레디트, 제작사 로고·저작권 표기
- 배경 그림 속 글씨

## 알려진 한계

- 모든 화면을 직접 확인하지는 못했습니다. 대사 출력과 타이틀·진행 메뉴는 에뮬레이터로 확인했지만, 챕터 타이틀 카드와 장소 이름은 게임 화면으로 보지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.
- 일곱 번째 소문의 대본 하나(`CAP7 YHLINK 1`)는 원본 자리에 그대로 써 넣어야 해서, 번역이 그 자리에 들어가지 않는 블록은 일본어로 남을 수 있습니다.
- 일부 선택지는 칸 폭 때문에 원문보다 짧게 줄였습니다.
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `build.py` | 전체 빌드(대본 재구성, 글꼴 생성, 실행파일·CDB 교체) |
| `tools/` | 빌드·검증 도구(Python). `kfont.py` 한글 글꼴, `gfxpatch.py` 그림 글자, `lz.py` 압축, `chk.py` 번역 검사, `apply_release.py` 해시 검사 후 적용, `emu.py` DuckStation 테스트 조작 |
| `text/ko/` | 번역. 대본별 `{"id": 블록 번호, "ko": 번역}` |
| `fonts/` | (저장소에 없음) 갈무리 글꼴을 두는 곳 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처, 번역 지침 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
