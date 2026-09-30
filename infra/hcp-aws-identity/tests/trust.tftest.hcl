mock_provider "aws" {}
variables {
  aws_account_id             = "000000000000"
  hcp_organization           = "mock-org"
  hcp_project                = "mcp-demo"
  hcp_workspace              = "aws-ai-demo"
  bucket_name                = "phase1-mock-bucket"
  existing_oidc_provider_arn = "arn:aws:iam::000000000000:oidc-provider/app.terraform.io"
}
run "restricted_trust_and_permissions" {
  command = plan
  assert {
    condition     = jsondecode(aws_iam_role.run["plan"].assume_role_policy).Statement[0].Condition.StringEquals["app.terraform.io:sub"] == "organization:mock-org:project:mcp-demo:workspace:aws-ai-demo:run_phase:plan" && jsondecode(aws_iam_role.run["apply"].assume_role_policy).Statement[0].Condition.StringEquals["app.terraform.io:sub"] == "organization:mock-org:project:mcp-demo:workspace:aws-ai-demo:run_phase:apply"
    error_message = "Plan/Apply의 exact subject 조건이 분리되어야 합니다."
  }
  assert {
    condition     = jsondecode(aws_iam_role.run["plan"].assume_role_policy).Statement[0].Condition.StringEquals["app.terraform.io:aud"] == "aws.workload.identity" && length(aws_iam_openid_connect_provider.hcp) == 0
    error_message = "Audience를 제한하고 기존 Provider를 재사용해야 합니다."
  }
  assert {
    condition     = !contains(jsondecode(aws_iam_role_policy.s3["plan"].policy).Statement[0].Action, "s3:CreateBucket") && contains(jsondecode(aws_iam_role_policy.s3["apply"].policy).Statement[0].Action, "s3:CreateBucket") && jsondecode(aws_iam_role_policy.s3["apply"].policy).Statement[0].Resource == "arn:aws:s3:::phase1-mock-bucket"
    error_message = "Plan은 조회 전용, Apply는 정확한 Bucket에만 변경 권한이 있어야 합니다."
  }
}
run "reject_wildcard_subject" {
  command = plan
  variables {
    hcp_workspace = "*"
  }
  expect_failures = [var.hcp_workspace]
}
