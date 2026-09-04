import { createServer } from 'node:http';
import { createYoga } from 'graphql-yoga';
import { schema } from './schema.js';
import { knex } from './db/knex.js';
import { migrate } from './db/migrate.js';
import { seed } from './db/seed.js';

const PORT = Number(process.env.PORT ?? 4000);

async function main() {
  await migrate(knex);
  await seed(knex);

  const yoga = createYoga({
    schema,
    context: () => ({ knex }),
    graphqlEndpoint: '/graphql',
    cors: { origin: '*', credentials: true },
  });

  const server = createServer(yoga);
  server.listen(PORT, () => {
    console.log(`🚀 GraphQL server ready at http://localhost:${PORT}/graphql`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
