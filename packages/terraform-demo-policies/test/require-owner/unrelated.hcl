mock "tfplan/v2" {
  module { source = "../../mocks/unrelated.sentinel" }
}
test { rules = { main = true } }
