import copy
from contextlib import redirect_stdout
import io
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "actions/ghas-prepare-fork"))
import prepare_fork as kit


TARGET = "example/reusable-test"
LIBRARY = "example/scripts"
SHA = "b" * 40


class FakeGitHub:
    def __init__(self, *, enabled=False, denied=False, review=True, mismatch=False):
        self.repo = {"id": 123, "full_name": TARGET, "fork": True, "parent": {"id": 1},
                     "html_url": "https://github.com/" + TARGET,
                     "default_branch": "integration/test", "visibility": "private",
                     "security_and_analysis": {key: {"status": "enabled" if enabled else "disabled"}
                                               for key in ("code_security", "secret_scanning",
                                                           "secret_scanning_push_protection")}}
        self.calls, self.variables = [], {}
        self.denied, self.review, self.mismatch = denied, review, mismatch

    def request(self, method, path, data=None):
        self.calls.append((method, path, data))
        base = "/repos/" + TARGET
        if path == base:
            if method == "GET":
                return copy.deepcopy(self.repo)
            if method == "PATCH":
                if self.denied:
                    raise kit.ApiError(422, "Activation locked by billing")
                self.repo["security_and_analysis"].update(data["security_and_analysis"])
                return copy.deepcopy(self.repo)
        if method == "GET" and path == base + "/branches/integration%2Ftest":
            return {"commit": {"sha": "a" * 40}}
        if method == "GET" and "/dependency-graph/compare/" in path:
            if not self.review:
                raise kit.ApiError(403, "Not available")
            return {}
        if method == "GET" and path.endswith("/git/ref/heads/integration%2Ftest"):
            return {"object": {"sha": "a" * 40}}
        if method == "GET" and path.endswith("/git/commits/" + "a" * 40):
            return {"tree": {"sha": "base-tree"}}
        if method == "GET" and path.endswith("/git/trees/base-tree?recursive=1"):
            return {"tree": [], "truncated": False}
        if method == "GET" and "/git/ref/heads/feature/ghas-setup-" in path:
            raise kit.ApiError(404, "Not found")
        if method == "POST" and path.endswith("/git/trees"):
            return {"sha": "new-tree"}
        if method == "POST" and path.endswith("/git/commits"):
            return {"sha": "new-commit"}
        if method == "POST" and path.endswith("/git/refs"):
            return {"ref": data["ref"]}
        if path == base + "/actions/variables" and method == "POST":
            self.variables[data["name"]] = data["value"]
            return None
        if "/actions/variables/" in path:
            name = path.rsplit("/", 1)[-1]
            if method == "PATCH":
                self.variables[name] = data["value"]
                return None
            if method == "GET":
                if name not in self.variables:
                    raise kit.ApiError(404, "Not found")
                return {"value": "wrong" if self.mismatch else self.variables[name]}
        raise AssertionError((method, path, data))


class AdministrationTests(unittest.TestCase):
    def run_action(self, api, **options):
        return kit.execute(api, TARGET, LIBRARY, report=lambda _: None, **options)

    def test_default_inspection_only_reads_and_returns_repository_identity(self):
        api = FakeGitHub()
        result = self.run_action(api)
        self.assertEqual(result["repository-id"], "123")
        self.assertEqual(result["proposal-branch"], "")
        self.assertEqual([method for method, _, _ in api.calls], ["GET"])

    def test_invalid_options_fail_before_any_api_request(self):
        for options in [{"target": LIBRARY}, {"target": "another-org/fork"},
                        {"files_mode": "delete"}, {"files_mode": "preview", "library_sha": "main"},
                        {"enable_security": "yes"}, {"configure": "yes"}]:
            api = FakeGitHub()
            args = {"target": TARGET, "library": LIBRARY, "report": lambda _: None, **options}
            with self.subTest(options=options), self.assertRaises(ValueError):
                kit.execute(api, **args)
            self.assertEqual(api.calls, [])

    def test_source_archived_disabled_or_renamed_repository_is_rejected(self):
        for override in [{"fork": False}, {"archived": True}, {"disabled": True},
                         {"full_name": "example/renamed"}, {"parent": None}]:
            api = FakeGitHub()
            api.repo.update(override)
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.run_action(api, enable_security="true", configure="true")
            self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_explicit_enablement_is_verified(self):
        api = FakeGitHub()
        self.run_action(api, enable_security="true")
        self.assertEqual(sum(method == "PATCH" for method, _, _ in api.calls), 3)
        self.assertTrue(all(x["status"] == "enabled" for x in api.repo["security_and_analysis"].values()))

    def test_existing_enabled_features_are_not_patched(self):
        api = FakeGitHub(enabled=True)
        self.run_action(api, enable_security="true")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_activation_failure_preserves_diagnostics_and_stops_subsequent_mutations(self):
        api, reports = FakeGitHub(denied=True), []
        with self.assertRaisesRegex(ValueError, "incomplete"):
            kit.execute(api, TARGET, LIBRARY, SHA, "true", "true", "install", reports.append)
        self.assertTrue(any("billing" in report for report in reports))
        self.assertFalse(any("/actions/variables" in path or "/git/" in path for _, path, _ in api.calls))

    def test_variable_creation_and_readback(self):
        api = FakeGitHub(enabled=True)
        self.run_action(api, configure="true")
        self.assertEqual(api.variables, {"CODEQL_ENABLED": "true", "DEPENDENCY_REVIEW_ENABLED": "true"})

    def test_false_prerequisites_keep_checks_disabled(self):
        api = FakeGitHub()
        self.run_action(api, configure="true")
        self.assertEqual(set(api.variables.values()), {"false"})
        self.assertFalse(any("/dependency-graph/" in path for _, path, _ in api.calls))

    def test_dependency_review_refusal_is_not_a_false_success(self):
        api = FakeGitHub(enabled=True, review=False)
        self.run_action(api, configure="true")
        self.assertEqual(api.variables["DEPENDENCY_REVIEW_ENABLED"], "false")

    def test_variable_updates_are_idempotent(self):
        api = FakeGitHub(enabled=True)
        api.variables = {"CODEQL_ENABLED": "false", "DEPENDENCY_REVIEW_ENABLED": "false"}
        self.run_action(api, configure="true")
        self.assertEqual(sum(method == "PATCH" for method, _, _ in api.calls), 2)
        api.calls.clear()
        self.run_action(api, configure="true")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_variable_readback_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, "not verified"):
            self.run_action(FakeGitHub(enabled=True, mismatch=True), configure="true")

    def test_summary_escapes_untrusted_messages(self):
        text = kit.table("Test", ["State"], [("<script>|\ninjected",)])
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)
        self.assertIn("\\|", text)

    def test_preview_integration_does_not_mutate_the_fork(self):
        api = FakeGitHub()
        result = self.run_action(api, library_sha=SHA, files_mode="preview")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))
        self.assertEqual(result["proposal-branch"], "")

    def test_install_returns_proposal_outputs_without_updating_default(self):
        api = FakeGitHub()
        result = self.run_action(api, library_sha=SHA, files_mode="install")
        self.assertTrue(result["proposal-branch"].startswith("feature/ghas-setup-"))
        self.assertIn("/compare/integration%2Ftest...feature%2Fghas-setup-", result["compare-url"])
        self.assertEqual(sum(method == "POST" for method, _, _ in api.calls), 3)
        self.assertFalse(any(method in {"PATCH", "DELETE"} for method, _, _ in api.calls))

    def test_main_writes_summary_and_outputs_without_logging_token(self):
        with tempfile.TemporaryDirectory() as directory:
            output, report = Path(directory) / "outputs", Path(directory) / "summary"
            env = {"GH_TOKEN": "fictitious-token-never-log", "GHAS_TARGET": TARGET,
                   "GHAS_LIBRARY": LIBRARY, "GITHUB_OUTPUT": str(output),
                   "GITHUB_STEP_SUMMARY": str(report)}
            capture = io.StringIO()
            with patch.dict(kit.os.environ, env, clear=True), patch.object(kit, "GitHub", return_value=FakeGitHub()):
                with redirect_stdout(capture):
                    kit.main()
            self.assertIn("repository-id=123", output.read_text())
            self.assertIn("GHAS fork inspection", report.read_text())
            self.assertNotIn(env["GH_TOKEN"], capture.getvalue() + report.read_text() + output.read_text())


if __name__ == "__main__":
    unittest.main()
