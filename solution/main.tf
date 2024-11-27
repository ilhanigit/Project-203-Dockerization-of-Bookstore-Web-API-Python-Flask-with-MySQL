terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    github = {
      source = "integrations/github"
      version = "6.2.3"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

provider "github" {
  # Configuration options
  # token = data.aws_ssm_parameter.token.value
  token = var.git-token
}

variable "git-token" {
  default = "xxxxxxxxxxxxxxxx"
}

variable "git-name" {
  default = "gitusername"
}

# data "aws_ssm_parameter" "gitname" {
#   name = "git-name"
# }

# data "aws_ssm_parameter" "token" {
#   name = "git-token"
# }

variable "key-name" {
  default = "instancekey"
}

resource "github_repository" "myrepo" {
  name = "bookstore-api-repo"
  visibility = "private"
  auto_init = true
}

resource "github_branch_default" "main" {
  branch = "main"
  repository = github_repository.myrepo.name
}

variable "files" {
  default = ["bookstore-api.py", "docker-compose.yml", "requirements.txt", "Dockerfile"]
}

resource "github_repository_file" "app-files" {
  for_each = toset(var.files)
  content = file(each.value)
  file = each.value
  repository = github_repository.myrepo.name
  branch = "main"
  commit_message = "managed by terraform"
  overwrite_on_create = true
}

resource "aws_security_group" "tf-docker-sec-gr" {
  name = "docker-sec-gr"
  tags = {
    Name = "docker-sec-group"
  }
  ingress {
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    protocol    = "tcp"
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    protocol    = -1
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "tf-docker-ec2" {
  ami = "ami-0b72821e2f351e396"
  instance_type = "t2.micro"
  key_name = var.key-name
  vpc_security_group_ids = [aws_security_group.tf-docker-sec-gr.id]
  tags = {
    Name = "Web Server of Bookstore"
  }
  user_data = templatefile("user-data.sh", { user-data-git-token = var.git-token, user-data-git-name = var.git-name })
  # user_data = templatefile("user-data.sh", { user-data-git-token = data.aws_ssm_parameter.token.value, user-data-git-name = data.aws_ssm_parameter.gitname.value })
  depends_on = [github_repository.myrepo, github_repository_file.app-files]
}


output "website" {
  value = "http://${aws_instance.tf-docker-ec2.public_dns}"
}



