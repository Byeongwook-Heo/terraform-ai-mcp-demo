mock "tfplan/v2" {
  module { source = "../../mocks/unknown-owner.sentinel" }
}
test { rules = { main = false } }
