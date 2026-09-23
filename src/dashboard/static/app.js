const form = document.querySelector("#settings-form");
const guildId = document.querySelector("#guild-id");
const status = document.querySelector("#status");
const card = document.querySelector("#card");
const previewTitle = document.querySelector("#preview-title");
const previewMessage = document.querySelector("#preview-message");
const avatar = document.querySelector("#avatar");
const memberCount = document.querySelector("#member-count");

function payload() {
  const data = new FormData(form);
  const channel = data.get("channel_id").trim();
  const background = data.get("background_url").trim();
  return { enabled: data.has("enabled"), channel_id: channel || null, title: data.get("title"), message: data.get("message"), extra_message: data.get("extra_message"), background_url: background || null, accent_color: data.get("accent_color"), text_color: data.get("text_color"), show_avatar: data.has("show_avatar"), show_member_count: data.has("show_member_count") };
}
function fill(data) { for (const [key, value] of Object.entries(data)) { const field = form.elements[key]; if (!field) continue; field.type === "checkbox" ? field.checked = value : field.value = value ?? ""; } preview(); }
function preview() { const data = payload(); card.style.color = data.text_color; card.style.backgroundColor = data.accent_color; card.style.backgroundImage = data.background_url ? `linear-gradient(rgb(0 0 0 / .35), rgb(0 0 0 / .35)), url("${data.background_url}")` : `linear-gradient(120deg, ${data.accent_color}, #252b55)`; previewTitle.textContent = data.title.replace("{user}", "Miki fan"); previewMessage.textContent = data.message; avatar.hidden = !data.show_avatar; memberCount.hidden = !data.show_member_count; }
async function load() { if (!/^\d+$/.test(guildId.value)) { status.textContent = "Enter a valid numeric server ID."; return; } status.textContent = "Loading…"; const response = await fetch(`/api/guilds/${guildId.value}/welcome-card`); if (!response.ok) { status.textContent = await response.text(); return; } fill(await response.json()); status.textContent = "Settings loaded."; }
document.querySelector("#load").addEventListener("click", load);
document.querySelector("#send-test").addEventListener("click", async () => { if (!/^\d+$/.test(guildId.value)) { status.textContent = "Load a valid server first."; return; } status.textContent = "Sending test card…"; const response = await fetch(`/api/guilds/${guildId.value}/welcome-card/test`, { method: "POST" }); status.textContent = response.ok ? "Test card sent. Check Discord and Miki's logs." : await response.text(); });
form.addEventListener("input", preview);
form.addEventListener("submit", async (event) => { event.preventDefault(); if (!/^\d+$/.test(guildId.value)) { status.textContent = "Load a valid server first."; return; } status.textContent = "Saving…"; const response = await fetch(`/api/guilds/${guildId.value}/welcome-card`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload()) }); status.textContent = response.ok ? "Saved to PostgreSQL." : await response.text(); if (response.ok) fill(await response.json()); });
fill({ enabled: false, channel_id: null, title: "Welcome, {user}!", message: "We are happy to have you here.", background_url: null, accent_color: "#8B5CF6", text_color: "#FFFFFF", show_avatar: true, show_member_count: true });
