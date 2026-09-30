mock "tfplan/v2" {
  module { source = "../../mocks/delete-only.sentinel" }
}
test { rules = { main = true } }
