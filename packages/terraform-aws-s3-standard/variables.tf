variable "bucket_name" {
  description = "운영자가 확정한 전역 고유 S3 Bucket 이름"
  type        = string
  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63 && can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.bucket_name))
    error_message = "S3 이름 길이와 소문자 형식을 확인하세요. 최종 AWS 이름 제약은 운영자가 확인합니다."
  }
}
variable "tags" {
  description = "Owner는 Sentinel에서 검사하며 Module은 누락을 허용합니다."
  type        = map(string)
  default     = {}
}
