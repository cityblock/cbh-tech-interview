import type { Knex } from 'knex';

// `availability` is stored as a JSON-encoded text column.
// In production this would be a Postgres jsonb; SQLite has no jsonb type,
// so the resolvers parse/stringify at the boundary.
export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('users', (t) => {
    t.text('id').primary();
    t.text('firstName').notNullable();
    t.text('lastName').notNullable();
    t.text('phoneNumber').notNullable();
    t.text('availability').notNullable();
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTable('users');
}
