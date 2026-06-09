import type { Knex } from 'knex';

export interface Context {
  knex: Knex;
}
