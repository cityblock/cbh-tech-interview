import { Routes, Route } from 'react-router-dom';
import { UserList } from './pages/UserList.js';
import { UserEdit } from './pages/UserEdit.js';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<UserList />} />
      <Route path="/users/:id" element={<UserEdit />} />
    </Routes>
  );
}
