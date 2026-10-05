variable "bucket_name" {
  description = "Existing demo S3 Bucket name"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-northeast-2"
}

variable "owner" {
  description = "Owner required by the Sentinel policy"
  type        = string
}
