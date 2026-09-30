mock "tfplan/v2" {
  module { source = "../../mocks/replacement.sentinel" }
}
test { rules = { main = false } }
