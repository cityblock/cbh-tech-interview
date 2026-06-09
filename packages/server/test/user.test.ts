import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import Knex from 'knex';
import { createYoga } from 'graphql-yoga';
import { schema } from '../src/schema.js';
import { migrate } from '../src/db/migrate.js';
import { seed } from '../src/db/seed.js';

interface UserShape {
  id: string;
  firstName: string;
  phoneNumber: string;
  availability: { availableDays: string[] };
}

const knex = Knex({
  client: 'better-sqlite3',
  connection: { filename: ':memory:' },
  useNullAsDefault: true,
  pool: { min: 1, max: 1 },
});

const yoga = createYoga({ schema, context: () => ({ knex }) });

async function gql<T>(query: string, variables?: Record<string, unknown>) {
  const res = await yoga.fetch('http://test/graphql', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query, variables }),
  });
  return (await res.json()) as { data: T; errors?: unknown };
}

beforeAll(async () => {
  await migrate(knex);
  await seed(knex);
});

afterAll(async () => {
  await knex.destroy();
});

describe('user resolvers', () => {
  it('lists seeded users with parsed availability', async () => {
    const result = await gql<{ users: UserShape[] }>(
      `{ users { id firstName availability { availableDays } } }`,
    );
    expect(result.errors).toBeUndefined();
    expect(result.data.users.length).toBeGreaterThan(0);
    expect(Array.isArray(result.data.users[0]!.availability.availableDays)).toBe(true);
  });

  it('updates phoneNumber and availability', async () => {
    const list = await gql<{ users: UserShape[] }>(`{ users { id } }`);
    const id = list.data.users[0]!.id;

    const updated = await gql<{ updateUser: UserShape }>(
      `mutation U($id: ID!, $input: UpdateUserInput!) {
        updateUser(id: $id, input: $input) {
          id phoneNumber availability { availableDays }
        }
      }`,
      { id, input: { phoneNumber: '+15550000000', availability: { availableDays: ['Mon'] } } },
    );
    expect(updated.errors).toBeUndefined();
    expect(updated.data.updateUser.phoneNumber).toBe('+15550000000');
    expect(updated.data.updateUser.availability.availableDays).toEqual(['Mon']);
  });
});
