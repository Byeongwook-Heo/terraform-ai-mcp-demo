mock_provider "aws" {}
override_data {
  target = data.aws_ami.approved
  values = {
    id           = "ami-mock"
    name         = "hc-base-unit-fixture"
    architecture = "x86_64"
  }
}
variables {
  vpc_id    = "vpc-mock"
  subnet_id = "subnet-mock"
  ami_id    = "ami-mock"
}
run "management_isolated" {
  command = plan
  assert {
    condition     = length(aws_vpc_security_group_ingress_rule.approved_ssh) == 0 && !aws_instance.mcp.associate_public_ip_address
    error_message = "기본 Inbound와 Public IP가 없어야 합니다."
  }
  assert {
    condition     = aws_instance.mcp.metadata_options[0].http_tokens == "required" && aws_instance.mcp.metadata_options[0].http_put_response_hop_limit == 1 && aws_instance.mcp.root_block_device[0].encrypted
    error_message = "IMDSv2, hop limit 1, EBS 암호화가 필요합니다."
  }
  assert {
    condition     = aws_iam_role_policy_attachment.ssm.policy_arn == "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    error_message = "EC2 Profile은 SSM 관리 전용이어야 합니다."
  }
}
run "reject_world_ssh" {
  command = plan
  variables {
    ssh_ingress_cidrs = ["0.0.0.0/0"]
  }
  expect_failures = [var.ssh_ingress_cidrs]
}

run "security_base_is_allowed" {
  command = plan
  override_data {
    target = data.aws_ami.approved
    values = {
      id           = "ami-mock"
      name         = "hc-security-base-unit-fixture"
      architecture = "x86_64"
    }
  }
  assert {
    condition     = aws_instance.mcp.ami == "ami-mock"
    error_message = "검증한 단일 AMI ID를 사용해야 합니다."
  }
}
run "reject_unapproved_ami_name" {
  command = plan
  override_data {
    target = data.aws_ami.approved
    values = {
      id           = "ami-mock"
      name         = "unapproved-unit-fixture"
      architecture = "x86_64"
    }
  }
  expect_failures = [aws_instance.mcp]
}
run "reject_arm_ami" {
  command = plan
  override_data {
    target = data.aws_ami.approved
    values = {
      id           = "ami-mock"
      name         = "hc-base-unit-fixture"
      architecture = "arm64"
    }
  }
  expect_failures = [aws_instance.mcp]
}
run "reject_different_ami_id" {
  command = plan
  override_data {
    target = data.aws_ami.approved
    values = {
      id           = "ami-other"
      name         = "hc-base-unit-fixture"
      architecture = "x86_64"
    }
  }
  expect_failures = [aws_instance.mcp]
}
