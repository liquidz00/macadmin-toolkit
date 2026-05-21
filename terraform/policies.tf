# Jamf Pro policy resources
# https://registry.terraform.io/providers/deploymenttheory/jamfpro/latest/docs/resources/policy

resource "jamfpro_policy" "chatgpt_atlas_install" {
  name          = "Install ChatGPT Atlas"
  enabled       = true
  trigger_other = "USER_INITIATED"
  frequency     = "Ongoing"
  target_drive  = "/"
  category_id   = jamfpro_category.standard_issue.id
  site_id       = -1

  scope {
    all_computers = true
  }

  self_service {
    use_for_self_service      = true
    self_service_display_name = "ChatGPT Atlas"
    install_button_text       = "Install"
    reinstall_button_text     = "Reinstall"
    self_service_description  = "Install or update OpenAI's ChatGPT Atlas browser."

    self_service_category {
      id         = jamfpro_category.standard_issue.id
      display_in = true
      feature_in = false
    }
  }

  payloads {
    scripts {
      id         = jamfpro_script.installomator.id
      priority   = "After"
      parameter4 = "valuesfromarguments"
      parameter5 = "name=ChatGPT Atlas"
      parameter6 = "type=dmg"
      parameter7 = "downloadURL=https://persistent.oaistatic.com/atlas/public/ChatGPT_Atlas_Desktop_public_1.2026.119.1_20260504231115000.dmg"
      parameter8 = "expectedTeamID=4P9YKVZSXJ"
    }
  }
}
