variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}
variable "name" {
  type    = string
  default = "terraform-mcp-demo"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.name))
    error_message = "name은 소문자와 숫자, 하이픈을 사용하는 3~31자여야 합니다."
  }
}
variable "vpc_id" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "ami_id" {
  description = "승인된 Region의 hc-base-* 또는 hc-security-base-* x86_64 AMI ID. AL2023/SSM 호환성은 별도 확인."
  type        = string
}
variable "instance_type" {
  type    = string
  default = "t3.small"
}
variable "associate_public_ip_address" {
  description = "기존 Subnet의 승인된 egress 경로를 사용합니다."
  type        = bool
  default     = false
}
variable "egress_https_cidrs" {
  type    = set(string)
  default = ["0.0.0.0/0"]
}
variable "ssh_ingress_cidrs" {
  description = "직접 SSH를 따로 승인한 경우에만 고정 IPv4 /32를 입력합니다."
  type        = set(string)
  default     = []
  validation {
    condition     = alltrue([for cidr in var.ssh_ingress_cidrs : can(cidrnetmask(cidr)) && can(regex("/32$", cidr))])
    error_message = "SSH 원본은 승인된 IPv4 /32만 허용합니다."
  }
}
variable "key_name" {
  description = "기존 EC2 Key Pair 이름. SSM 기반 기본 구성에서는 null입니다."
  type        = string
  default     = null
}
variable "tags" {
  type    = map(string)
  default = {}
}
