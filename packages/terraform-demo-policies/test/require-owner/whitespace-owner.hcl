mock "tfplan/v2" {
  module { source = "../../mocks/whitespace-owner.sentinel" }
}
test { rules = { main = false } }
