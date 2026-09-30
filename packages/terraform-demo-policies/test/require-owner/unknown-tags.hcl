mock "tfplan/v2" {
  module { source = "../../mocks/unknown-tags.sentinel" }
}
test { rules = { main = false } }
