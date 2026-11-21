// Checks the static guide: every local href/src exists, every #anchor has a
// matching id, and every <img> has alt text and size. Usage: node tools/check_site.mjs site
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
const root = process.argv[2] || "site";
const errors = [];
for (const file of readdirSync(root).filter((f) => f.endsWith(".html"))) {
  const html = readFileSync(join(root, file), "utf8");
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  for (const [, attr, value] of html.matchAll(/\s(href|src)="([^"]+)"/g)) {
    if (/^(https?:|mailto:)/.test(value)) continue;
    if (value.startsWith("#")) { if (value.length > 1 && !ids.has(value.slice(1))) errors.push(`${file}: missing anchor ${value}`); continue; }
    if (!existsSync(join(root, value.split("#")[0]))) errors.push(`${file}: missing ${attr} ${value}`);
  }
  for (const [tag] of html.matchAll(/<img\b[^>]*>/g))
    if (!/\salt="[^"]+"/.test(tag) || !/\swidth="\d+"/.test(tag) || !/\sheight="\d+"/.test(tag)) errors.push(`${file}: img needs alt/width/height: ${tag.slice(0, 80)}`);
}
if (errors.length) { console.error(errors.join("\n")); process.exit(1); }
console.log("Guide site: links, anchors and images OK");
