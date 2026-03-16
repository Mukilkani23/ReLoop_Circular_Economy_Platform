/**
 * Navbar Component — Top navigation with auth state awareness.
 */
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link';

  if (!isAuthenticated) return null;

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/dashboard" className="navbar-logo">
          <span className="logo-icon">♻️</span>
          <span>ReLoop</span>
        </Link>

        <div className="navbar-links">
          <Link to="/dashboard" className={isActive('/dashboard')}>
            📊 Dashboard
          </Link>
          <Link to="/marketplace" className={isActive('/marketplace')}>
            🏪 Marketplace
          </Link>
        </div>

        <div className="nav-user">
          <div className="nav-user-info">
            <div className="nav-user-name">{user?.username}</div>
            <div className="nav-user-role">{user?.role}</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
