# 기준 저장소와 작업 재개

사용자 지정일: 2026-09-30 UTC.

| 항목 | 값 |
|---|---|
| 기준 저장소 | [Byeongwook-Heo/terraform-ai-mcp-demo](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo) |
| 공개 범위 | Private; 로그인 및 저장소 접근 권한 필요 |
| 작업 경로 | `/workspace/terraform-ai-mcp-demo` |
| 기본 Branch | `main` |
| Phase 1 검토 Branch | `codex/phase1-terraform-mcp` |
| 기존 main Commit | `53b0f820bbfb99fd447a827f652b29db27d19361` |
| 검토용 PR | [Draft PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1), Open / Draft / 미Merge |
| 구현 Commit | `5f3ecfcea93bf369fa08437038add7be253bbb0a` |
| 게시 결과 | PASS: 작업 Branch 파일의 Git tree가 로컬 검증본과 일치 |
| 원격 CI | SKIPPED: 확인 시 Workflow Run 0개, 실행·성공 증거 없음 |

기존 저장소는 README만 포함했습니다. 기존 README 제목과 Commit 이력을 보존하고, 앞서 격리 환경에서 검증한 Phase 1 산출물을 별도 Branch에 통합했습니다. 이전 `/workspace/terraform-mcp-demo`는 초기 준비 경로이며 앞으로의 기준 저장소가 아닙니다.

## 휴대폰에서 확인하고 이어가기

1. GitHub에 로그인하고 위 저장소에서 `codex/phase1-terraform-mcp` Branch 또는 Draft PR을 엽니다. Merge 전에는 main에서 구현 파일이 보이지 않습니다.
2. README → `reports/progress.md` → `reports/required-inputs.md` → `docs/08-without-pc.md` 순서로 검토합니다. PR의 Files changed에서 코드와 테스트도 확인할 수 있습니다.
3. 다음 Codex Cloud 작업에서 이 저장소를 선택합니다. 기존 PR 보완은 해당 Branch를 지정하고 `AGENTS.md`, `DEMO_SPEC.md`, `START_HERE.md`를 읽도록 요청합니다.
4. PR이 Merge된 뒤 새 작업을 시작한다면 최신 main에서 별도 Branch를 만듭니다. Merge 자체는 이번 작업에서 수행하지 않습니다.

다음 요청 예시:

```text
Byeongwook-Heo/terraform-ai-mcp-demo 저장소의
codex/phase1-terraform-mcp Branch에서 이어서 작업해줘.
AGENTS.md, DEMO_SPEC.md, START_HERE.md와 reports/progress.md를 먼저 읽어줘.
현재는 Phase 1 보완만 진행하고 실제 AWS/HCP 연결·배포, PR Merge,
Module Version Tag 게시 없이 코드·문서와 격리된 검증 결과를 갱신해줘.
```

현재 승인 범위는 기존 저장소의 작업 Branch 게시와 검토용 PR입니다. AWS/HCP 외부 변경, 실제 Registry 게시·조회, Standard Run/Apply는 별도 대상·입력·승인이 필요합니다. CI에는 자격증명 없는 검증만 포함했습니다. 배포 Workflow를 실행하지 않습니다.

Git HTTPS Push의 HTTP 401 이후 연결된 GitHub 앱의 Git Data API로 같은 tree를 게시했습니다. PR 생성 앱 도구의 Internal error 이후 중복 PR이 없음을 조회하고 `gh pr create --draft --body-file`로 PR #1을 만들었습니다. 최종 PR의 base=main, head=codex/phase1-terraform-mcp, Draft=true, merged=false를 확인했습니다. 게시·확인 기록은 `github-publication.json`에 있습니다.
