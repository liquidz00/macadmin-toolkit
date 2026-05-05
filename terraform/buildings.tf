# Buildings — physical office locations referenced by computer records.
# Driven by a local map and rendered with for_each so a new location is one
# entry away rather than a copy-pasted resource block.

locals {
  buildings = {
    avengers_tower = {
      name            = "Avengers Tower"
      street_address1 = "200 Park Avenue"
      street_address2 = ""
      city            = "New York"
      state_province  = "NY"
      zip_postal_code = "10166"
      country         = "United States"
    }
    avengers_compound = {
      name            = "Avengers Compound"
      street_address1 = "1407 Graymalkin Lane"
      street_address2 = ""
      city            = "North Salem"
      state_province  = "NY"
      zip_postal_code = "10560"
      country         = "United States"
    }
    stark_industries_hq = {
      name            = "Stark Industries HQ"
      street_address1 = "10880 Malibu Point"
      street_address2 = ""
      city            = "Malibu"
      state_province  = "CA"
      zip_postal_code = "90265"
      country         = "United States"
    }
    sanctum_sanctorum = {
      name            = "Sanctum Sanctorum"
      street_address1 = "177A Bleecker Street"
      street_address2 = ""
      city            = "New York"
      state_province  = "NY"
      zip_postal_code = "10012"
      country         = "United States"
    }
    xaviers_school = {
      name            = "Xavier's School for Gifted Youngsters"
      street_address1 = "1407 Graymalkin Lane"
      street_address2 = ""
      city            = "Salem Center"
      state_province  = "NY"
      zip_postal_code = "10560"
      country         = "United States"
    }
    wakanda_embassy = {
      name            = "Wakanda Embassy"
      street_address1 = "2530 Massachusetts Avenue NW"
      street_address2 = ""
      city            = "Washington"
      state_province  = "DC"
      zip_postal_code = "20008"
      country         = "United States"
    }
    triskelion = {
      name            = "The Triskelion"
      street_address1 = "1101 Wilson Boulevard"
      street_address2 = ""
      city            = "Arlington"
      state_province  = "VA"
      zip_postal_code = "22209"
      country         = "United States"
    }
  }
}

resource "jamfpro_building" "this" {
  for_each = local.buildings

  name            = each.value.name
  street_address1 = each.value.street_address1
  street_address2 = each.value.street_address2
  city            = each.value.city
  state_province  = each.value.state_province
  zip_postal_code = each.value.zip_postal_code
  country         = each.value.country
}
