mock "tfplan/v2" {
  module { source = "../../mocks/no-op-missing.sentinel" }
}
test { rules = { main = false } }
