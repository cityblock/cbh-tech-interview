import { gql } from '@apollo/client';

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
  availability: { availableDays: string[] };
}

export const USERS_QUERY = gql`
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
`;

export const USER_QUERY = gql`
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
`;

export const UPDATE_USER_MUTATION = gql`
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
`;
