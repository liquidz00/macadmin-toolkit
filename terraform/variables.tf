locals {
  repo_root      = "${path.module}/.."
  components_dir = "${local.repo_root}/components"

  scripts_dir         = "${local.components_dir}/scripts/"
  py_dir              = "${local.scripts_dir}/python"
  shell_dir           = "${local.scripts_dir}/shell"
  powershell_dir      = "${local.scripts_dir}/powershell"
  xattrs_dir          = "${local.components_dir}/xattrs"
  vendor_provided_dir = "${local.components_dir}/vendor-provided"
  configs_dir         = "${local.components_dir}/configs"
}


variable "jamfpro_instance_fqdn" {
  description = "The Jamf Pro FQDN (fully qualified domain name). Example: https://mycompany.jamfcloud.com"
  sensitive   = true
}

variable "jamfpro_auth_method" {
  description = "Auth method chosen for Jamf. Options are 'basic' or 'oauth2'."
  sensitive   = true
  type        = string
}

variable "jamfpro_client_id" {
  description = "The Jamf Pro Client ID for authentication."
  sensitive   = true
  type        = string
}

variable "jamfpro_client_secret" {
  description = "The Jamf Pro Client Secret for authentication."
  sensitive   = true
  type        = string
}

variable "enable_client_sdk_logs" {
  description = "Enable client SDK logs."
  type        = bool
  default     = false
}

variable "client_sdk_log_export_path" {
  description = "Specify the path to export http client logs to."
  type        = string
  default     = ""
}

variable "jamfpro_hide_sensitive_data" {
  description = "Define whether sensitive fields should be hidden in logs."
  type        = bool
  default     = true
}

variable "jamfpro_custom_cookies" {
  description = "Custom cookies for the HTTP client."
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "jamfpro_load_balancer_lock" {
  description = "Programmatically determines all available web app members in the load balancer and locks all instances of httpclient to the app for faster executions."
  type        = bool
  default     = true
}

variable "jamfpro_token_refresh_buffer_period_seconds" {
  description = "The buffer period in seconds for token refresh."
  type        = number
  default     = 300
}

variable "jamfpro_mandatory_request_delay_milliseconds" {
  description = "A mandatory delay after each request before returning to reduce high volume of requests in a short time."
  type        = number
  default     = 100
}
