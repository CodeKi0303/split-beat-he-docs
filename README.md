# Split-Beat HE 사용 설명서

Split-Beat HE(C86) 사용자 가이드 정적 사이트입니다. Studio(`studio.codekilab.com`)와 별도로 `docs.codekilab.com`에 배포합니다.

- `site/` — 배포되는 파일 전체 (`index.html`, `style.css`, `guide.js`, `theme.js`, `img/`, `_headers`)
- `tools/check_site.mjs` — 링크·앵커·이미지 alt/크기 검사 (`node tools/check_site.mjs site`)

## 미리보기

```sh
python -m http.server 8890 --bind 127.0.0.1 --directory site
```

## 배포

`main`에 `site/` 변경을 push하면 GitHub Actions가 Cloudflare Pages 프로젝트 `split-docs`에 배포하고 `docs.codekilab.com` 도메인을 연결합니다. 저장소에 Studio와 같은 `CLOUDFLARE_ACCOUNT_ID` 변수와 `CLOUDFLARE_API_TOKEN` Secret을 설정해야 합니다.

## 화면 이미지

`site/img/`의 Studio 화면은 Studio의 테스트용 HID 시뮬레이터로 캡처했습니다(실제 장치 아님). Studio UI가 바뀌면 다시 캡처하세요.
