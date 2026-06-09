import type { Context } from '../context.js';

interface UserRow {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
  availability: string;
}

interface AvailabilityInput {
  availableDays: string[];
}

interface UpdateUserInput {
  firstName?: string;
  lastName?: string;
  phoneNumber?: string;
  availability?: AvailabilityInput;
}

function hydrate(row: UserRow) {
  return {
    id: row.id,
    firstName: row.firstName,
    lastName: row.lastName,
    phoneNumber: row.phoneNumber,
    availability: JSON.parse(row.availability) as AvailabilityInput,
  };
}

export const userResolvers = {
  Query: {
    users: async (_: unknown, __: unknown, { knex }: Context) => {
      const rows = await knex<UserRow>('users').select('*').orderBy('firstName');
      return rows.map(hydrate);
    },
    user: async (_: unknown, args: { id: string }, { knex }: Context) => {
      const row = await knex<UserRow>('users').where({ id: args.id }).first();
      return row ? hydrate(row) : null;
    },
  },
  Mutation: {
    updateUser: async (
      _: unknown,
      args: { id: string; input: UpdateUserInput },
      { knex }: Context,
    ) => {
      const patch: Partial<UserRow> = {};
      if (args.input.firstName !== undefined) patch.firstName = args.input.firstName;
      if (args.input.lastName !== undefined) patch.lastName = args.input.lastName;
      if (args.input.phoneNumber !== undefined) patch.phoneNumber = args.input.phoneNumber;
      if (args.input.availability !== undefined) {
        patch.availability = JSON.stringify(args.input.availability);
      }

      await knex<UserRow>('users').where({ id: args.id }).update(patch);
      const row = await knex<UserRow>('users').where({ id: args.id }).first();
      if (!row) throw new Error(`User ${args.id} not found`);
      return hydrate(row);
    },
  },
};
