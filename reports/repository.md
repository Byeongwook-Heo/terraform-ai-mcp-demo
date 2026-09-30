# 기준 저장소와 main 재개

확인일: 2026-09-30 UTC.

| 항목 | 현재 값 |
|---|---|
| 기준 저장소 | [Byeongwook-Heo/terraform-ai-mcp-demo](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo) |
| 공개 범위 | Public; 실제 GitHub API 조회 확인 |
| 기본·후속 작업 Branch | main |
| Phase 1 PR | [PR #1](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/pull/1), 병합 완료 |
| Phase 1 병합 Commit | f7299c10fa1b9376988644d85983d6e24f5add70 |
| 후속 원격 반영 | PASS: Git Data API로 main 게시, 원격 tree/파일 일치 확인 |
| 구현 게시 Commit | faf4b2ce11222d3546306be1dabfdbf09a9b20e3 |
| 원격 CI | [Run 36679127805 PASS](https://github.com/Byeongwook-Heo/terraform-ai-mcp-demo/actions/runs/36679127805); 구현 게시 Commit 검증 |
| 후속 게시 방식 | 사용자가 main 직접 반영을 명시적으로 요청; 새 작업 Branch 없이 main 갱신 |
| 작업 경로 | `/workspace/terraform-ai-mcp-demo` |

기존 Phase 1 이력과 파일을 보존합니다. `codex/phase1-terraform-mcp`는 과거 검토 Branch이며 현재 준비물은 main에서 확인합니다. 과거 게시 API 오류와 Draft PR 생성 기록은 `github-publication.json`, `progress.md`의 초기 기록입니다. 현재 공개 범위·병합 상태와 혼동하지 않습니다.

휴대폰과 다음 Codex Cloud 작업에서 이 저장소의 **main**을 선택하고 `START_HERE.md`와 `cloud-completion.md`를 읽습니다. Cloud에서 가능한 준비 범위는 `../docs/09-cloud-preparation.md`에 있습니다.

main 게시 범위는 이 준비 저장소입니다. Module/Root/Policy의 다른 저장소, Registry version/Tag, HCP Workspace/Policy 또는 AWS 리소스 변경은 별도의 실제 대상과 입력·접근 조건을 확인해야 합니다. 자동 Apply/Destroy를 포함하지 않습니다.

연동 설치의 중지는 해제됐습니다. 일반 Git 전송은 401로 실패했지만 연결된 GitHub 앱의 Git Data API로 main 게시를 완료했습니다. force=false로 기존 이력을 보존하고 원격 파일 일치를 확인했습니다. 구현 게시 후 상태 보고서만 갱신하는 Commit이 이어질 수 있으며 최신 main의 게시·CI 상태는 `cloud-publication.json`을 확인합니다.
