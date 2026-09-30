mock "tfplan/v2" {
  module { source = "../../mocks/data-resource.sentinel" }
}
test { rules = { main = true } }
