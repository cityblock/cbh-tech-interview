import type { Knex } from 'knex';
import * as users from './migrations/0001_users.js';

const migrations = [{ name: '0001_users', module: users }];

// Tracks which migrations have already run so boot is safe against a persisted
// database — each migration's `up()` runs exactly once, ever.
async function ensureMigrationsTable(knex: Knex): Promise<void> {
  if (!(await knex.schema.hasTable('_migrations'))) {
    await knex.schema.createTable('_migrations', (t) => {
      t.text('name').primary();
    });
  }
}

export async function migrate(knex: Knex): Promise<void> {
  await ensureMigrationsTable(knex);
  for (const m of migrations) {
    const applied = await knex('_migrations').where({ name: m.name }).first();
    if (applied) continue;
    await m.module.up(knex);
    await knex('_migrations').insert({ name: m.name });
  }
}
