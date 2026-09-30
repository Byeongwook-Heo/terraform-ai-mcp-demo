output "plan_role_arn" {
  value = aws_iam_role.run["plan"].arn
}
output "apply_role_arn" {
  value = aws_iam_role.run["apply"].arn
}
output "oidc_provider_arn" {
  value = local.oidc_provider_arn
}
