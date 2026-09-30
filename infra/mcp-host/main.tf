provider "aws" {
  region = var.aws_region
}
data "aws_ami" "approved" {
  # 운영자가 승인한 단일 ID를 조회합니다. latest 자동 선택은 하지 않습니다.
  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
  filter {
    name   = "name"
    values = ["hc-base-*", "hc-security-base-*"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "state"
    values = ["available"]
  }
}
resource "aws_security_group" "mcp" {
  name_prefix = "${var.name}-"
  description = "SSM management; no ingress by default"
  vpc_id      = var.vpc_id
  tags        = merge(var.tags, { Name = var.name, ManagedBy = "Terraform" })
}
resource "aws_vpc_security_group_egress_rule" "https" {
  for_each          = var.egress_https_cidrs
  security_group_id = aws_security_group.mcp.id
  cidr_ipv4         = each.value
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}
resource "aws_vpc_security_group_ingress_rule" "approved_ssh" {
  for_each          = var.ssh_ingress_cidrs
  security_group_id = aws_security_group.mcp.id
  cidr_ipv4         = each.value
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
}
resource "aws_iam_role" "ssm" {
  name = "${var.name}-ssm"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "sts:AssumeRole", Principal = { Service = "ec2.amazonaws.com" } }]
  })
  tags = var.tags
}
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_instance_profile" "ssm" {
  name = "${var.name}-ssm"
  role = aws_iam_role.ssm.name
}
resource "aws_instance" "mcp" {
  ami                         = data.aws_ami.approved.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.mcp.id]
  associate_public_ip_address = var.associate_public_ip_address
  key_name                    = var.key_name
  iam_instance_profile        = aws_iam_instance_profile.ssm.name
  user_data                   = file("${path.module}/bootstrap.sh")
  user_data_replace_on_change = true
  dynamic "credit_specification" {
    # 짧은 데모의 기본 비용을 예측할 수 있도록 T3 surplus credit 과금을 방지합니다.
    for_each = startswith(var.instance_type, "t3.") || startswith(var.instance_type, "t3a.") || startswith(var.instance_type, "t2.") ? [1] : []
    content {
      cpu_credits = "standard"
    }
  }
  lifecycle {
    precondition {
      condition = (
        data.aws_ami.approved.id == var.ami_id &&
        data.aws_ami.approved.architecture == "x86_64" &&
        (startswith(data.aws_ami.approved.name, "hc-base-") || startswith(data.aws_ami.approved.name, "hc-security-base-"))
      )
      error_message = "선택한 ID의 x86_64 AMI는 hc-base-* 또는 hc-security-base-* 이름이어야 합니다."
    }
  }
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }
  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
  }
  tags = merge(var.tags, { Name = var.name, ManagedBy = "Terraform" })
}
