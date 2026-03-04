async function main() {
  const el = document.getElementById("status");
  const res = await fetch("/api/health");
  const data = await res.json();
  el.textContent = "API: " + data.status;
}
main().catch(err => {
  document.getElementById("status").textContent = "Error: " + err;
});
