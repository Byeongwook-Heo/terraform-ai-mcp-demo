provider "aws" {
  region = var.aws_region
}
resource "aws_iam_openid_connect_provider" "hcp" {
  count          = var.create_oidc_provider ? 1 : 0
  url            = "https://app.terraform.io"
  client_id_list = [var.audience]
  # AWS Provider 6.14.1에서 thumbprint_list는 선택 사항입니다.
}
locals {
  oidc_provider_arn = var.create_oidc_provider ? aws_iam_openid_connect_provider.hcp[0].arn : var.existing_oidc_provider_arn
  subject_prefix    = "organization:${var.hcp_organization}:project:${var.hcp_project}:workspace:${var.hcp_workspace}:run_phase"
  bucket_arn        = "arn:aws:s3:::${var.bucket_name}"
  read_actions = [
    "s3:ListBucket", "s3:GetBucketLocation", "s3:GetBucketTagging",
    "s3:GetBucketPolicy", "s3:GetBucketAcl", "s3:GetBucketCors", "s3:GetBucketWebsite",
    "s3:GetBucketVersioning", "s3:GetBucketLogging", "s3:GetLifecycleConfiguration",
    "s3:GetAccelerateConfiguration", "s3:GetBucketRequestPayment",
    "s3:GetReplicationConfiguration", "s3:GetEncryptionConfiguration",
    "s3:GetBucketObjectLockConfiguration", "s3:GetBucketPublicAccessBlock"
  ]
  write_actions = [
    "s3:CreateBucket", "s3:DeleteBucket", "s3:PutBucketTagging",
    "s3:PutBucketVersioning", "s3:PutBucketPublicAccessBlock"
  ]
}
resource "aws_iam_role" "run" {
  for_each = toset(["plan", "apply"])
  name     = "${var.role_name_prefix}-${each.key}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = local.oidc_provider_arn }
      Condition = {
        StringEquals = {
          "app.terraform.io:aud" = var.audience
          "app.terraform.io:sub" = "${local.subject_prefix}:${each.key}"
        }
      }
    }]
  })
  lifecycle {
    precondition {
      condition     = var.create_oidc_provider != (var.existing_oidc_provider_arn != null)
      error_message = "기존 OIDC 재사용과 새 생성 중 정확히 하나를 선택하세요."
    }
  }
}
resource "aws_iam_role_policy" "s3" {
  for_each = aws_iam_role.run
  name     = "demo-bucket-only"
  role     = each.value.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = each.key == "plan" ? local.read_actions : concat(local.read_actions, local.write_actions)
      Resource = local.bucket_arn
    }]
  })
}
