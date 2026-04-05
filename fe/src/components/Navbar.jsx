export default function Navbar({ role, setRole, theme, toggleTheme, currentPath }) {
  return (
    <header className="navbar">
      <div>
        <p className="eyebrow">Finance Data Processing and Access Control</p>
        <h1>Zorvyn API Playground</h1>
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
          Theme: {theme}
        </button>
      </div>
    </header>
  );
}
