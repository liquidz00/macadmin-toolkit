# Categories — Jamf-internal groupings used to organize policies, packages,
# scripts, and config profiles. Each category carries a `priority` (1 = highest)
# that affects display order and policy execution sequencing.
#
# These are intentionally written as individual resources rather than rendered
# from a map. The original repo this pattern came from grew categories
# organically over years, each with its own creation context (and occasionally
# its own lifecycle quirks like the prevent_destroy on `restricted` below).
# Keeping them flat makes it easy to audit who-added-what via git blame and
# to attach per-category meta-arguments without contorting the map.

resource "jamfpro_category" "hero_apps" {
  name     = "Hero Apps"
  priority = 1
}

resource "jamfpro_category" "stark_tech" {
  name     = "Stark Tech"
  priority = 2
}

resource "jamfpro_category" "shield_comms" {
  name     = "S.H.I.E.L.D. Comms"
  priority = 3
}

resource "jamfpro_category" "wakandan_tech" {
  name     = "Wakandan Tech"
  priority = 4
}

resource "jamfpro_category" "mystic_arts" {
  name     = "Mystic Arts"
  priority = 5
}

resource "jamfpro_category" "mutant_affairs" {
  name     = "Mutant Affairs"
  priority = 6
}

resource "jamfpro_category" "standard_issue" {
  name     = "Standard Issue"
  priority = 9
}

# `restricted` carries `prevent_destroy` because policies and configuration
# profiles routinely get assigned to it. A `terraform destroy` that wiped this
# category would orphan every dependent resource — not a state we ever want to
# recover from in production. Lifting the lock requires explicit edit + apply.
resource "jamfpro_category" "restricted" {
  name     = "Restricted"
  priority = 10

  lifecycle {
    prevent_destroy = true
  }
}
