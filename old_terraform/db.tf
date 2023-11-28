resource "aws_dynamodb_table" "ConcertsTable" {
  name = "Concerts"
  billing_mode = "PROVISIONED"
  read_capacity = 10
  write_capacity = 10
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name = "ConcertsTable"
  }
}

resource "aws_dynamodb_table" "TicketsTable" {
  name = "Tickets"
  billing_mode = "PROVISIONED"
  read_capacity = 10
  write_capacity = 10
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name = "TicketsTable"
  }
}

resource "aws_dynamodb_table" "UsersTable" {
  name = "Users"
  billing_mode = "PROVISIONED"
  read_capacity = 10
  write_capacity = 10
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }
  tags = {
    Name = "UsersTable"
  }
}