provider "aws" {
  region = "ap-northeast-2"
}
variable "bucket_name" {
  type    = string
  default = "phase1-mock-bucket"
}
variable "tags" {
  type    = map(string)
  default = {}
}
module "s3_standard" {
  source      = "../../packages/terraform-aws-s3-standard"
  bucket_name = var.bucket_name
  tags        = var.tags
}
output "bucket_id" {
  value = module.s3_standard.bucket_id
}
