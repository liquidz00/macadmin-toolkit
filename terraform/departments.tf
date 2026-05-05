# Departments — organizational divisions, used as scope criteria for policies,
# config profiles, and smart groups. Departments only have a name field, so
# the simpler for_each-over-set form fits cleanly.

locals {
  departments = toset([
    "Avengers",
    "X-Men",
    "Fantastic Four",
    "Defenders",
    "Guardians of the Galaxy",
    "S.H.I.E.L.D.",
    "Stark Industries R&D",
    "Wakandan Design Group",
    "Howling Commandos",
  ])
}

resource "jamfpro_department" "this" {
  for_each = local.departments

  name = each.value
}
