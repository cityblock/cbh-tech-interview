USERS_QUERY = """
  query Users {
    users {
      id
      firstName
      lastName
      phoneNumber
      availability {
        availableDays
      }
    }
  }
"""

USER_QUERY = """
  query User($id: ID!) {
    user(id: $id) {
      id
      firstName
      lastName
      phoneNumber
      availability {
        availableDays
      }
    }
  }
"""

UPDATE_USER_MUTATION = """
  mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
    updateUser(id: $id, input: $input) {
      id
      firstName
      lastName
      phoneNumber
      availability {
        availableDays
      }
    }
  }
"""
