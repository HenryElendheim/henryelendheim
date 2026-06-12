// Rebuilds the "Featured projects" table in README.md from repos tagged
// with the "featured" topic. Run by .github/workflows/update-featured.yml.
const fs = require("fs");

const USER = "HenryElendheim";

// Fallback texts for repos that have no description set on GitHub.
const FALLBACK_DESCRIPTIONS = {
  SurvivalGame: "A survival game built in JavaScript",
  ParaDies: "A JavaScript game project",
  VareHusAdministrasjon: "Warehouse administration system in C#",
  BibliotekApp: "Library management app in C#",
};

async function main() {
  const headers = { "User-Agent": USER, Accept: "application/vnd.github+json" };
  if (process.env.GITHUB_TOKEN) {
    headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }

  const res = await fetch(`https://api.github.com/users/${USER}/repos?per_page=100`, { headers });
  if (!res.ok) throw new Error(`GitHub API returned ${res.status}`);
  const repos = await res.json();

  const featured = repos
    .filter((r) => (r.topics || []).includes("featured"))
    .sort((a, b) => new Date(b.pushed_at) - new Date(a.pushed_at));

  if (featured.length === 0) {
    console.log("No repos with the 'featured' topic found - leaving README unchanged.");
    return;
  }

  const rows = featured.map((r) => {
    const description =
      r.description ||
      FALLBACK_DESCRIPTIONS[r.name] ||
      (r.language ? `A ${r.language} project` : "");
    return `| [${r.name}](${r.html_url}) | ${description} |`;
  });

  const table = ["| Project | What it is |", "|---|---|", ...rows].join("\n");

  const readme = fs.readFileSync("README.md", "utf8");
  const updated = readme.replace(
    /(<!-- FEATURED:START -->)[\s\S]*?(<!-- FEATURED:END -->)/,
    `$1\n${table}\n$2`
  );

  fs.writeFileSync("README.md", updated);
  console.log(`Wrote ${featured.length} featured project(s) to README.md.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
