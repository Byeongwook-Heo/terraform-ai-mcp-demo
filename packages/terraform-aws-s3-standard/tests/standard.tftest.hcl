mock_provider "aws" {}
variables {
  bucket_name = "phase1-mock-bucket"
}
run "secure_defaults" {
  command = plan
  variables {
    tags = { Owner = "demo-team", ManagedBy = "untrusted-input" }
  }
  assert {
    condition     = aws_s3_bucket_public_access_block.this.block_public_acls && aws_s3_bucket_public_access_block.this.block_public_policy && aws_s3_bucket_public_access_block.this.ignore_public_acls && aws_s3_bucket_public_access_block.this.restrict_public_buckets
    error_message = "Public Access Block 네 설정이 모두 켜져야 합니다."
  }
  assert {
    condition     = aws_s3_bucket_versioning.this.versioning_configuration[0].status == "Enabled" && !aws_s3_bucket.this.force_destroy
    error_message = "Versioning을 켜고 강제 삭제를 금지해야 합니다."
  }
  assert {
    condition     = aws_s3_bucket.this.tags.ManagedBy == "Terraform" && aws_s3_bucket.this.tags.Owner == "demo-team"
    error_message = "ManagedBy는 고정하고 Owner 입력은 보존해야 합니다."
  }
}
run "owner_missing_is_not_module_validation" {
  command = plan
  assert {
    condition     = !contains(keys(aws_s3_bucket.this.tags), "Owner")
    error_message = "Owner를 자동으로 추가하면 Policy 실패 시연이 불가능합니다."
  }
}
run "empty_owner_is_not_module_validation" {
  command = plan
  variables {
    tags = { Owner = "" }
  }
}
