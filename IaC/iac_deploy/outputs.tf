output "instance_public_dns" {
  description = "Endereço DNS público da EC2, use http://<dns>:8501 para Streamlit"
  value       = aws_instance.ec2_fraudes.public_dns
}
