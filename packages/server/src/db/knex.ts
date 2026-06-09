import path from 'node:path';
import fs from 'node:fs';
import Knex from 'knex';

// Persist to a file by default so state survives restarts.
// Set DB_FILE=:memory: for an ephemeral database (e.g. tests, throwaway runs).
const DB_FILE = process.env.DB_FILE ?? path.resolve(process.cwd(), 'data/app.sqlite');
if (DB_FILE !== ':memory:') {
  fs.mkdirSync(path.dirname(DB_FILE), { recursive: true });
}

export const knex = Knex({
  client: 'better-sqlite3',
  connection: { filename: DB_FILE },
  useNullAsDefault: true,
  pool: { min: 1, max: 1 },
});

export type Knex = typeof knex;
