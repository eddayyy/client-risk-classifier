################################
# ECR Repository
################################
resource "aws_ecr_repository" "app" {
  name                 = "${var.project}-repo"
  image_scanning_configuration {
    scan_on_push = true
  }
}

################################
# EKS Cluster via Module
################################
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "18.29.0"

  cluster_name    = var.project
  cluster_version = "1.27"

  # VPC config: module will create a new VPC
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Nodegroup
  node_groups = {
    default = {
      desired_capacity = var.node_group_desired_capacity
      instance_types   = var.node_group_instance_types
    }
  }

  tags = {
    "Project" = var.project
  }
}

################################
# VPC (for EKS)
################################
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "4.0.2"

  name = "${var.project}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    "Project" = var.project
  }
}

data "aws_availability_zones" "available" {}

################################
# IAM Role for CodeBuild
################################
resource "aws_iam_role" "codebuild" {
  name = "${var.project}-codebuild-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codebuild.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "codebuild_ecr" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy_attachment" "codebuild_eks" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "codebuild_eks_worker" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "codebuild_logs" {
  role       = aws_iam_role.codebuild.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

################################
# CodeBuild Project
################################
resource "aws_codebuild_project" "build_and_deploy" {
  name          = "${var.project}-build"
  service_role  = aws_iam_role.codebuild.arn
  artifacts {
    type = "NO_ARTIFACTS"
  }
  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = true  # required for Docker
    environment_variable {
      name  = "ECR_REPO_URI"
      value = aws_ecr_repository.app.repository_url
    }
    environment_variable {
      name  = "CLUSTER_NAME"
      value = module.eks.cluster_id
    }
    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }
  }
  source {
    type            = "GITHUB"
    location        = "https://github.com/${var.github_owner}/${var.github_repo}.git"
    buildspec       = <<EOF
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.12
      docker: 20
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REPO_URI

  build:
    commands:
      - echo Build Docker image...
      - docker build -t $ECR_REPO_URI:latest .
      - docker push $ECR_REPO_URI:latest

  post_build:
    commands:
      - echo Updating Kubernetes deployment...
      - aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $CLUSTER_NAME
      - kubectl set image deployment/risk-classifier risk-classifier=$ECR_REPO_URI:latest --namespace default || kubectl create deployment risk-classifier --image=$ECR_REPO_URI:latest --namespace default
EOF
  }
}

################################
# S3 Bucket for CodePipeline Artifacts
################################
resource "aws_s3_bucket" "codepipeline" {
  bucket = "${var.project}-cp-artifacts-${random_id.suffix.hex}"
  acl    = "private"
  versioning {
    enabled = true
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

################################
# IAM Role for CodePipeline
################################
resource "aws_iam_role" "codepipeline" {
  name = "${var.project}-codepipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codepipeline.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cp_s3" {
  role       = aws_iam_role.codepipeline.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "cp_codebuild" {
  role       = aws_iam_role.codepipeline.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess"
}

resource "aws_iam_role_policy_attachment" "cp_ecr" {
  role       = aws_iam_role.codepipeline.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "cp_eks" {
  role       = aws_iam_role.codepipeline.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

################################
# CodePipeline
################################
resource "aws_codepipeline" "pipeline" {
  name     = "${var.project}-pipeline"
  role_arn = aws_iam_role.codepipeline.arn
  artifact_store {
    location = aws_s3_bucket.codepipeline.bucket
    type     = "S3"
  }
  stage {
    name = "Source"
    action {
      name             = "GitHub_Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        Owner      = var.github_owner
        Repo       = var.github_repo
        Branch     = "main"
        OAuthToken = var.github_oauth_token
      }
    }
  }
  stage {
    name = "Build"
    action {
      name             = "CodeBuild"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = []
      version          = "1"
      configuration = {
        ProjectName = aws_codebuild_project.build_and_deploy.name
      }
    }
  }
}
