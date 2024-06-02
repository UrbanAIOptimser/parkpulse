variable "project_name" {
  default = "parkpulse-airflow"
}

variable "stage" {
  default = "dev"
}

variable "profile" {
  default = "park_pulse"
}

variable "metadata_db_instance_type" {
   default = "db.t3.micro"
}

variable "celery_backend_instance_type" {
  default = "cache.t2.micro"
}

variable   "log_group_name" {
    default = "ecs/parkpulse-airflow"
}

variable "s3_bucket" {
  default = "parkpulse-airflow"
}

variable "base_cidr_block" {
   default = "10.0.0.0"
}

variable "image_version" {
  default = "latest"
}

variable "fernet_key" {
  default = ""
}

variable "aws_region" {
  default = "us-east-1"
}

variable "availability_zones" {
   type    = list(string)
   default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}