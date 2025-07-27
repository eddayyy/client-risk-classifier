output "ecr_repo_url" {
  description = "ECR repository URI"
  value       = aws_ecr_repository.app.repository_url
}

output "eks_cluster_name" {
  description = "EKS Cluster name"
  value       = module.eks.cluster_id
}

output "codebuild_project_name" {
  description = "CodeBuild project"
  value       = aws_codebuild_project.build_and_deploy.name
}

output "codepipeline_name" {
  description = "CodePipeline"
  value       = aws_codepipeline.pipeline.name
}
