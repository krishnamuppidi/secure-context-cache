resource "aws_iam_role" "payment_lambda_role" {
  name = "prod-payment-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "payment_lambda_policy" {
  name = "prod-payment-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "kms:Decrypt"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_lambda_function" "payment_api" {
  function_name = "prod-payment-api"
  role          = aws_iam_role.payment_lambda_role.arn
  handler       = "app.handler"
  runtime       = "python3.11"
}

