resource "jamfpro_computer_extension_attribute" "claude_code_guidelines" {
  name                   = "Claude Code Guidelines Status"
  enabled                = true
  description            = "Validates CLAUDE.md against the deployed source-of-truth hash."
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"

  script_contents = templatefile(
    "${local.xattrs_dir}/claude_code_guidelines.py.tftpl",
    {
      expected_sha256 = sha256(
        file("${local.configs_dir}/claudecode/CLAUDE.md")
      )
    }
  )
}

resource "jamfpro_computer_extension_attribute" "claude_code_model" {
  name                   = "Claude Code Model"
  enabled                = true
  description            = "AI model set for claude code usage"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/claude_code_model.py")
}

resource "jamfpro_computer_extension_attribute" "managed_python_present" {
  name                   = "Managed Python Present"
  enabled                = true
  description            = "Checks installation status of managed python interpreter"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/managed-python-present.sh")
}

resource "jamfpro_computer_extension_attribute" "falcon_agent_id" {
  name                   = "Falcon Sensor Agent ID"
  enabled                = true
  description            = "Returns agent ID of installed Falcon sensor"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/falcon_agent_id.py")
}

resource "jamfpro_computer_extension_attribute" "falcon_sensor_status" {
  name                   = "Falcon Sensor Status"
  enabled                = true
  description            = "Returns sensor status of installed Falcon sensor"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/falcon_sensor_status.py")
}

resource "jamfpro_computer_extension_attribute" "uptime" {
  name                   = "Uptime"
  enabled                = true
  description            = "Returns amount of days since machine last rebooted"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/uptime.py")
}

resource "jamfpro_computer_extension_attribute" "zoom_camera_allowed" {
  name                   = "Zoom Camera Allowed"
  enabled                = true
  description            = "Determines camera TCC permissions set for Zoom"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/zoom_camera_allowed.py")
}
