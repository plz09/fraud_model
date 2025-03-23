################################
# PROVEDOR AWS E REGIÃO
################################
provider "aws" {
  region = "us-east-2"
}

################################
# BUCKET S3 PARA CÓDIGO
################################
resource "aws_s3_bucket" "fraudes_bucket" {
  bucket = "pellizzi-914156456046-bucket"

  tags = {
    Projeto     = "Deteccao Fraudes"
    Environment = "Academico"
  }

  # Opcional: enviar algo inicial p/ S3
  provisioner "local-exec" {
    command = "${path.module}/upload_to_s3.sh"
  }

  # Remove arquivos do Bucket no destroy
  provisioner "local-exec" {
    when    = destroy
    command = "aws s3 rm s3://pellizzi-914156456046-bucket --recursive"
  }
}

################################
# RDS PostgreSQL (FREE TIER)
################################
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

################################
# SECURITY GROUP DO RDS
################################
resource "aws_security_group" "db_sg" {
  name        = "db-fraudes-sg"
  description = "Permitir acesso PostgreSQL (Porta 5432)"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Ajuste futuramente
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

################################
# SECURITY GROUP DA EC2
################################
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-fraudes-sg"
  description = "Permitir SSH, HTTP e Streamlit"

  # SSH
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP (porta 80) para FastAPI
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Streamlit (porta 8501)
  ingress {
    description = "Streamlit"
    from_port   = 8501
    to_port     = 8501
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

################################
# ROLE + INSTANCE PROFILE P/ EC2 S3
################################
resource "aws_iam_role" "ec2_s3_access_role" {
  name = "ec2_s3_fraudes_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" },
      Action    = "sts:AssumeRole"
    }]
  })
}

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

resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ec2_fraudes_profile"
  role = aws_iam_role.ec2_s3_access_role.name
}

################################
# EC2 PARA FASTAPI + STREAMLIT
################################
resource "aws_instance" "ec2_fraudes" {
  ami                         = "ami-0a0d9cf81c479446a" # Amazon Linux 2
  instance_type               = "t2.micro"
  iam_instance_profile        = aws_iam_instance_profile.ec2_s3_profile.name
  vpc_security_group_ids      = [aws_security_group.ec2_sg.id]
  associate_public_ip_address = true

  # Interpolar endpoint do RDS
  user_data = <<-EOF
  #!/bin/bash
  sudo yum update -y
  sudo yum install -y python3 python3-pip awscli

  # Variáveis do RDS
  DB_ENDPOINT="${aws_db_instance.db_fraudes.endpoint}"
  DB_NAME="db_fraudes"
  DB_USER="pellizzi"
  DB_PASS="Pellizzi123!"

  # Sincroniza o código do S3
  mkdir -p /model_app
  aws s3 sync s3://pellizzi-914156456046-bucket/model_app /model_app

  # Exporta /model_app para PYTHONPATH para que os módulos sejam encontrados
  echo "export PYTHONPATH=/model_app" | sudo tee -a /etc/profile
  export PYTHONPATH=/model_app

  # Instala dependências principais fixando versões para evitar erro de OpenSSL
  # (Forçamos urllib3==1.26.16 e requests==2.28.2, que funcionam com OpenSSL 1.0.2)
  pip3 install fastapi uvicorn[standard] streamlit pandas numpy scikit-learn psycopg2-binary \
               "urllib3==1.26.16" "requests==2.28.2"

  # Exporta variáveis de ambiente para a aplicação
  echo "export DB_ENDPOINT=$DB_ENDPOINT" | sudo tee -a /etc/profile
  echo "export DB_NAME=$DB_NAME"         | sudo tee -a /etc/profile
  echo "export DB_USER=$DB_USER"         | sudo tee -a /etc/profile
  echo "export DB_PASS=$DB_PASS"         | sudo tee -a /etc/profile

  # Inicia a API FastAPI
  cd /model_app/fastapi_api
  nohup uvicorn main:app --host 0.0.0.0 --port 80 &

  # Inicia o Streamlit na porta 8501
  nohup streamlit run /model_app/frontend_streamlit/app.py --server.port=8501 --server.address=0.0.0.0 &
EOF

  tags = {
    Name        = "EC2-Fraudes-ML"
    Projeto     = "Deteccao Fraudes"
    Environment = "Academico"
  }
}


