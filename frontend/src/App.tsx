export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "var(--font-ui)",
        background: "linear-gradient(180deg, #f7f9f8 0%, #eef6f4 45%, #f7f9f8 100%)",
        color: "var(--color-text)",
        padding: "2rem",
      }}
    >
      <header style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <img src="/brand/groundly-mark-icon.png" alt="Groundly" width={40} height={40} />
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: "1.75rem", margin: 0 }}>
            Groundly
          </h1>
          <p style={{ margin: 0, color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
            AI support that only answers from your docs
          </p>
        </div>
      </header>
      <main style={{ marginTop: "2rem" }}>
        <p>Admin shell — pages land in Phase 5.</p>
      </main>
    </div>
  );
}
