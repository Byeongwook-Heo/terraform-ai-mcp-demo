output "instance_id" {
  value = aws_instance.mcp.id
}
output "security_group_id" {
  value = aws_security_group.mcp.id
}
output "ssm_role_arn" {
  value = aws_iam_role.ssm.arn
}
