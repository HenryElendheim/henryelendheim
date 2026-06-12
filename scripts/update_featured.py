"""Rebuilds the "Featured projects" table in README.md from repos tagged
with the "featured" topic. Run by .github/workflows/update-featured.yml."""

import json
import os
import re
import urllib.request

USER = "HenryElendheim"

# Fallback texts for repos that have no description set on GitHub.
FALLBACK_DESCRIPTIONS = {
    "SurvivalGame": "A survival game built in JavaScript",
    "ParaDies": "A JavaScript game project",
    "VareHusAdministrasjon": "Warehouse administration system in C#",
    "BibliotekApp": "Library management app in C#",
}


def main():
    headers = {"User-Agent": USER, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?per_page=100", headers=headers
    )
    with urllib.request.urlopen(request) as response:
        repos = json.load(response)

    featured = [r for r in repos if "featured" in (r.get("topics") or [])]
    featured.sort(key=lambda r: r["pushed_at"], reverse=True)

    if not featured:
        print("No repos with the 'featured' topic found - leaving README unchanged.")
        return

    rows = []
    for repo in featured:
        description = (
            repo.get("description")
            or FALLBACK_DESCRIPTIONS.get(repo["name"])
            or (f"A {repo['language']} project" if repo.get("language") else "")
        )
        rows.append(f"| [{repo['name']}]({repo['html_url']}) | {description} |")

    table = "\n".join(["| Project | What it is |", "|---|---|"] + rows)

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    updated = re.sub(
        r"(<!-- FEATURED:START -->)[\s\S]*?(<!-- FEATURED:END -->)",
        lambda match: f"{match.group(1)}\n{table}\n{match.group(2)}",
        readme,
    )

    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)
    print(f"Wrote {len(featured)} featured project(s) to README.md.")


if __name__ == "__main__":
    main()
