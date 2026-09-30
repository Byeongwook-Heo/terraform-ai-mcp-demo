variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}
variable "aws_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "AWS account ID는 12자리여야 합니다."
  }
}
variable "hcp_organization" {
  type = string
  validation {
    condition     = can(regex("^[A-Za-z0-9_-]+$", var.hcp_organization))
    error_message = "Organization 값에 wildcard나 subject 구분자를 사용하지 마세요."
  }
}
variable "hcp_project" {
  type = string
  validation {
    condition     = length(trimspace(var.hcp_project)) > 0 && !can(regex("[:*?]", var.hcp_project))
    error_message = "Project는 정확한 이름이어야 합니다."
  }
}
variable "hcp_workspace" {
  type = string
  validation {
    condition     = can(regex("^[A-Za-z0-9_-]+$", var.hcp_workspace))
    error_message = "Workspace 값에 wildcard나 subject 구분자를 사용하지 마세요."
  }
}
variable "audience" {
  type    = string
  default = "aws.workload.identity"
  validation {
    condition     = length(trimspace(var.audience)) > 0 && !can(regex("[*?]", var.audience))
    error_message = "Audience는 정확한 값이어야 합니다."
  }
}
variable "role_name_prefix" {
  type    = string
  default = "hcp-s3-demo"
}
variable "create_oidc_provider" {
  description = "기존 Provider가 없음을 Phase 2에서 확인한 경우에만 true입니다."
  type        = bool
  default     = false
}
variable "existing_oidc_provider_arn" {
  type    = string
  default = null
  validation {
    condition     = var.existing_oidc_provider_arn == null ? true : var.existing_oidc_provider_arn == "arn:aws:iam::${var.aws_account_id}:oidc-provider/app.terraform.io"
    error_message = "동일 계정의 app.terraform.io OIDC Provider ARN이어야 합니다."
  }
}
variable "bucket_name" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "정확한 Bucket 이름이 필요합니다. wildcard는 허용하지 않습니다."
  }
}
