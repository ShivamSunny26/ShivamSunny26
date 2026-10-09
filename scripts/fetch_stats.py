#!/usr/bin/env python3
"""Fetch live GitHub stats for the profile dashboard and write data/stats.json.

Needs env var GH_TOKEN (GITHUB_TOKEN works for public data; a personal access
token with `read:user` + `repo` also counts private activity).
Standard library only.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
USER = os.environ.get("GH_USER") or CFG["github_username"]
TOKEN = os.environ.get("GH_TOKEN")
API = "https://api.github.com/graphql"

if not TOKEN:
    sys.exit("GH_TOKEN is not set.")

PRIV = "" if CFG.get("include_private") else ", privacy: PUBLIC"

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

PROFILE_Q = """
query($login: String!, $from3: DateTime!, $from12: DateTime!, $to: DateTime!) {
  user(login: $login) {
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false__PRIV__) { totalCount }
    three: contributionsCollection(from: $from3, to: $to) {
      totalCommitContributions
    }
    year: contributionsCollection(from: $from12, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
""".replace("__PRIV__", PRIV)

LANG_Q = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 50, after: $cursor, ownerAffiliations: OWNER, isFork: false__PRIV__) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
""".replace("__PRIV__", PRIV)


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-dashboard",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API error {e.code}: {e.read().decode()[:300]}")
    if data.get("errors"):
        sys.exit(f"GraphQL errors: {data['errors']}")
    return data["data"]


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def streaks(days):
    """days: list of (date, count) sorted ascending."""
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    current = 0
    seq = list(reversed(days))
    if seq and seq[0][1] == 0:      # today may not have a contribution yet
        seq = seq[1:]
    for _, c in seq:
        if c > 0:
            current += 1
        else:
            break
    return current, longest


def main():
    now = dt.datetime.now(dt.timezone.utc)
    variables = {
        "login": USER,
        "from3": iso(now - dt.timedelta(days=90)),
        "from12": iso(now - dt.timedelta(days=364)),
        "to": iso(now),
    }
    u = gql(PROFILE_Q, variables)["user"]
    cal = u["year"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    days = [(d["date"], d["contributionCount"]) for w in weeks for d in w]
    days.sort()
    current, longest = streaks(days)
    heatmap = [[LEVELS.get(d["contributionLevel"], 0) for d in w] for w in weeks[-20:]]

    # ---- languages (bytes of code across your own, non-fork repos) ----
    totals, colors = {}, {}
    excl_repos = set(CFG.get("exclude_repos", []))
    excl_langs = set(CFG.get("exclude_languages", []))
    cursor = None
    while True:
        repos = gql(LANG_Q, {"login": USER, "cursor": cursor})["user"]["repositories"]
        for repo in repos["nodes"]:
            if repo["name"] in excl_repos:
                continue
            for e in repo["languages"]["edges"]:
                name = e["node"]["name"]
                if name in excl_langs:
                    continue
                totals[name] = totals.get(name, 0) + e["size"]
                colors.setdefault(name, e["node"]["color"] or "#8b949e")
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]

    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    langs = [{"name": n, "percent": round(s / grand * 100, 1), "color": colors[n]}
             for n, s in ranked[:5]]
    others = round(100 - sum(l["percent"] for l in langs), 1)
    if ranked[5:] and others > 0:
        langs.append({"name": "Others", "percent": others, "color": "#6e7681"})

    stats = {
        "username": USER,
        "updated": now.strftime("%Y-%m-%d"),
        "repositories": u["repositories"]["totalCount"],
        "commits_3mo": u["three"]["totalCommitContributions"],
        "issues": u["issues"]["totalCount"],
        "contributions_1y": cal["totalContributions"],
        "current_streak": current,
        "longest_streak": longest,
        "languages": langs,
        "heatmap": heatmap,
    }
    out = ROOT / "data" / "stats.json"
    out.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "heatmap"}, indent=2))


if __name__ == "__main__":
    main()
