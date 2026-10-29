"""Inspect a fork and propose GHAS files without executing its contents."""

import argparse
import hashlib
import html
import json
import os
from pathlib import PurePosixPath
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


WORKFLOW = ".github/workflows/ghas-security.yml"
DEPENDABOT = ".github/dependabot.yml"
IGNORED = {"node_modules", "vendor", ".venv", "venv", "dist", "build"}
INTERPRETED = {
    ".py": "python", ".rb": "ruby", ".js": "javascript-typescript",
    ".jsx": "javascript-typescript", ".ts": "javascript-typescript",
    ".tsx": "javascript-typescript", ".mjs": "javascript-typescript",
    ".cjs": "javascript-typescript", ".mts": "javascript-typescript", ".cts": "javascript-typescript",
}
BUILD_PROFILES = {
    ".c": "c-cpp", ".h": "c-cpp", ".cc": "c-cpp", ".cpp": "c-cpp", ".hpp": "c-cpp",
    ".cs": "csharp", ".go": "go", ".java": "java-kotlin", ".kt": "java-kotlin",
    ".swift": "swift", ".rs": "rust",
}
MANIFESTS = {
    "package.json": "npm", "requirements.txt": "pip", "Pipfile": "pip",
    "pyproject.toml": "pip", "setup.py": "pip", "setup.cfg": "pip", "Gemfile": "bundler",
    "go.mod": "gomod", "pom.xml": "maven", "build.gradle": "gradle",
    "build.gradle.kts": "gradle", "Cargo.toml": "cargo", "composer.json": "composer",
    "packages.config": "nuget",
}


class ApiError(RuntimeError):
    def __init__(self, status, message):
        self.status = status
        super().__init__(f"HTTP {status}: {message}")


class GitHub:
    def __init__(self, token, url="https://api.github.com"):
        self.token, self.url = token, url.rstrip("/")

    def request(self, method, path, data=None):
        request = urllib.request.Request(
            self.url + path, method=method,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": "Bearer " + self.token,
                     "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                     "X-GitHub-Api-Version": "2022-11-28"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            try:
                message = json.loads(error.read()).get("message", "GitHub request failed")
            except (ValueError, AttributeError):
                message = "GitHub request failed"
            raise ApiError(error.code, message) from None


def inventory(paths):
    # The installed caller is itself an Actions workflow, even in a code-free repo.
    languages, profiles, updates = {"actions"}, set(), {("github-actions", "/")}
    for path in paths:
        file = PurePosixPath(path)
        if any(part in IGNORED for part in file.parts):
            continue
        if file.suffix in INTERPRETED:
            languages.add(INTERPRETED[file.suffix])
        if file.suffix in BUILD_PROFILES:
            profiles.add(BUILD_PROFILES[file.suffix])
        ecosystem = MANIFESTS.get(file.name)
        if file.suffix == ".tf":
            ecosystem = "terraform"
        elif file.suffix in {".csproj", ".fsproj", ".vbproj"}:
            ecosystem = "nuget"
        if ecosystem:
            directory = "/" if str(file.parent) == "." else "/" + str(file.parent)
            updates.add((ecosystem, directory))
    if len(updates) > 100:
        raise ValueError("More than 100 dependency directories: a reviewed monorepo profile is required.")
    return {
        "languages": sorted(languages), "profiles_required": sorted(profiles),
        "updates": [{"package-ecosystem": ecosystem, "directory": directory,
                     "schedule": {"interval": "weekly"}, "open-pull-requests-limit": 5}
                    for ecosystem, directory in sorted(updates)],
    }


def render(info, default_branch, library, library_sha):
    workflow = {
        "name": "GHAS - Security checks",
        "on": {"pull_request": {}, "push": {"branches": [default_branch]},
               "schedule": [{"cron": "34 6 * * 1"}], "workflow_dispatch": {}},
        "permissions": {"contents": "read"},
        "concurrency": {"group": "ghas-${{ github.workflow }}-${{ github.ref }}", "cancel-in-progress": True},
        "jobs": {
            "codeql": {
                "if": "${{ vars.CODEQL_ENABLED == 'true' }}",
                "permissions": {"actions": "read", "contents": "read", "security-events": "write"},
                "uses": f"{library}/.github/workflows/ghas-codeql.yml@{library_sha}",
                "with": {"languages": json.dumps(info["languages"])},
            },
            "dependency-review": {
                "if": "${{ github.event_name == 'pull_request' && vars.DEPENDENCY_REVIEW_ENABLED == 'true' }}",
                "uses": f"{library}/.github/workflows/ghas-dependency-review.yml@{library_sha}",
                "with": {"fail-on-severity": "low"},
            },
        },
    }
    # JSON is a YAML subset; use the standard serializer rather than a custom YAML emitter.
    return {WORKFLOW: json.dumps(workflow, indent=2) + "\n",
            DEPENDABOT: json.dumps({"version": 2, "updates": info["updates"]}, indent=2) + "\n"}


def blob_sha(content):
    data = content.encode()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def prepare(api, target, library, library_sha, mode="preview"):
    if mode not in {"preview", "install"}:
        raise ValueError("Mode must be preview or install.")
    pattern = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
    if not re.fullmatch(pattern, target) or not re.fullmatch(pattern, library):
        raise ValueError("Repository names must use OWNER/REPO.")
    if target.lower() == library.lower() or target.split("/")[0].lower() != library.split("/")[0].lower():
        raise ValueError("Target must be another repository in the library organization.")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", library_sha):
        raise ValueError("A full library commit SHA is required.")
    base = f"/repos/{target}"
    repo = api.request("GET", base)
    if repo.get("full_name", "").lower() != target.lower():
        raise ValueError("GitHub resolved another repository name; review the target before retrying.")
    if not repo.get("fork") or not repo.get("parent") or repo.get("archived") or repo.get("disabled"):
        raise ValueError("Target must be an active GitHub fork; no files were changed.")
    default = repo["default_branch"]
    ref = api.request("GET", base + "/git/ref/heads/" + urllib.parse.quote(default, safe=""))
    commit_sha = ref["object"]["sha"]
    commit = api.request("GET", base + "/git/commits/" + commit_sha)
    tree = api.request("GET", base + "/git/trees/" + commit["tree"]["sha"] + "?recursive=1")
    if tree.get("truncated"):
        raise ValueError("Truncated Git tree: refusing an incomplete inventory.")
    blobs = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}
    info = inventory(blobs)
    proposed = render(info, default, library, library_sha)
    warnings = []
    if info["profiles_required"]:
        warnings.append("CodeQL profiles not automated in this version: " + ", ".join(info["profiles_required"]))
    if DEPENDABOT in blobs or ".github/dependabot.yaml" in blobs:
        del proposed[DEPENDABOT]
        warnings.append("Existing Dependabot configuration preserved; review its coverage separately.")
    legacy = [path for path in blobs if path.startswith(".github/workflows/") and path != WORKFLOW
              and ("codeql" in PurePosixPath(path).name.lower()
                   or "dependency-review" in PurePosixPath(path).name.lower())]
    if legacy:
        warnings.append("Other security workflows may duplicate the generated checks; review them in the fork.")
    for path in proposed:
        if path in blobs and blobs[path].get("mode") != "100644":
            raise ValueError("A managed output path is not a regular file; review it manually.")
    changes = {path: content for path, content in proposed.items()
               if path not in blobs or blobs[path]["sha"] != blob_sha(content)}
    plan = {"mode": mode, "repository": target, "base_branch": default,
            "base_commit": commit_sha, "library_commit": library_sha,
            "inventory": info, "warnings": warnings, "files": proposed,
            "changed_files": sorted(changes), "installation": "preview only"}
    if mode == "preview" or not changes:
        if mode == "install":
            plan["installation"] = "already configured on default branch"
        return plan

    # Stage all files in one Git tree/commit; never update the default branch.
    branch = f"ghas/setup-{commit_sha[:12]}-{library_sha[:12]}"
    new_tree = api.request("POST", base + "/git/trees", {
        "base_tree": commit["tree"]["sha"],
        "tree": [{"path": path, "mode": "100644", "type": "blob", "content": content}
                 for path, content in changes.items()],
    })
    try:
        existing = api.request("GET", base + "/git/ref/heads/" + branch)
    except ApiError as error:
        if error.status != 404:
            raise
        existing = None
    if existing:
        existing_commit = api.request("GET", base + "/git/commits/" + existing["object"]["sha"])
        if existing_commit["tree"]["sha"] != new_tree["sha"]:
            raise ValueError("Proposal branch already has different changes; refusing to overwrite it.")
        plan["installation"] = "existing proposal reused"
        plan["proposal_commit"] = existing["object"]["sha"]
    else:
        proposal = api.request("POST", base + "/git/commits", {
            "message": f"Configure GHAS testing from {library}@{library_sha}",
            "tree": new_tree["sha"], "parents": [commit_sha],
        })
        api.request("POST", base + "/git/refs", {"ref": "refs/heads/" + branch, "sha": proposal["sha"]})
        plan["installation"] = "proposal branch created"
        plan["proposal_commit"] = proposal["sha"]
    plan["proposal_branch"] = branch
    plan["compare_url"] = (repo["html_url"] + "/compare/" + urllib.parse.quote(default, safe="")
                           + "..." + urllib.parse.quote(branch, safe=""))
    return plan


def summary(plan):
    def cell(value):
        return html.escape(str(value)).replace("|", "\\|").replace("\n", " ")

    counts = {}
    for update in plan["inventory"]["updates"]:
        ecosystem = update["package-ecosystem"]
        counts[ecosystem] = counts.get(ecosystem, 0) + 1
    lines = ["## GHAS file preparation", "", "| Check | Result |", "| --- | --- |",
             f"| Mode | {cell(plan['mode'])} |",
             f"| CodeQL languages | {cell(', '.join(plan['inventory']['languages']))} |",
             f"| Installation | {cell(plan['installation'])} |",
             f"| Files to change | {cell(', '.join(plan['changed_files']) or 'none')} |",
             f"| Dependency ecosystems / directory counts | {cell(json.dumps(counts))} |"]
    if "compare_url" in plan:
        lines.extend(["", f"[Review proposal in the fork]({plan['compare_url']})"])
    lines.extend(["", *["- " + cell(warning) for warning in plan["warnings"]], "",
                  "No default-branch update, merge, scan dispatch, deployment or security activation was requested by this job.",
                  "Disable inherited deployment workflows in the fork before merging the proposal.",
                  "Manifest detection is not proof of vulnerability coverage; private registries and unsupported profiles need review.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--library", required=True)
    parser.add_argument("--library-sha", required=True)
    parser.add_argument("--mode", choices=["preview", "install"], default="preview")
    args = parser.parse_args()
    if not os.environ.get("GH_TOKEN"):
        parser.error("GH_TOKEN is required")
    api = GitHub(os.environ["GH_TOKEN"], os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    plan = prepare(api, args.target, args.library, args.library_sha, args.mode)
    report = summary(plan)
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(report)
    if os.environ.get("GHAS_PLAN_PATH"):
        with open(os.environ["GHAS_PLAN_PATH"], "w", encoding="utf-8") as output:
            json.dump(plan, output, indent=2)
            output.write("\n")


if __name__ == "__main__":
    try:
        main()
    except (ApiError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
