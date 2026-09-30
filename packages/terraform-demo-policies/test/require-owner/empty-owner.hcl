mock "tfplan/v2" {
  module { source = "../../mocks/empty-owner.sentinel" }
}
test { rules = { main = false } }
