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

resource "jamfpro_computer_extension_attribute" "managed_python_present" {
  name                   = "Managed Python Present"
  enabled                = true
  description            = "Checks installation status of managed python interpreter"
  data_type              = "STRING"
  input_type             = "SCRIPT"
  inventory_display_type = "EXTENSION_ATTRIBUTES"
  script_contents        = file("${local.xattrs_dir}/managed-python-present.sh")
}
