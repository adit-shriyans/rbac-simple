import { Github, Moon, Sun } from "lucide-react";

export default function Navbar({ role, setRole, theme, toggleTheme, currentPath }) {
  return (
    <header className="navbar">
      <div>
        <p className="eyebrow">Finance Data Processing and Access Control</p>
        <div className="title-row">
          <h1>Zorvyn API Playground</h1>
          <a
            href="https://github.com/adit-shriyans/rbac-simple"
            target="_blank"
            rel="noreferrer"
            className="icon-link"
            aria-label="Open GitHub repository"
            title="Open GitHub repository"
          >
            <Github size={19} strokeWidth={2} />
          </a>
        </div>
        <div className="nav-links">
          <a href="/" className={`nav-link${currentPath === "/" ? " active" : ""}`}>
            Playground
          </a>
          <a href="/test" className={`nav-link${currentPath === "/test" ? " active" : ""}`}>
            Tests
          </a>
        </div>
      </div>

      <div className="navbar-controls">
        {currentPath !== "/test" ? (
          <label className="control">
            <span>Role</span>
            <select value={role} onChange={(event) => setRole(event.target.value)}>
              <option value="viewer">viewer</option>
              <option value="analyst">analyst</option>
              <option value="admin">admin</option>
            </select>
          </label>
        ) : null}

        <button type="button" className="secondary-button" onClick={toggleTheme}>
          {theme === "dark" ? <Moon size={18} strokeWidth={2} /> : <Sun size={18} strokeWidth={2} />}
        </button>
      </div>
    </header>
  );
}
