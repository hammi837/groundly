var GroundlyWidget=(function(c){"use strict";function m(a,t){return{"Content-Type":"application/json","X-Api-Key":a}}async function C(a,t){const e=await fetch(`${a.replace(/\/$/,"")}/widget/config`,{headers:m(t)});if(!e.ok)throw new Error(`Config failed (${e.status})`);return e.json()}async function B(a){const t=await fetch(`${a.apiBase.replace(/\/$/,"")}/chat/message/stream`,{method:"POST",headers:m(a.apiKey),body:JSON.stringify({visitor_id:a.visitorId,conversation_id:a.conversationId,message:a.message})});if(!t.ok||!t.body){const i=await t.text();throw new Error(i||`Chat failed (${t.status})`)}const e=t.body.getReader(),n=new TextDecoder;let r="",s=null;for(;;){const{done:i,value:o}=await e.read();if(i)break;r+=n.decode(o,{stream:!0});const l=r.split(`

`);r=l.pop()||"";for(const p of l){const g=p.split(`
`);let d="message",b="";for(const h of g)h.startsWith("event:")&&(d=h.slice(6).trim()),h.startsWith("data:")&&(b+=h.slice(5).trim());if(!b)continue;const u=JSON.parse(b);if(d==="token"&&u.text)a.onToken(u.text);else if(d==="final")s=u;else if(d==="error")throw new Error(u.detail||"Stream error")}}if(!s)throw new Error("Stream ended without final event");return s}async function I(a){const t=await fetch(`${a.apiBase.replace(/\/$/,"")}/chat/handoff`,{method:"POST",headers:m(a.apiKey),body:JSON.stringify({conversation_id:a.conversationId,visitor_id:a.visitorId,email:a.email,name:a.name||null,phone:a.phone||null,question:a.question})});if(!t.ok){const e=await t.text();throw new Error(e||`Handoff failed (${t.status})`)}}function f(a){return a.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(new RegExp("(?<!\\*)\\*([^*]+)\\*(?!\\*)","g"),"<em>$1</em>").split(/\n{2,}/).map(i=>`<p>${i.replace(/\n/g,"<br>")}</p>`).join("")||"<p></p>"}function F(a){return`
:host {
  all: initial;
  font-family: "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;
  color: #0B1220;
  --g-primary: ${a||"#0F766E"};
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
`}const x=`
<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M8 6.5h12.5a3 3 0 0 1 3 3V22a4.5 4.5 0 0 1-4.5 4.5H11A3.5 3.5 0 0 1 7.5 23V9.5A3 3 0 0 1 10.5 6.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M12 14.5h8M12 18.5h5.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
  <circle cx="22.5" cy="22.5" r="3.2" fill="currentColor"/>
</svg>
`,y="groundly_visitor_id";function v(){return typeof crypto<"u"&&crypto.randomUUID?crypto.randomUUID():`v_${Math.random().toString(36).slice(2)}_${Date.now()}`}function q(){try{const a=localStorage.getItem(y);if(a)return a;const t=v();return localStorage.setItem(y,t),t}catch{return v()}}class k{constructor(t){this.config=null,this.open=!1,this.busy=!1,this.conversationId=null,this.visitorId=q(),this.lastQuestion="",this.options=t,this.host=document.createElement("div"),this.host.id="groundly-widget-host",document.body.appendChild(this.host),this.shadow=this.host.attachShadow({mode:"open"}),this.init()}async init(){var g;let t=this.options.primaryColor||"#0F766E",e=this.options.botName||"Support Assistant",n=this.options.welcomeMessage||"Hi! Ask me anything.",r=this.options.starterQuestions||[];try{this.config=await C(this.options.apiBaseUrl,this.options.apiKey),t=this.config.primary_color||t,e=this.config.bot_name||e,n=this.config.welcome_message||n,r=(g=this.config.starter_questions)!=null&&g.length?this.config.starter_questions:r}catch{}const s=document.createElement("style");s.textContent=F(t),this.shadow.appendChild(s),this.ensureFonts();const i=document.createElement("div");i.className="gw-root",i.innerHTML=`
      <div class="gw-panel" part="panel" role="dialog" aria-label="${M(e)}">
        <div class="gw-header">
          <div class="gw-header-left">
            <div class="gw-avatar">${x}</div>
            <div>
              <div class="gw-title">${E(e)}</div>
              <div class="gw-sub">Grounded answers</div>
            </div>
          </div>
          <button type="button" class="gw-close" aria-label="Close">×</button>
        </div>
        <div class="gw-messages"></div>
        <div class="gw-composer">
          <form class="gw-form">
            <textarea class="gw-input" rows="1" placeholder="Ask a question…" aria-label="Message"></textarea>
            <button class="gw-send" type="submit" aria-label="Send">↑</button>
          </form>
          <div class="gw-privacy">Ask about hours, insurance, or appointments</div>
        </div>
      </div>
      <button type="button" class="gw-launcher" aria-label="Open chat">${x}</button>
    `,this.shadow.appendChild(i),this.panel=i.querySelector(".gw-panel"),this.messagesEl=i.querySelector(".gw-messages"),this.input=i.querySelector(".gw-input"),this.sendBtn=i.querySelector(".gw-send");const o=i.querySelector(".gw-launcher"),l=i.querySelector(".gw-close"),p=i.querySelector(".gw-form");o.addEventListener("click",()=>this.setOpen(!this.open)),l.addEventListener("click",()=>this.setOpen(!1)),p.addEventListener("submit",d=>{d.preventDefault(),this.send(this.input.value)}),this.input.addEventListener("keydown",d=>{d.key==="Enter"&&!d.shiftKey&&(d.preventDefault(),this.send(this.input.value))}),this.addAssistant(n),r.length&&this.renderStarters(r)}ensureFonts(){const t="groundly-fonts";if(document.getElementById(t))return;const e=document.createElement("link");e.id=t,e.rel="stylesheet",e.href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",document.head.appendChild(e)}setOpen(t){this.open=t,this.panel.classList.toggle("open",t),t&&this.input.focus()}renderStarters(t){const e=document.createElement("div");e.className="gw-starters";for(const n of t){const r=document.createElement("button");r.type="button",r.className="gw-starter",r.textContent=n,r.addEventListener("click",()=>void this.send(n)),e.appendChild(r)}this.messagesEl.appendChild(e)}addUser(t){const e=document.createElement("div");e.className="gw-bubble user",e.textContent=t,this.messagesEl.appendChild(e),this.scrollBottom()}addAssistant(t){const e=document.createElement("div");return e.className="gw-bubble assistant",e.innerHTML=f(t),this.messagesEl.appendChild(e),this.scrollBottom(),e}showTyping(){const t=document.createElement("div");return t.className="gw-typing",t.innerHTML="<span></span><span></span><span></span>",this.messagesEl.appendChild(t),this.scrollBottom(),t}scrollBottom(){this.messagesEl.scrollTop=this.messagesEl.scrollHeight}async send(t){var i;const e=t.trim();if(!e||this.busy)return;this.busy=!0,this.lastQuestion=e,this.input.value="",this.sendBtn.disabled=!0,(i=this.messagesEl.querySelector(".gw-starters"))==null||i.remove(),this.addUser(e);const n=this.showTyping();let r=null,s="";try{const o=await B({apiBase:this.options.apiBaseUrl,apiKey:this.options.apiKey,visitorId:this.visitorId,conversationId:this.conversationId,message:e,onToken:l=>{r||(n.remove(),r=this.addAssistant("")),s+=l,r.innerHTML=f(s),this.scrollBottom()}});this.conversationId=o.conversation_id,n.remove(),r?r.innerHTML=f(o.answer):r=this.addAssistant(o.answer),o.was_fallback&&this.showLeadForm(o.conversation_id)}catch(o){n.remove();const l=o instanceof Error?o.message:"Something went wrong";this.addAssistant(`Sorry — ${l}`)}finally{this.busy=!1,this.sendBtn.disabled=!1,this.input.focus()}}showLeadForm(t){const e=document.createElement("div");e.className="gw-lead",e.innerHTML=`
      <h4>Connect with the team</h4>
      <p>I’m not sure about that. Leave your details and someone will follow up.</p>
      <input type="email" name="email" placeholder="Email *" required />
      <input type="text" name="name" placeholder="Name (optional)" />
      <input type="tel" name="phone" placeholder="Phone (optional)" />
      <div class="gw-lead-actions">
        <button type="button" class="gw-btn primary">Send</button>
        <button type="button" class="gw-btn ghost">Dismiss</button>
      </div>
    `;const n=e.querySelector('input[name="email"]'),r=e.querySelector('input[name="name"]'),s=e.querySelector('input[name="phone"]'),i=e.querySelector(".gw-btn.primary");e.querySelector(".gw-btn.ghost").addEventListener("click",()=>e.remove()),i.addEventListener("click",async()=>{if(!n.value.trim()){n.focus();return}i.disabled=!0;try{await I({apiBase:this.options.apiBaseUrl,apiKey:this.options.apiKey,conversationId:t,visitorId:this.visitorId,email:n.value.trim(),name:r.value.trim()||void 0,phone:s.value.trim()||void 0,question:this.lastQuestion}),e.innerHTML="<h4>Thanks</h4><p>Your note is with the team. We’ll be in touch.</p>"}catch(l){i.disabled=!1;const p=l instanceof Error?l.message:"Failed";e.querySelector("p").textContent=p}}),this.messagesEl.appendChild(e),this.scrollBottom()}}function E(a){return a.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}function M(a){return E(a).replace(/'/g,"&#39;")}function w(a){return new k(a)}function A(){const a=document.currentScript||document.querySelector("script[data-groundly-api-key], script[data-api-key]");if(!a)return null;const t=a.getAttribute("data-groundly-api-key")||a.getAttribute("data-api-key")||"",e=a.getAttribute("data-groundly-api-base")||a.getAttribute("data-api-base")||"";if(!t||!e)return null;const n=a.getAttribute("data-starter-questions")||a.getAttribute("data-starters")||"",r=n?n.split("|").map(s=>s.trim()).filter(Boolean):void 0;return{apiKey:t,apiBaseUrl:e,botName:a.getAttribute("data-bot-name")||void 0,primaryColor:a.getAttribute("data-primary-color")||void 0,welcomeMessage:a.getAttribute("data-welcome")||void 0,starterQuestions:r}}function S(){window.GroundlyWidget={mount:w};const a=A();a&&w(a)}return document.readyState==="loading"?document.addEventListener("DOMContentLoaded",S):S(),c.GroundlyChat=k,c.mountGroundlyWidget=w,Object.defineProperty(c,Symbol.toStringTag,{value:"Module"}),c})({});
//# sourceMappingURL=widget.js.map
