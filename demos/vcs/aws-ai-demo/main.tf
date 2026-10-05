provider "aws" {
  region = var.aws_region
}

module "s3_standard" {
  source  = "ip-10-40-10-211.ap-northeast-2.compute.internal/hashicorp_lab/s3-standard/aws"
  version = "1.0.0"

  bucket_name = var.bucket_name
  tags = {
    Owner       = var.owner
    Environment = "production"
  }
}

output "bucket_id" {
  description = "S3 Bucket ID"
  value       = module.s3_standard.bucket_id
}

output "bucket_arn" {
  description = "S3 Bucket ARN"
  value       = module.s3_standard.bucket_arn
}
