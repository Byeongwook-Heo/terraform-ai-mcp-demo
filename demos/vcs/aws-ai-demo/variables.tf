variable "bucket_name" {
  description = "Existing demo S3 Bucket name"
  type        = string
  default     = "bw-terraform-ai-demo-20260930-17e980ef"
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-northeast-2"
}

variable "owner" {
  description = "Owner required by the Sentinel policy"
  type        = string
  default     = "bw-heo"
}
