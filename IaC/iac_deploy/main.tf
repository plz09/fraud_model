provider "aws" {
  region = "us-east-2"
}

#--- Bucket S3 para datasets e modelo ML
resource "aws_s3_bucket" "fraudes_bucket" {
  bucket = "pellizzi-914156456046-bucket"
  
  tags = {
    Projeto     = "Deteccao Fraudes"
    Environment = "Academico"
  }
  
  # Opcional: provisioner para fazer upload inicial (se precisar futuramente)
  provisioner "local-exec" {
  command = "${path.module}/upload_to_s3.sh"
  }
  
  # Remove objetos antes de destruir o bucket (útil!)
  provisioner "local-exec" {
    when    = destroy
    command = "aws s3 rm s3://pellizzi-914156456046-bucket --recursive"
  }
}

#--- RDS PostgreSQL (free-tier)
resource "aws_db_instance" "db_fraudes" {
  identifier             = "db-fraudes"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  username               = "pellizzi"
  password               = "Pellizzi123!"
  publicly_accessible    = true
  skip_final_snapshot    = true

  vpc_security_group_ids = [aws_security_group.db_sg.id]

  tags = {
    Projeto     = "Deteccao Fraudes"
    Environment = "Academico"
  }
}

#--- Grupo de segurança para o Banco de Dados RDS
resource "aws_security_group" "db_sg" {
  name        = "db-fraudes-sg"
  description = "Permitir acesso PostgreSQL (Porta 5432)"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Ajuste futuramente para mais segurança
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Projeto = "Deteccao Fraudes"
  }
}

#--- Instância EC2 para execução do treinamento e interação com S3 e RDS 
resource "aws_instance" "ec2_fraudes" {
  ami                    = "ami-0a0d9cf81c479446a"  # Ubuntu Server 22.04 LTS (us-east-2)
  instance_type          = "t2.micro"
  iam_instance_profile   = aws_iam_instance_profile.ec2_s3_profile.name
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update -y
    sudo apt install -y python3-pip awscli
    sudo pip3 install pandas numpy scikit-learn boto3 psycopg2-binary
    sudo mkdir /pellizzi_fraud_app
    aws s3 sync s3://pellizzi-914156456046-bucket /pellizzi_fraud_app
  EOF

  tags = {
    Name        = "EC2-Fraudes-ML"
    Projeto     = "Deteccao Fraudes"
    Environment = "Academico"
  }
}

#--- Security Group EC2 (SSH + HTTP)
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-fraudes-sg"
  description = "Permitir SSH e HTTP para EC2"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Projeto = "Deteccao Fraudes"
  }
}

#--- Role IAM para acesso da EC2 ao Bucket S3
resource "aws_iam_role" "ec2_s3_access_role" {
  name = "ec2_s3_fraudes_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

#--- IAM Policy para permitir acesso ao Bucket S3 pela EC2
resource "aws_iam_role_policy" "ec2_s3_access_policy" {
  name = "ec2_s3_fraudes_policy"
  role = aws_iam_role.ec2_s3_access_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      Resource = [
        "${aws_s3_bucket.fraudes_bucket.arn}",
        "${aws_s3_bucket.fraudes_bucket.arn}/*"
      ]
    }]
  })
}

#--- IAM Instance Profile para associar role IAM com EC2
resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ec2_fraudes_profile"
  role = aws_iam_role.ec2_s3_access_role.name
}
