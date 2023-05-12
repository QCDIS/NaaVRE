nested_data <- list(
  name = "John Doe",
  age = 30,
  address = list(
    street = "123 Main St",
    city = "New York",
    state = "NY",
    zip = 10001
  ),
  hobbies = c("reading", "cooking", "sports"),
  friends = list(
    list(name = "Jane Smith", age = 28),
    list(name = "Mike Johnson", age = 32)
  )
)

typeof(nested_data)