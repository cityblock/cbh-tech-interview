import { randomUUID } from 'node:crypto';
import type { Knex } from 'knex';

export async function seed(knex: Knex): Promise<void> {
  // Only seed an empty table so edits survive restarts on a persisted database.
  const existing = await knex('users').count({ count: '*' }).first();
  if (Number(existing?.count ?? 0) > 0) return;

  await knex('users').insert([
    {
      id: randomUUID(),
      firstName: 'Ada',
      lastName: 'Lovelace',
      phoneNumber: '+15555550101',
      availability: JSON.stringify({ availableDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] }),
    },
    {
      id: randomUUID(),
      firstName: 'Grace',
      lastName: 'Hopper',
      phoneNumber: '+15555550102',
      availability: JSON.stringify({ availableDays: ['Tue', 'Wed', 'Thu'] }),
    },
    {
      id: randomUUID(),
      firstName: 'Katherine',
      lastName: 'Johnson',
      phoneNumber: '+15555550103',
      availability: JSON.stringify({ availableDays: ['Sat', 'Sun'] }),
    },
    {
      id: randomUUID(),
      firstName: 'Mae',
      lastName: 'Jemison',
      phoneNumber: '+15555550104',
      availability: JSON.stringify({ availableDays: ['Mon', 'Wed', 'Fri'] }),
    },
  ]);
}
