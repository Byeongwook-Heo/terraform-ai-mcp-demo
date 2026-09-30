mock "tfplan/v2" {
  module { source = "../../mocks/normal.sentinel" }
}
test { rules = { main = true } }
