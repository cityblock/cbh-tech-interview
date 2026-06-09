import { useQuery } from '@apollo/client';
import { Link } from 'react-router-dom';
import { USERS_QUERY, type User } from '../graphql/user.js';

export function UserList() {
  const { data, loading, error } = useQuery<{ users: User[] }>(USERS_QUERY);

  if (loading) return <p>Loading…</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="container">
      <h1>Users</h1>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Available days</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {data?.users.map((u) => (
            <tr key={u.id}>
              <td>
                {u.firstName} {u.lastName}
              </td>
              <td>{u.phoneNumber}</td>
              <td>
                {u.availability.availableDays.map((d) => (
                  <span key={d} className="badge">
                    {d}
                  </span>
                ))}
              </td>
              <td>
                <Link to={`/users/${u.id}`}>Edit</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
