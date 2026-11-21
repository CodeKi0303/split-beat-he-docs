# Split-Beat HE 사용 설명서

Split-Beat HE(C86) 사용자 가이드 정적 사이트입니다. Studio(`studio.codekilab.com`)와 별도로 `docs.codekilab.com`에 배포합니다.

- `site/` — 배포되는 파일 전체 (`index.html`, `style.css`, `guide.js`, `theme.js`, `img/`, `_headers`)
- `tools/check_site.mjs` — 링크·앵커·이미지 alt/크기 검사 (`node tools/check_site.mjs site`)
- `tools/render_keyboard.py` — 시작하기의 키보드·포트 그림(인라인 SVG)을 실제 CAD(상·하판 DXF, 노브·롤러 STEP)와 C86 PCB의 USB-C 위치(J401 PC, J501·J551 좌우 연결)로 다시 그립니다. 로컬 작업 공간의 `shipping-foam/geometry.py`와 CAD venv가 필요합니다: `.tools/cad-venv/Scripts/python.exe -X utf8 split-beat-he-docs/tools/render_keyboard.py`

## 미리보기

```sh
python -m http.server 8890 --bind 127.0.0.1 --directory site
```

## 배포

`main`에 `site/` 변경을 push하면 GitHub Actions가 Cloudflare Pages 프로젝트 `split-docs`에 배포하고 `docs.codekilab.com` 도메인을 연결합니다. 저장소에 Studio와 같은 `CLOUDFLARE_ACCOUNT_ID` 변수와 `CLOUDFLARE_API_TOKEN` Secret을 설정해야 합니다.

## 화면 이미지

`site/img/`의 Studio 화면은 Studio의 테스트용 HID 시뮬레이터로 캡처했습니다(실제 장치 아님). Studio UI가 바뀌면 다시 캡처하세요.
