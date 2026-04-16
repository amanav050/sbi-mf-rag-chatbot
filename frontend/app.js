const API_URL = "https://amanav050-sbi-mf-rag-chatbot.hf.space/chat";
let threads = [], activeId = null, chatOpen = false, drawerOpen = false;

function gid() { return "t_" + Math.random().toString(36).substr(2, 9) + Date.now(); }
function mk() { const t = { id: gid(), sid: "s_" + Math.random().toString(36).substr(2, 9), name: "New Chat", msgs: [], at: new Date().toISOString() }; threads.unshift(t); return t; }
function cur() { return threads.find(t => t.id === activeId); }

async function api(q, sid) {
    const r = await fetch(API_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: q, session_id: sid }) });
    if (!r.ok) throw new Error("API " + r.status);
    return r.json();
}

function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById("fp").classList.toggle("open", chatOpen);
    document.getElementById("fab").classList.toggle("active", chatOpen);
    if (chatOpen && !activeId) startNew();
    if (chatOpen) setTimeout(() => document.getElementById("chatInput").focus(), 100);
}

function openChat(q) {
    if (!chatOpen) toggleChat();
    if (q) setTimeout(() => handleSend(q), 200);
}

function toggleDrawer() { drawerOpen = !drawerOpen; document.getElementById("fpDrawer").classList.toggle("open", drawerOpen); }
function closeDrawer() { drawerOpen = false; document.getElementById("fpDrawer").classList.remove("open"); }

function startNew() { const t = mk(); activeId = t.id; renderList(); renderMsgs(); closeDrawer(); }
function switchTo(id) { activeId = id; renderList(); renderMsgs(); closeDrawer(); }

function renderList() {
    const el = document.getElementById("threadList");
    el.innerHTML = "";
    threads.forEach(t => {
        const d = document.createElement("div");
        d.className = "th-it" + (t.id === activeId ? " active" : "");
        d.onclick = () => switchTo(t.id);
        d.innerHTML = `<div class="th-dt"></div><div class="th-inf"><div class="th-nm">${esc(t.name)}</div><div class="th-tm">${rel(t.at)}</div></div>`;
        el.appendChild(d);
    });
}

function renderMsgs() {
    const c = document.getElementById("messages");
    const t = cur();
    c.innerHTML = "";
    if (!t || t.msgs.length === 0) {
        c.innerHTML = `
            <div class="welc">
                <div class="w-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="3"/></svg></div>
                <p class="w-title">What would you like to know?</p>
                <p class="w-sub">Ask about NAVs, expense ratios, fund objectives, lock-in periods, or anything from official SBI MF documents.</p>
                <div class="w-chips">
                    <button class="w-ch" data-q="What is the NAV of SBI Large Cap Fund?"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>NAV of Large Cap</button>
                    <button class="w-ch" data-q="What is the expense ratio of SBI Small Cap Fund?"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12h8"/></svg>Expense ratio</button>
                    <button class="w-ch" data-q="What is the lock-in period for SBI ELSS Tax Saver Fund?"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>ELSS lock-in</button>
                </div>
            </div>`;
        c.querySelectorAll(".w-ch").forEach(ch => ch.addEventListener("click", () => handleSend(ch.getAttribute("data-q"))));
        return;
    }
    t.msgs.forEach(m => { if (m.role === "user") uBub(m.text, false); else bBub(m.text, m.src, m.date, m.ref, false); });
    scr();
}

function uBub(text, doScr = true) {
    const c = document.getElementById("messages");
    const w = c.querySelector(".welc"); if (w) w.remove();
    const d = document.createElement("div");
    d.className = "msg msg-u";
    d.innerHTML = `<div class="m-cl"><div class="m-bb m-us">${esc(text)}</div></div>`;
    c.appendChild(d);
    if (doScr) scr();
}

function bBub(text, srcUrl, srcDate, isRef, doScr = true) {
    const c = document.getElementById("messages");
    let clean = text, url = srcUrl || "", date = srcDate || "";
    const sm = clean.match(/\n\nSource:\s*(https?:\/\/\S+)/); if (sm) { url = url || sm[1]; clean = clean.replace(sm[0], ""); }
    const dm = clean.match(/\nLast updated from sources:\s*(.+)/); if (dm) { date = date || dm[1]; clean = clean.replace(dm[0], ""); }
    const meta = (url && url !== "N/A") ? `<div class="m-mt"><span class="m-sr"><a href="${esc(url)}" target="_blank">View source</a></span>${date && date !== "N/A" ? ` <span class="m-dt">· ${esc(date)}</span>` : ""}</div>` : "";
    const d = document.createElement("div");
    d.className = "msg msg-b";
    d.innerHTML = `<div class="m-av"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="3"/></svg></div><div class="m-cl"><div class="m-bb m-bt${isRef ? " m-er" : ""}">${esc(clean.trim())}</div>${meta}</div>`;
    c.appendChild(d);
    if (doScr) scr();
}

function showTyp() {
    const c = document.getElementById("messages");
    const d = document.createElement("div"); d.className = "typ-w"; d.id = "typ";
    d.innerHTML = `<div class="m-av"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="3"/></svg></div><div class="typ-d"><div class="t-d"></div><div class="t-d"></div><div class="t-d"></div></div>`;
    c.appendChild(d); scr();
}
function hideTyp() { const e = document.getElementById("typ"); if (e) e.remove(); }

async function handleSend(override) {
    const input = document.getElementById("chatInput");
    const q = override || input.value.trim();
    if (!q) return;
    const t = cur(); if (!t) return;
    if (t.msgs.length === 0) { t.name = q.length > 28 ? q.substring(0, 28) + "..." : q; renderList(); }
    t.msgs.push({ role: "user", text: q });
    uBub(q); input.value = ""; showTyp();
    try {
        const data = await api(q, t.sid);
        hideTyp();
        t.msgs.push({ role: "bot", text: data.answer, src: data.source_url, date: data.scraped_date, ref: data.is_refusal || false });
        bBub(data.answer, data.source_url, data.scraped_date, data.is_refusal);
    } catch (e) { hideTyp(); bBub("Something went wrong. Please try again.", "", "", false); }
}

function scr() { const c = document.getElementById("messages"); setTimeout(() => c.scrollTop = c.scrollHeight, 40); }
function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
function rel(iso) { const m = Math.floor((Date.now() - new Date(iso)) / 60000); if (m < 1) return "Now"; if (m < 60) return m + "m"; const h = Math.floor(m / 60); if (h < 24) return h + "h"; return Math.floor(h / 24) + "d"; }

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("fab").addEventListener("click", toggleChat);
    document.getElementById("sendBtn").addEventListener("click", () => handleSend());
    document.getElementById("chatInput").addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); handleSend(); } });
    document.getElementById("fpNew").addEventListener("click", startNew);
    document.querySelectorAll(".s-card").forEach(c => c.addEventListener("click", () => openChat(c.getAttribute("data-query"))));
});
