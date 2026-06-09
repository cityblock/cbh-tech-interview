import { createSchema } from 'graphql-yoga';
import { userResolvers } from './resolvers/user.js';
import type { Context } from './context.js';

const typeDefs = /* GraphQL */ `
  type User {
    id: ID!
    firstName: String!
    lastName: String!
    phoneNumber: String!
    availability: UserAvailability!
  }

  type UserAvailability {
    availableDays: [String!]!
  }

  input UpdateUserInput {
    firstName: String
    lastName: String
    phoneNumber: String
    availability: UserAvailabilityInput
  }

  input UserAvailabilityInput {
    availableDays: [String!]!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
  }

  type Mutation {
    updateUser(id: ID!, input: UpdateUserInput!): User!
  }
`;

export const schema = createSchema<Context>({
  typeDefs,
  resolvers: {
    Query: userResolvers.Query,
    Mutation: userResolvers.Mutation,
  },
});
