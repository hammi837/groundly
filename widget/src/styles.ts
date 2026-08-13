/** CSS injected into Shadow DOM — Groundly design tokens. */
export function widgetStyles(primary: string): string {
  const teal = primary || "#0F766E";
  return `
:host {
  all: initial;
  font-family: "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;
  color: #0B1220;
  --g-primary: ${teal};
  --g-primary-hover: #0D9488;
  --g-accent: #CCFBF1;
  --g-ink: #0B1220;
  --g-muted: #64748B;
  --g-line: #E2E8F0;
  --g-surface: #F7F9F8;
  --g-card: #FFFFFF;
  --g-radius: 10px;
}

*, *::before, *::after { box-sizing: border-box; }

.gw-root {
  position: fixed;
  z-index: 2147483000;
  right: 20px;
  bottom: 20px;
  font-size: 14px;
  line-height: 1.45;
}

.gw-launcher {
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  background: var(--g-primary);
  color: #fff;
  cursor: pointer;
  display: grid;
  place-items: center;
  box-shadow: 0 8px 24px rgba(11, 18, 32, 0.18);
  transition: transform 200ms ease-out, background 160ms ease-out;
}
.gw-launcher:hover { background: var(--g-primary-hover); transform: translateY(-1px); }
.gw-launcher svg { width: 26px; height: 26px; display: block; }

.gw-panel {
  position: absolute;
  right: 0;
  bottom: 68px;
  width: min(380px, calc(100vw - 24px));
  height: min(560px, calc(100vh - 100px));
  background: linear-gradient(180deg, #F7F9F8 0%, #EEF6F4 50%, #F7F9F8 100%);
  border: 1px solid var(--g-line);
  border-radius: 14px;
  box-shadow: 0 18px 50px rgba(11, 18, 32, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  opacity: 0;
  transform: translateY(10px) scale(0.98);
  pointer-events: none;
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}
.gw-panel.open {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.gw-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.85);
  border-bottom: 1px solid var(--g-line);
}
.gw-header-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.gw-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--g-primary); color: #fff;
  display: grid; place-items: center; flex-shrink: 0;
}
.gw-avatar svg { width: 18px; height: 18px; }
.gw-title { font-weight: 700; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gw-sub { font-size: 11px; color: var(--g-muted); }
.gw-close {
  border: none; background: transparent; color: var(--g-muted);
  width: 32px; height: 32px; border-radius: 8px; cursor: pointer; font-size: 18px;
}
.gw-close:hover { background: var(--g-accent); color: var(--g-ink); }

.gw-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gw-bubble {
  max-width: 92%;
  padding: 10px 12px;
  border-radius: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}
.gw-bubble.user {
  align-self: flex-end;
  background: var(--g-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.gw-bubble.assistant {
  align-self: flex-start;
  background: var(--g-card);
  border: 1px solid var(--g-line);
  border-bottom-left-radius: 4px;
}
.gw-bubble.assistant p { margin: 0 0 0.5em; }
.gw-bubble.assistant p:last-child { margin-bottom: 0; }
.gw-bubble.assistant strong { font-weight: 600; }
.gw-bubble.assistant code {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 12px;
  background: var(--g-accent);
  padding: 1px 4px;
  border-radius: 4px;
}

.gw-citations {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.gw-chip {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 11px;
  color: var(--g-primary);
  background: var(--g-accent);
  border-radius: 6px;
  padding: 3px 7px;
  animation: gwChipIn 220ms ease-out both;
}
.gw-chip:nth-child(2) { animation-delay: 40ms; }
.gw-chip:nth-child(3) { animation-delay: 80ms; }
@keyframes gwChipIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.gw-typing {
  align-self: flex-start;
  display: inline-flex;
  gap: 4px;
  padding: 10px 12px;
  background: var(--g-card);
  border: 1px solid var(--g-line);
  border-radius: 12px;
}
.gw-typing span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--g-muted);
  animation: gwDot 1s infinite ease-in-out;
}
.gw-typing span:nth-child(2) { animation-delay: 0.15s; }
.gw-typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes gwDot {
  0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-3px); }
}

.gw-starters {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}
.gw-starter {
  text-align: left;
  border: 1px solid var(--g-line);
  background: var(--g-card);
  color: var(--g-ink);
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  font: inherit;
  transition: border-color 140ms ease, background 140ms ease;
}
.gw-starter:hover { border-color: var(--g-primary); background: var(--g-accent); }

.gw-lead {
  align-self: stretch;
  border: 1px dashed var(--g-line);
  background: var(--g-card);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.gw-lead h4 { margin: 0; font-size: 13px; }
.gw-lead p { margin: 0; font-size: 12px; color: var(--g-muted); }
.gw-lead input {
  border: 1px solid var(--g-line);
  border-radius: 8px;
  padding: 8px 10px;
  font: inherit;
  background: #fff;
}
.gw-lead input:focus {
  outline: 2px solid var(--g-primary);
  outline-offset: 1px;
}
.gw-lead-actions { display: flex; gap: 8px; }
.gw-btn {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
.gw-btn.primary { background: var(--g-primary); color: #fff; }
.gw-btn.primary:hover { background: var(--g-primary-hover); }
.gw-btn.ghost { background: transparent; color: var(--g-muted); border: 1px solid var(--g-line); }

.gw-composer {
  border-top: 1px solid var(--g-line);
  background: rgba(255,255,255,0.9);
  padding: 10px 12px 8px;
}
.gw-form {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
.gw-input {
  flex: 1;
  resize: none;
  min-height: 42px;
  max-height: 100px;
  border: 1px solid var(--g-line);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
  background: #fff;
}
.gw-input:focus {
  outline: 2px solid var(--g-primary);
  outline-offset: 1px;
}
.gw-send {
  border: none;
  border-radius: 10px;
  background: var(--g-primary);
  color: #fff;
  width: 42px;
  height: 42px;
  cursor: pointer;
  font-weight: 700;
}
.gw-send:disabled { opacity: 0.5; cursor: not-allowed; }
.gw-privacy {
  margin: 6px 2px 0;
  font-size: 11px;
  color: var(--g-muted);
  text-align: center;
}

@media (max-width: 480px) {
  .gw-root { right: 0; bottom: 0; left: 0; }
  .gw-launcher { position: absolute; right: 16px; bottom: 16px; }
  .gw-panel {
    right: 0; left: 0; bottom: 0;
    width: 100vw;
    height: min(78vh, 640px);
    border-radius: 16px 16px 0 0;
  }
}
`;
}

export const MARK_SVG = `
<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M8 6.5h12.5a3 3 0 0 1 3 3V22a4.5 4.5 0 0 1-4.5 4.5H11A3.5 3.5 0 0 1 7.5 23V9.5A3 3 0 0 1 10.5 6.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M12 14.5h8M12 18.5h5.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="22.5" cy="22.5" r="3.2" fill="currentColor"/>
</svg>
`;
