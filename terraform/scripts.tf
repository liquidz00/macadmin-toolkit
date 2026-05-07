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

resource "jamfpro_script" "swift_dialog_notification_template" {
  name            = "Swift Dialog Notification Template"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.vendor_provided_dir}/swiftDialog-notification-template.sh")
  info            = "Template script for basic notification via swiftDialog.\nSee https://swiftdialog.app/examples/jamf-scripts/"
  parameter4      = "Title option (--title)"
  parameter5      = "Message option (--message)"
  parameter6      = "Icon option (--icon)"
  parameter7      = "Overlay option (--overlayicon)"
  parameter8      = "Button 1 option (--button1text)"
  parameter9      = "Button 2 option (--button2text)"
  parameter10     = "Info button option (--infobuttontext)"
  parameter11     = "Extra flag"
}

resource "jamfpro_script" "installomator" {
  name            = "Installomator"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.vendor_provided_dir}/Installomator.sh")
  info            = "See https://github.com/Installomator/Installomator"
}

resource "jamfpro_script" "clear_downloads" {
  name            = "Clear Downloads"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.py_dir}/clear_downloads.py")
  info            = "Removes all contents of the active console user's ~/Downloads directory. Designed for weekly weekend execution via recurring policy."
  parameter4      = "Dry-run (True/False)"
}

resource "jamfpro_script" "default_dock_dockutil" {
  name            = "Default Dock (dockutil)"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.py_dir}/default_dock.py")
  info            = "Configures the active console user's Dock with the org's standard apps via dockutil. Requires /usr/local/bin/dockutil."
  parameter4      = "Dry-run (True/False)"
  parameter5      = "Custom app path (optional)"
}

resource "jamfpro_script" "default_dock_docklib" {
  name            = "Default Dock (docklib)"
  category_id     = jamfpro_category.standard_issue.id
  priority        = "AFTER"
  script_contents = file("${local.py_dir}/default_dock_docklib.py")
  info            = "Configures the active console user's Dock with the org's standard apps via the docklib package shipped in macadmins managed_python3."
  parameter4      = "Dry-run (True/False)"
  parameter5      = "Custom app path (optional)"
}
