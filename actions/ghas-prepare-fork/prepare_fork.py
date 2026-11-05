"""GHAS administration logic; never checkout or execute target repository code."""

import html
import os
import re
import sys
from urllib.parse import quote

from prepare_files import ApiError, GitHub, prepare, summary


def validate_options(target, library, library_sha, enable_security, configure_variables, files_mode):
    name = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
    if not re.fullmatch(name, target) or not re.fullmatch(name, library):
        raise ValueError("Use OWNER/REPO for target and library.")
    if target.lower() == library.lower() or target.split("/")[0].lower() != library.split("/")[0].lower():
        raise ValueError("The target must be another repository in the library organization.")
    if enable_security not in {"true", "false"} or configure_variables not in {"true", "false"}:
        raise ValueError("Boolean action inputs must be true or false.")
    if files_mode not in {"none", "preview", "install"}:
        raise ValueError("files-mode must be none, preview or install.")
    if files_mode != "none" and not re.fullmatch(r"[a-fA-F0-9]{40}", library_sha):
        raise ValueError("Preview/install requires a published full library commit SHA.")


def verified_fork(api, target):
    repo = api.request("GET", "/repos/" + target)
    if (repo.get("full_name", "").lower() != target.lower()
            or not repo.get("fork") or not repo.get("parent")
            or repo.get("archived") or repo.get("disabled")):
        raise ValueError("Target is not the requested active GitHub fork. No further requests made.")
    return repo


def state(repo, key):
    security = repo.get("security_and_analysis") or {}
    if key == "code_security":
        return (security.get(key, {}).get("status")
                or security.get("advanced_security", {}).get("status") or "not reported")
    return security.get(key, {}).get("status") or "not reported"


def table(heading, headers, rows):
    def cell(value):
        return html.escape(str(value)).replace("|", "\\|").replace("\n", " ")
    return "\n".join(["## " + heading, "", "| " + " | ".join(map(cell, headers)) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |",
                      *["| " + " | ".join(map(cell, row)) + " |" for row in rows], ""])


def enable_features(api, target, report):
    before = verified_fork(api, target)
    features = [("code_security", "Code Security"), ("secret_scanning", "Secret scanning"),
                ("secret_scanning_push_protection", "Push protection")]
    attempts = {}
    for key, _ in features:
        if state(before, key) == "enabled":
            attempts[key] = "already enabled"
            continue
        try:
            api.request("PATCH", "/repos/" + target,
                        {"security_and_analysis": {key: {"status": "enabled"}}})
            attempts[key] = "request accepted"
        except ApiError as error:
            attempts[key] = str(error)[:1500]
    after = verified_fork(api, target)
    report(table("GHAS activation", ["Feature", "Before", "Request", "After"],
                 [(label, state(before, key), attempts[key], state(after, key)) for key, label in features]))
    report("Only the target fork was requested. Partial activation is not rolled back.\n")
    if any(state(after, key) != "enabled" for key, _ in features):
        raise ValueError("Security enablement incomplete. Check App permissions, enterprise policy and licenses. "
                         "Variables and file preparation were not attempted after this failure.")
    return after


def configure_variables(api, target, report):
    repo = verified_fork(api, target)
    code_ready = repo.get("visibility") == "public" or state(repo, "code_security") == "enabled"
    review_ready = False
    review_check = "not checked: Code Security not confirmed"
    base = "/repos/" + target
    if code_ready:
        try:
            branch = api.request("GET", base + "/branches/" + quote(repo["default_branch"], safe=""))
            sha = branch["commit"]["sha"]
            api.request("GET", base + "/dependency-graph/compare/" + sha + "..." + sha)
            review_ready, review_check = True, "same-commit comparison accessible; not a detection test"
        except ApiError as error:
            review_check = f"not confirmed: HTTP {error.status}"
    rows, failed = [], False
    for name, value in [("CODEQL_ENABLED", str(code_ready).lower()),
                        ("DEPENDENCY_REVIEW_ENABLED", str(review_ready).lower())]:
        path = base + "/actions/variables/" + name
        try:
            try:
                old = api.request("GET", path)
            except ApiError as error:
                if error.status != 404:
                    raise
                old = None
            if old is None:
                api.request("POST", base + "/actions/variables", {"name": name, "value": value})
            elif old.get("value") != value:
                api.request("PATCH", path, {"name": name, "value": value})
            saved = api.request("GET", path)
            if saved.get("value") != value:
                raise ValueError("Variable read-back mismatch")
            rows.append((name, value, "verified"))
        except (ApiError, ValueError) as error:
            failed = True
            rows.append((name, value, str(error)[:1500]))
    report(table("GHAS fork variables", ["Variable", "Desired", "Result"], rows))
    report("Dependency Review: " + review_check + ". No dependency graph activation was requested.\n")
    if failed:
        raise ValueError("Some variables were not verified; partial configuration may remain.")


def execute(api, target, library, library_sha="", enable_security="false",
            configure="false", files_mode="none", report=print):
    validate_options(target, library, library_sha, enable_security, configure, files_mode)
    repo = verified_fork(api, target)
    report(table("GHAS fork inspection", ["Check", "Result"], [
        ("Target", repo["full_name"]), ("Repository ID", repo.get("id", "not reported")),
        ("Default branch", repo["default_branch"]), ("GitHub fork", "yes"),
        ("Visibility", repo.get("visibility", "not reported")),
        ("Code Security", state(repo, "code_security")),
        ("Secret scanning", state(repo, "secret_scanning")),
        ("Push protection", state(repo, "secret_scanning_push_protection")),
        ("Changes made by inspection", "none")]))
    report("Inspection proves access, not write permissions, licenses or successful scans.\n")
    if enable_security == "true":
        enable_features(api, target, report)
    if configure == "true":
        configure_variables(api, target, report)
    result = {"repository-id": str(repo.get("id", "")), "proposal-branch": "", "compare-url": ""}
    if files_mode != "none":
        plan = prepare(api, target, library, library_sha, files_mode)
        report(summary(plan))
        result.update({"proposal-branch": plan.get("proposal_branch", ""),
                       "compare-url": plan.get("compare_url", "")})
    return result


def main():
    def report(message):
        print(message)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
                output.write(message + "\n")
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        raise ValueError("github-token is required")
    result = execute(GitHub(token, os.environ.get("GITHUB_API_URL", "https://api.github.com")),
                     os.environ.get("GHAS_TARGET", ""), os.environ.get("GHAS_LIBRARY", ""),
                     os.environ.get("GHAS_LIBRARY_SHA", ""), os.environ.get("GHAS_ENABLE_SECURITY", "false"),
                     os.environ.get("GHAS_CONFIGURE_VARIABLES", "false"),
                     os.environ.get("GHAS_FILES_MODE", "none"), report)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            for name, value in result.items():
                output.write(f"{name}={value}\n")


if __name__ == "__main__":
    try:
        main()
    except (ApiError, ValueError) as error:
        print("GHAS preparation failed: " + " ".join(str(error).split()), file=sys.stderr)
        sys.exit(1)
