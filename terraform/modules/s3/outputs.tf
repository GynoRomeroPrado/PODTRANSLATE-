output "audio_bucket_name" {
  description = "Audio bucket name"
  value       = aws_s3_bucket.audio.id
}

output "audio_bucket_arn" {
  description = "Audio bucket ARN"
  value       = aws_s3_bucket.audio.arn
}

output "transcripts_bucket_name" {
  description = "Transcripts bucket name"
  value       = aws_s3_bucket.transcripts.id
}

output "transcripts_bucket_arn" {
  description = "Transcripts bucket ARN"
  value       = aws_s3_bucket.transcripts.arn
}
