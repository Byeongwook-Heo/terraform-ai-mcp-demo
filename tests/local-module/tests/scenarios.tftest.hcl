mock_provider "aws" {}
run "normal" {
  command = plan
  variables {
    tags = { Owner = "demo-team", Environment = "demo" }
  }
  assert {
    condition     = var.tags.Owner == "demo-team"
    error_message = "정상 Root fixture 입력이 유지되어야 합니다."
  }
}
run "missing_owner_plan_allowed" {
  command = plan
  variables {
    tags = { Environment = "demo" }
  }
  assert {
    condition     = !contains(keys(var.tags), "Owner")
    error_message = "Owner 누락을 Module validation으로 차단하면 안 됩니다."
  }
}
run "fixed_owner_plan_allowed" {
  command = plan
  variables {
    tags = { Owner = "demo-team", Environment = "demo" }
  }
}
