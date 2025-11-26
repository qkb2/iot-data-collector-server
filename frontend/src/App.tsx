import { Outlet, Link } from "react-router-dom";
import "./App.css";

export default function App() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">ESP Dashboard</h1>
        <nav>
          <Link
            to="/"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Devices
          </Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
