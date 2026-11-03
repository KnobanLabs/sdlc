#!/usr/bin/env python3
# Copyright 2026 Knoban LLC
# SPDX-License-Identifier: MIT
# (https://github.com/KnobanLabs/sdlc)

"""Keep Claude Code's auto mode settings in step with the SDLC plugin.

The plugin README's Auto mode section explains the recommended settings. This
script merges them into a Claude Code user settings file and keeps two
environment entries current: the owned GitHub accounts (your gh login plus the
`owned` lists in ~/.sdlc/settings.json) and their public repositories, whose
visibility it reads from GitHub. To add an organization, list it in
~/.sdlc/settings.json, then run `sync --write`.

  automode-settings.py list               # owned accounts, and which entries are in place
  automode-settings.py merge [--write]    # add or update every recommended entry
  automode-settings.py sync [--write]     # rewrite only the two owned-account entries

Without --write it prints what would change. With --write it first saves a
dated backup beside the settings file. It changes only the entries it owns,
matched by their names, and leaves every other key and entry as it is.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECOMMENDED = ROOT / "plugins" / "sdlc" / "claude-settings.recommended.json"
SDLC_SETTINGS = pathlib.Path.home() / ".sdlc" / "settings.json"
ACCOUNTS = "**Owned GitHub accounts**"
PUBLIC = "**Public repositories of owned accounts**"
LISTS = ("environment", "allow", "soft_deny", "hard_deny")


def gh(*args, host="github.com"):
    env = dict(os.environ, GH_HOST=host)
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, env=env).stdout.strip()


def name(entry):
    """What identifies an entry across releases: its bold title, or the text before its first bracket or colon."""
    m = re.match(r"\*\*(.+?)\*\*|([^\[(:]+)", entry)
    return (m.group(1) or m.group(2)).strip()


def owned():
    """Your github.com login, then the accounts and repositories ~/.sdlc/settings.json lists, as (name, host)."""
    lists = json.loads(SDLC_SETTINGS.read_text()).get("owned", {}) if SDLC_SETTINGS.exists() else {}
    pick = lambda key: [(e["name"], e["host"]) for e in lists.get(key, [])]
    me = gh("api", "user", "--jq", ".login")
    accounts = [(me, "github.com")] + [a for a in pick("users") + pick("organizations") if a != (me, "github.com")]
    return me, accounts, pick("repositories")


def label(name_, host):
    return name_ if host == "github.com" else f"{name_} (on {host})"


def public_repos(accounts, repos):
    found = set()
    for a, host in accounts:
        listed = json.loads(gh("repo", "list", a, "--limit", "1000", "--json", "nameWithOwner,visibility", host=host))
        found.update(label(r["nameWithOwner"], host) for r in listed if r["visibility"] == "PUBLIC")
    for r, host in repos:
        if gh("repo", "view", r, "--json", "visibility", "--jq", ".visibility", host=host) == "PUBLIC":
            found.add(label(r, host))
    return sorted(found, key=str.lower)


def owned_entries():
    me, accounts, repos = owned()
    scope = ", ".join(label(*a) for a in accounts) + f" (every repository of each; {me} is the user's own login)"
    if repos:
        scope += "; and the repositories " + ", ".join(label(*r) for r in repos)
    pubs = public_repos(accounts, repos)
    return [
        f"{ACCOUNTS} (overrides the default Organization and Source control entries; from the SDLC plugin's "
        f"~/.sdlc/settings.json, as of the last sync; this list, not that file's current contents, is what counts): "
        f"{scope}. Every repository these name is the user's own and inside the trust boundary for source control, "
        "so copying between them is not Data Exfiltration; content from a private one reaching a public one is "
        "still Out-of-Place Publication.",
        f"{PUBLIC} (treat these as `visibility: public` even when no meta line appears; the other repositories "
        "of the owned accounts were private when this list was made, and a visibility meta line showing public "
        "or unverified overrides that): " + (", ".join(pubs) or "none") + ". They remain publication "
        "destinations: content from a private repository pushed, posted or copied to one of them is "
        "Out-of-Place Publication.",
    ]


def upsert(current, wanted):
    """`current` with each wanted entry replacing the one of the same name, or appended, and "$defaults" kept."""
    out = list(current)
    if "$defaults" not in out:
        out.insert(0, "$defaults")
    for w in wanted:
        same = [i for i, e in enumerate(out) if e != "$defaults" and name(e) == name(w)]
        if same:
            out[same[0]] = w
            out = [e for i, e in enumerate(out) if i not in same[1:]]
        else:
            out.append(w)
    return out


def planned(settings, action):
    """The settings after the action, built on a copy."""
    new = json.loads(json.dumps(settings))
    auto = new.setdefault("autoMode", {})
    if action == "merge":
        rec = json.loads(RECOMMENDED.read_text())
        for key in LISTS:
            entries = [e for e in rec["autoMode"].get(key, []) if e != "$defaults"]
            if entries:
                auto[key] = upsert(auto.get(key, []), entries)
        perms = new.setdefault("permissions", {})
        for key, values in rec["permissions"].items():
            have = perms.setdefault(key, [])
            if key == "additionalDirectories":
                values = [os.path.expanduser(v) for v in values]
            have += [v for v in values if v not in have]
    auto["environment"] = upsert(auto.get("environment", []), owned_entries())
    return new


def show(old, new, path=""):
    """Print each added (+) and removed (-) entry, by key path."""
    if isinstance(old, dict) and isinstance(new, dict):
        for k in dict.fromkeys([*old, *new]):
            show(old.get(k, []), new.get(k, []), f"{path}.{k}" if path else k)
    elif old != new:
        for e in new if isinstance(new, list) else [new]:
            if e not in (old if isinstance(old, list) else [old]):
                print(f"+ {path}: {e}")
        for e in old if isinstance(old, list) else [old]:
            if e not in (new if isinstance(new, list) else [new]):
                print(f"- {path}: {e}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["list", "merge", "sync"])
    ap.add_argument("--write", action="store_true", help="save the change (a backup is kept)")
    ap.add_argument("--file", default=str(pathlib.Path.home() / ".claude" / "settings.json"),
                    help="the Claude Code settings file (default: ~/.claude/settings.json)")
    a = ap.parse_args()

    path = pathlib.Path(a.file)
    settings = json.loads(path.read_text()) if path.exists() else {}

    if a.action == "list":
        me, accounts, repos = owned()
        print("Owned accounts:    ", ", ".join(label(*x) for x in accounts))
        print("Owned repositories:", ", ".join(label(*x) for x in repos) or "(none)")
        rec = json.loads(RECOMMENDED.read_text())["autoMode"]
        auto = settings.get("autoMode", {})
        for key in LISTS:
            for e in rec.get(key, []):
                if e == "$defaults":
                    continue
                have = next((x for x in auto.get(key, []) if name(x) == name(e)), None)
                print(f"{key}: {name(e)}: {'current' if have == e else 'outdated' if have else 'missing'}")
        for key in LISTS:
            if key in auto and "$defaults" not in auto[key]:
                print(f'{key}: no "$defaults", so the built-in {key} rules are dropped')
        return

    new = planned(settings, a.action)
    if new == settings:
        print("No change.")
        return
    show(settings, new)
    if not a.write:
        print("\n(dry run; add --write to save)")
        return
    if path.exists():
        backup = path.with_name(f"{path.name}.{time.strftime('%Y%m%d%H%M%S')}.bak")
        shutil.copy2(path, backup)
        print(f"Backup: {backup}")
    path.write_text(json.dumps(new, indent=2) + "\n")
    print(f"Saved {path}.")


if __name__ == "__main__":
    main()
