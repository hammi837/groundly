import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";

const nav = [
  { to: "/", label: "Overview", end: true },
  { to: "/documents", label: "Documents" },
  { to: "/conversations", label: "Conversations" },
  { to: "/leads", label: "Leads" },
  { to: "/settings", label: "Settings" },
];

export function AppShell() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <img src="/brand/groundly-mark-icon.png" alt="" width={36} height={36} />
          <div>
            <div className="brand-name">Groundly</div>
            <div className="brand-tag">Grounded support</div>
          </div>
        </div>
        <nav className="nav">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="tenant-name">{user?.tenant.name}</div>
          <button type="button" className="btn ghost small" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <img
            className="topbar-lockup"
            src="/brand/groundly-logo-lockup.png"
            alt="Groundly"
            height={28}
          />
          <span className="topbar-meta">{user?.email}</span>
        </header>
        <Outlet />
      </div>
    </div>
  );
}
