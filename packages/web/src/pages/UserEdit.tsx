import { useMutation, useQuery } from '@apollo/client';
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { UPDATE_USER_MUTATION, USERS_QUERY, USER_QUERY, type User } from '../graphql/user.js';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function UserEdit() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const { data, loading, error } = useQuery<{ user: User | null }>(USER_QUERY, {
    variables: { id },
  });
  const [updateUser, { loading: saving }] = useMutation(UPDATE_USER_MUTATION, {
    refetchQueries: [{ query: USERS_QUERY }],
  });

  const [phoneNumber, setPhoneNumber] = useState('');
  const [availableDays, setAvailableDays] = useState<string[]>([]);

  useEffect(() => {
    if (data?.user) {
      setPhoneNumber(data.user.phoneNumber);
      setAvailableDays(data.user.availability.availableDays);
    }
  }, [data]);

  if (loading) return <p>Loading…</p>;
  if (error) return <p>Error: {error.message}</p>;
  if (!data?.user) return <p>User not found.</p>;

  const toggleDay = (day: string) => {
    setAvailableDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day],
    );
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateUser({
      variables: {
        id,
        input: { phoneNumber, availability: { availableDays } },
      },
    });
    navigate('/');
  };

  return (
    <div className="container">
      <h1>
        Edit: {data.user.firstName} {data.user.lastName}
      </h1>
      <form className="card" onSubmit={onSubmit}>
        <label>
          <span>Phone number</span>
          <input type="text" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
        </label>
        <div>
          <span style={{ fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
            Available days
          </span>
          <div className="days">
            {DAYS.map((d) => (
              <label key={d}>
                <input
                  type="checkbox"
                  checked={availableDays.includes(d)}
                  onChange={() => toggleDay(d)}
                />
                {d}
              </label>
            ))}
          </div>
        </div>
        <div style={{ marginTop: '1.5rem' }}>
          <button type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
          <Link to="/" className="secondary" style={{ marginLeft: '0.5rem' }}>
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
