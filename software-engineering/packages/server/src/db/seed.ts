import type { Knex } from 'knex';
import { seed as seedUsers } from './seeds/users.js';

export async function seed(knex: Knex): Promise<void> {
  await seedUsers(knex);
}
