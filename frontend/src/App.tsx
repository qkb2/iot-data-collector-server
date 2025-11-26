import { Outlet, Link } from 'react-router-dom'
import "./App.css";

function App() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">ESP Dashboard</h1>
      <nav className="mb-4">
        <Link to="/" className="text-blue-600">
          Devices
        </Link>
      </nav>
      <Outlet />
    </div>
  );
}

export default App;
