let currentDocType = "rental";
let currentDocumentId = null;

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadStatus = document.getElementById("uploadStatus");
const workspace = document.getElementById("workspace");
const runScanBtn = document.getElementById("runScanBtn");
const scanResults = document.getElementById("scanResults");
const chatLog = document.getElementById("chatLog");
const chatInput = document.getElementById("chatInput");
const chatSendBtn = document.getElementById("chatSendBtn");

// ---- doc type tabs ----
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    currentDocType = tab.dataset.doctype;
  });
});

// ---- workspace tabs ----
document.querySelectorAll(".wtab").forEach((wtab) => {
  wtab.addEventListener("click", () => {
    document.querySelectorAll(".wtab").forEach((t) => t.classList.remove("active"));
    wtab.classList.add("active");
    document.getElementById("panel-scan").hidden = wtab.dataset.panel !== "scan";
    document.getElementById("panel-chat").hidden = wtab.dataset.panel !== "chat";
  });
});

// ---- upload handling ----
browseBtn.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("click", (e) => {
  if (e.target !== browseBtn) fileInput.click();
});
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length) uploadFiles(Array.from(e.dataTransfer.files));
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) uploadFiles(Array.from(fileInput.files));
});

async function uploadFiles(files) {
  // Sort by filename so "page1.jpg, page2.jpg, page3.jpg" upload in the
  // right order even if the OS's file picker returned them out of order.
  files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));

  const label = files.length === 1 ? files[0].name : `${files.length} files`;
  setUploadStatus(`Indexing ${label}…`, "");

  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  formData.append("doc_type", currentDocType);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");

    currentDocumentId = data.document_id;
    setUploadStatus(`✓ ${data.message}`, "success");
    workspace.hidden = false;
    scanResults.innerHTML = "";
    chatLog.innerHTML = '<div class="chat-hint">Ask anything about the uploaded document.</div>';
  } catch (err) {
    setUploadStatus(`✕ ${err.message}`, "error");
  }
}

function setUploadStatus(msg, cls) {
  uploadStatus.textContent = msg;
  uploadStatus.className = "upload-status" + (cls ? " " + cls : "");
}

// ---- risk scan ----
runScanBtn.addEventListener("click", async () => {
  if (!currentDocumentId) return;
  runScanBtn.disabled = true;
  scanResults.innerHTML = `<p class="spinner-text">Running self-healing scan across all clause categories — this checks its own grounding before showing you anything…</p>`;

  try {
    const res = await fetch("/api/risk-scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: currentDocumentId, doc_type: currentDocType }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Scan failed");

    scanResults.innerHTML = "";
    data.results.forEach((r, i) => renderClauseCard(r, i));
  } catch (err) {
    scanResults.innerHTML = `<p class="upload-status error">${err.message}</p>`;
  } finally {
    runScanBtn.disabled = false;
  }
});

function renderClauseCard(result, index) {
  const template = document.getElementById("clause-card-template");
  const node = template.content.cloneNode(true);

  node.querySelector(".clause-label").textContent = result.label;
  node.querySelector(".clause-why").textContent = result.why_it_matters;
  node.querySelector(".clause-answer").textContent = result.answer;

  const pill = node.querySelector(".severity-pill");
  pill.textContent = result.severity;
  pill.classList.add(result.severity);

  const meta = node.querySelector(".clause-meta");
  meta.textContent = `status: ${result.status} · retries used: ${result.retries_used}`;

  const stamp = node.querySelector(".stamp");
  if (result.status === "GAVE_UP") {
    stamp.textContent = "Needs Review";
    stamp.classList.add("review");
  } else if (result.severity === "red") {
    stamp.textContent = "Flagged";
    stamp.classList.add("flagged");
  } else {
    stamp.textContent = "Verified";
    stamp.classList.add("verified");
  }

  scanResults.appendChild(node);

  // stagger the stamp animation per card for a "notary" feel
  const stampEl = scanResults.children[scanResults.children.length - 1].querySelector(".stamp");
  setTimeout(() => stampEl.classList.add("animate"), 200 + index * 150);
}

// ---- chat ----
chatSendBtn.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", (e) => { if (e.key === "Enter") sendChat(); });

async function sendChat() {
  const question = chatInput.value.trim();
  if (!question || !currentDocumentId) return;

  appendBubble(question, "user");
  chatInput.value = "";
  const thinkingBubble = appendBubble("Retrieving and checking groundedness…", "assistant thinking");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: currentDocumentId, question }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Chat failed");

    thinkingBubble.querySelector(".text").textContent = data.answer;
    thinkingBubble.querySelector(".meta").textContent =
      `status: ${data.status} · retries used: ${data.retries_used}`;
  } catch (err) {
    thinkingBubble.querySelector(".text").textContent = `Error: ${err.message}`;
  }
}

function appendBubble(text, cls) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${cls}`;
  bubble.innerHTML = `<div class="text"></div><div class="meta"></div>`;
  bubble.querySelector(".text").textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}