const body = document.body, menu = document.querySelector(".menu-toggle");
menu.addEventListener("click", () => {
  const open = body.classList.toggle("toc-open");
  menu.setAttribute("aria-expanded", String(open));
});
document.querySelectorAll(".toc a").forEach((a) => a.addEventListener("click", () => {
  body.classList.remove("toc-open");
  menu.setAttribute("aria-expanded", "false");
}));
document.querySelector(".theme-toggle").addEventListener("click", () => {
  const root = document.documentElement;
  const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  root.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("guide-theme", root.dataset.theme); } catch {}
});
const links = new Map([...document.querySelectorAll(".toc a")].map((a) => [a.hash.slice(1), a]));
const seen = new Set();
const observer = new IntersectionObserver((entries) => {
  for (const e of entries) e.isIntersecting ? seen.add(e.target.id) : seen.delete(e.target.id);
  const current = [...links.keys()].find((id) => seen.has(id));
  if (current) links.forEach((a, id) => a.classList.toggle("active", id === current));
}, { rootMargin: "-64px 0px -60% 0px" });
links.forEach((_, id) => { const s = document.getElementById(id); if (s) observer.observe(s); });
