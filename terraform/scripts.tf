# Jamf Pro script resources. Each resource pulls its body from the
# components/scripts/ tree via path locals. Two patterns appear here:
#
#   1. Plain `file()` — body is the script as written on disk.
#   2. `templatefile()` — body is rendered with values baked in at apply time
#      (typically base64-encoded content from components/configs/). When the
#      source content changes, terraform detects a script_contents diff and
#      re-deploys.

resource "jamfpro_script" "jamf_log_uploader" {
  name            = "Jamf Log Uploader"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.py_dir}/jamf_log_uploader.py")
  info            = "Collects Jamf, system, networking, and SSO logs and uploads to a webhook."
  parameter4      = "Webhook URL (optional)"
  parameter5      = "Dry-run (True/False)"
  parameter6      = "Custom subsystem (optional)"
  parameter7      = "Custom subsystem (optional)"
  parameter8      = "Custom subsystem (optional)"
}

resource "jamfpro_script" "claude_code_guidelines" {
  name        = "Deploy Claude Code Guidelines"
  category_id = jamfpro_category.standard_issue.id
  priority    = "AFTER"
  info        = "Renders the source-of-truth CLAUDE.md from VCS to /Library/Application Support/ClaudeCode/."
  script_contents = templatefile(
    "${local.py_dir}/claude_code_guidelines.py.tftpl",
    {
      claude_md_b64 = base64encode(
        file("${local.configs_dir}/claudecode/CLAUDE.md")
      )
    }
  )
}
