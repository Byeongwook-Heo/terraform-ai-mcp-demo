mock "tfplan/v2" {
  module { source = "../../mocks/null-owner.sentinel" }
}
test { rules = { main = false } }
