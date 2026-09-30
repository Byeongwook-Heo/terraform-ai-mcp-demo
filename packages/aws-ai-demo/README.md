# Private Registry Root 원본

`templates/*.tf.tmpl`은 실제 Organization이 없는 상태의 Registry 전용 템플릿입니다. 활성 Terraform Root와 혼합하지 않았습니다. `scripts/render-registry-root.py`로 새 로컬 디렉터리에 렌더링한 뒤 실제 Registry 응답과 Source/Version을 대조합니다.

정상 템플릿에는 Owner=demo-team이 있습니다. `fixtures/missing-owner.patch`로 Root main.tf의 Owner만 제거하고 `fix-owner.patch`로 복구합니다. Region과 bucket_name은 Root 변수이며 AWS Key나 provider Owner default_tags가 없습니다.

계정 없는 검증 Root는 별도 `tests/local-module`에 있으며 이를 Private Registry 성공으로 소개하지 않습니다. 게시/Workspace 설정은 docs/03-registry-and-workspace.md를 따릅니다.
