variable "project_name" {
  type    = string
  default = "iqda-portfolio"
}

variable "location" {
  type    = string
  default = "germanywestcentral"
}

variable "container_image" {
  type        = string
  description = "Fully-qualified ACR image reference."
}

variable "container_port" {
  type    = number
  default = 8000
}
