mock "tfplan/v2" {
  module { source = "../../mocks/missing-owner.sentinel" }
}
test { rules = { main = false } }
