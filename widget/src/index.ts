import { mountGroundlyWidget, type MountOptions } from "./widget";

export { mountGroundlyWidget, GroundlyChat } from "./widget";
export type { MountOptions } from "./widget";

declare global {
  interface Window {
    GroundlyWidget?: {
      mount: typeof mountGroundlyWidget;
    };
  }
}

function readScriptConfig(): MountOptions | null {
  const script =
    document.currentScript ||
    document.querySelector<HTMLScriptElement>("script[data-groundly-api-key], script[data-api-key]");
  if (!script) return null;

  const apiKey =
    script.getAttribute("data-groundly-api-key") ||
    script.getAttribute("data-api-key") ||
    "";
  const apiBaseUrl =
    script.getAttribute("data-groundly-api-base") ||
    script.getAttribute("data-api-base") ||
    "";

  if (!apiKey || !apiBaseUrl) return null;

  const startersRaw =
    script.getAttribute("data-starter-questions") ||
    script.getAttribute("data-starters") ||
    "";
  const starterQuestions = startersRaw
    ? startersRaw.split("|").map((s) => s.trim()).filter(Boolean)
    : undefined;

  return {
    apiKey,
    apiBaseUrl,
    botName: script.getAttribute("data-bot-name") || undefined,
    primaryColor: script.getAttribute("data-primary-color") || undefined,
    welcomeMessage: script.getAttribute("data-welcome") || undefined,
    starterQuestions,
  };
}

function autoMount() {
  window.GroundlyWidget = { mount: mountGroundlyWidget };
  const opts = readScriptConfig();
  if (opts) {
    mountGroundlyWidget(opts);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", autoMount);
} else {
  autoMount();
}
