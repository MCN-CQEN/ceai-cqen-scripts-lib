import importlib.util
import json
from pathlib import Path
import unittest


MODULE = Path(__file__).resolve().parents[2] / "scripts/ghas/prepare_files.py"
SPEC = importlib.util.spec_from_file_location("prepare_files", MODULE)
kit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kit)
TARGET = "MCN-CQEN/example-ghas"
LIBRARY = "MCN-CQEN/ceai-cqen-scripts-lib"
SHA = "b" * 40
BASE = "a" * 40


class FakeGitHub:
    def __init__(self, files=(), *, fork=True, truncated=False, proposal=None):
        self.calls = []
        self.files = {path: {"path": path, "type": "blob", "mode": "100644",
                             "sha": kit.blob_sha(content)} for path, content in files}
        self.fork, self.truncated, self.proposal = fork, truncated, proposal

    def request(self, method, path, data=None):
        self.calls.append((method, path, data))
        if method == "GET":
            if path == f"/repos/{TARGET}":
                return {"full_name": TARGET, "fork": self.fork, "parent": {"id": 1}, "default_branch": "integration/test",
                        "html_url": f"https://github.com/{TARGET}"}
            if path.endswith("/git/ref/heads/integration%2Ftest"):
                return {"object": {"sha": BASE}}
            if path.endswith("/git/commits/" + BASE):
                return {"tree": {"sha": "base-tree"}}
            if path.endswith("/git/trees/base-tree?recursive=1"):
                return {"tree": list(self.files.values()), "truncated": self.truncated}
            if "/git/ref/heads/ghas/setup-" in path:
                if self.proposal:
                    return {"object": {"sha": "existing-proposal"}}
                raise kit.ApiError(404, "Not Found")
            if path.endswith("/git/commits/existing-proposal"):
                return {"tree": {"sha": self.proposal}}
        elif method == "POST":
            if path.endswith("/git/trees"):
                return {"sha": "new-tree"}
            if path.endswith("/git/commits"):
                return {"sha": "new-commit"}
            if path.endswith("/git/refs"):
                return {"ref": data["ref"]}
        raise AssertionError((method, path, data))


class PreparationTests(unittest.TestCase):
    def test_inventory_is_project_specific_and_deduplicates_directories(self):
        info = kit.inventory(["src/app.py", "web/app.tsx", "tool.rb", "src/main.go",
                              "infra/main.tf", "infra/variables.tf", "web/package.json",
                              "requirements.txt", "vendor/unrelated/Cargo.toml"])
        self.assertEqual(info["languages"], ["actions", "javascript-typescript", "python", "ruby"])
        self.assertEqual(info["profiles_required"], ["go"])
        pairs = [(u["package-ecosystem"], u["directory"]) for u in info["updates"]]
        self.assertIn(("npm", "/web"), pairs)
        self.assertIn(("pip", "/"), pairs)
        self.assertEqual(pairs.count(("terraform", "/infra")), 1)
        self.assertNotIn(("cargo", "/vendor/unrelated"), pairs)

    def test_monorepo_limit_does_not_silently_truncate(self):
        with self.assertRaisesRegex(ValueError, "100"):
            kit.inventory([f"app{i}/package.json" for i in range(101)])

    def test_render_uses_actual_branch_and_immutable_library_ref(self):
        files = kit.render(kit.inventory(["src/main.py"]), "integration/test", LIBRARY, SHA)
        workflow = json.loads(files[kit.WORKFLOW])
        self.assertEqual(workflow["on"]["push"]["branches"], ["integration/test"])
        self.assertEqual(json.loads(workflow["jobs"]["codeql"]["with"]["languages"]), ["actions", "python"])
        for job in workflow["jobs"].values():
            self.assertTrue(job["uses"].endswith("@" + SHA))
        self.assertNotIn("secrets", workflow["jobs"]["codeql"])
        self.assertNotIn("id-token", workflow["permissions"])

    def test_preview_never_mutates_repository(self):
        api = FakeGitHub([("different-project/main.tf", "terraform {}")])
        plan = kit.prepare(api, TARGET, LIBRARY, SHA)
        self.assertEqual(plan["installation"], "preview only")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))
        self.assertNotIn("proposal_branch", plan)

    def test_existing_dependabot_is_preserved_including_yaml_extension(self):
        for path in [kit.DEPENDABOT, ".github/dependabot.yaml"]:
            with self.subTest(path=path):
                api = FakeGitHub([(path, "version: 2\nupdates: []\n")])
                plan = kit.prepare(api, TARGET, LIBRARY, SHA)
                self.assertNotIn(kit.DEPENDABOT, plan["files"])
                self.assertTrue(any("preserved" in warning for warning in plan["warnings"]))

    def test_truncated_tree_is_rejected_before_writes(self):
        api = FakeGitHub(truncated=True)
        with self.assertRaisesRegex(ValueError, "Truncated"):
            kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertTrue(all(call[0] == "GET" for call in api.calls))

    def test_source_and_foreign_targets_are_rejected(self):
        api = FakeGitHub(fork=False)
        with self.assertRaisesRegex(ValueError, "active GitHub fork"):
            kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        for target in [LIBRARY, "another-org/example"]:
            with self.assertRaises(ValueError):
                kit.prepare(FakeGitHub(), target, LIBRARY, SHA)

    def test_mutable_library_ref_is_rejected(self):
        api = FakeGitHub()
        with self.assertRaises(ValueError):
            kit.prepare(api, TARGET, LIBRARY, "feature/ghas-toolkit")
        self.assertEqual(api.calls, [])

    def test_redirected_repository_identity_is_rejected(self):
        api = FakeGitHub()
        original = api.request

        def request(method, path, data=None):
            response = original(method, path, data)
            if path == f"/repos/{TARGET}":
                response["full_name"] = "another-org/moved-fork"
            return response

        api.request = request
        with self.assertRaisesRegex(ValueError, "another repository"):
            kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertEqual(len(api.calls), 1)

    def test_symlink_output_is_not_replaced(self):
        api = FakeGitHub([(kit.WORKFLOW, "../../somewhere")])
        api.files[kit.WORKFLOW]["mode"] = "120000"
        with self.assertRaisesRegex(ValueError, "regular file"):
            kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_install_creates_one_proposal_commit_and_never_updates_default(self):
        api = FakeGitHub([("main.py", "print('test')")])
        plan = kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        posts = [(path, data) for method, path, data in api.calls if method == "POST"]
        self.assertEqual(len(posts), 3)
        self.assertEqual(posts[1][1]["parents"], [BASE])
        self.assertTrue(posts[2][1]["ref"].startswith("refs/heads/ghas/setup-"))
        self.assertEqual(plan["installation"], "proposal branch created")
        self.assertEqual({item["path"] for item in posts[0][1]["tree"]}, {kit.WORKFLOW, kit.DEPENDABOT})
        self.assertFalse(any(method in {"PATCH", "DELETE"} for method, _, _ in api.calls))

    def test_existing_identical_proposal_is_reused(self):
        api = FakeGitHub(proposal="new-tree")
        plan = kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertEqual(plan["installation"], "existing proposal reused")
        self.assertEqual(sum(method == "POST" for method, _, _ in api.calls), 1)

    def test_existing_modified_proposal_is_not_overwritten(self):
        api = FakeGitHub(proposal="someone-elses-tree")
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertFalse(any(path.endswith("/git/refs") for _, path, _ in api.calls))

    def test_already_configured_default_is_not_recommitted(self):
        files = kit.render(kit.inventory([]), "integration/test", LIBRARY, SHA)
        # Existing Dependabot is preserved; the workflow matches the generated content.
        api = FakeGitHub(files.items())
        plan = kit.prepare(api, TARGET, LIBRARY, SHA, "install")
        self.assertEqual(plan["changed_files"], [])
        self.assertEqual(plan["installation"], "already configured on default branch")
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))


if __name__ == "__main__":
    unittest.main()
