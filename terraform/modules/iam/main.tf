locals {
  name = "${var.project_name}-${var.environment}"
}

# Service Account IAM Role for Pods
resource "aws_iam_role" "pod_s3_access" {
  name = "${local.name}-pod-s3-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRoleWithWebIdentity"
      Effect = "Allow"
      Principal = {
        Federated = var.eks_oidc_provider
      }
      Condition = {
        StringEquals = {
          "${replace(var.eks_oidc_provider, "/^(.*provider/)/", "")}:sub" = "system:serviceaccount:default:podtranslate-sa"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "pod_s3_access" {
  name = "s3-access"
  role = aws_iam_role.pod_s3_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ]
      Resource = [
        var.s3_bucket_arn,
        "${var.s3_bucket_arn}/*"
      ]
    }]
  })
}

# CloudWatch Logs IAM Policy
resource "aws_iam_role_policy" "cloudwatch_logs" {
  name = "cloudwatch-logs"
  role = aws_iam_role.pod_s3_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ]
      Resource = "arn:aws:logs:*:*:*"
    }]
  })
}
