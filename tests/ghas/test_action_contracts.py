import os
from pathlib import Path
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


def document(relative):
    # BaseLoader keeps the GitHub Actions key "on" as a string (YAML 1.2).
    with (ROOT / relative).open(encoding="utf-8") as source:
        return yaml.load(source, Loader=yaml.BaseLoader)


class ActionContractTests(unittest.TestCase):
    def test_delivery_adapters_and_examples_pin_library_actions(self):
        paths = [f".github/workflows/ghas-{name}.yml" for name in
                 ("codeql", "dependency-review", "prepare-fork")]
        paths += ["exemples/ghas/security.yml", "exemples/ghas/prepare-fork.yml"]
        for path in paths:
            workflow = document(path)
            references = [step["uses"] for job in workflow["jobs"].values()
                          for step in job["steps"] if "uses" in step
                          and step["uses"].startswith("MCN-CQEN/ceai-cqen-scripts-lib/actions/ghas-")]
            self.assertTrue(references, path)
            for reference in references:
                self.assertRegex(reference, r"@[a-f0-9]{40}$", path)

    def test_temporary_pilot_workflows_are_not_delivered(self):
        for filename in ("ghas-pilot.yml", "ghas-composite-preview-test.yml"):
            self.assertFalse((ROOT / ".github/workflows" / filename).exists())

    def test_actions_are_step_libraries_not_workflows(self):
        for name in ("ghas-codeql", "ghas-dependency-review", "ghas-prepare-fork"):
            with self.subTest(name=name):
                action = document(f"actions/{name}/action.yml")
                self.assertEqual(action["runs"]["using"], "composite")
                self.assertTrue(action["runs"]["steps"])
                self.assertTrue((ROOT / f"actions/{name}/README.md").is_file())
                self.assertFalse({"jobs", "on", "permissions", "runs-on"}.intersection(action))
                for step in action["runs"]["steps"]:
                    if "run" in step:
                        self.assertEqual(step["shell"], "bash")
                        self.assertNotIn("${{", step["run"])

    def test_adapters_delegate_instead_of_implementing_scans(self):
        for name in ("codeql", "dependency-review", "prepare-fork"):
            workflow = document(f".github/workflows/ghas-{name}.yml")
            steps = [step for job in workflow["jobs"].values() for step in job["steps"]]
            uses = [step.get("uses", "") for step in steps]
            self.assertTrue(any(f"/actions/ghas-{name}@" in use for use in uses))
            self.assertFalse(any(use.startswith(("github/codeql-action/", "actions/dependency-review-action@"))
                                 for use in uses))

    def test_security_example_owns_jobs_matrix_and_permissions(self):
        workflow = document("exemples/ghas/security.yml")
        self.assertIn("pull_request", workflow["on"])
        self.assertNotIn("pull_request_target", workflow["on"])
        codeql = workflow["jobs"]["codeql"]
        self.assertEqual(codeql["strategy"]["matrix"]["language"], ["actions", "python"])
        self.assertEqual(codeql["permissions"]["security-events"], "write")
        self.assertIn("pull_request", workflow["jobs"]["dependency-review"]["if"])
        for job in workflow["jobs"].values():
            self.assertIn("runs-on", job)
            self.assertNotIn("uses", job)
            self.assertTrue(job["steps"][-1]["uses"].startswith("MCN-CQEN/ceai-cqen-scripts-lib/actions/"))
        self.assertNotIn("GHAS_APP_PRIVATE_KEY", (ROOT / "exemples/ghas/security.yml").read_text())

    def test_administration_example_is_manual_and_requires_explicit_mutation(self):
        workflow = document("exemples/ghas/prepare-fork.yml")
        self.assertEqual(list(workflow["on"]), ["workflow_dispatch"])
        inputs = workflow["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["enable_security"]["default"], "false")
        self.assertEqual(inputs["configure_variables"]["default"], "false")
        self.assertEqual(inputs["files_mode"]["default"], "preview")
        steps = workflow["jobs"]["prepare"]["steps"]
        self.assertTrue(all("checkout@" not in step.get("uses", "") for step in steps))
        for step in steps:
            if "create-github-app-token@" in step.get("uses", ""):
                self.assertTrue(step["with"]["owner"])
                self.assertTrue(step["with"]["repositories"])

    def test_preparation_loads_trusted_action_scripts_and_no_implicit_app_secrets(self):
        action = document("actions/ghas-prepare-fork/action.yml")
        step = action["runs"]["steps"][0]
        self.assertEqual(step["env"]["GHAS_ACTION_PATH"], "${{ github.action_path }}")
        self.assertEqual(step["run"], 'python3 "$GHAS_ACTION_PATH/prepare_fork.py"')
        self.assertEqual(step["env"]["GH_TOKEN"], "${{ inputs.github-token }}")
        self.assertNotIn("secrets.", (ROOT / "actions/ghas-prepare-fork/action.yml").read_text())

    def test_codeql_guard_accepts_only_supported_single_language(self):
        script = document("actions/ghas-codeql/action.yml")["runs"]["steps"][0]["run"]
        for language in ("actions", "python", "ruby", "javascript-typescript", "java-kotlin", "python,actions", ""):
            result = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                                    env={**os.environ, "GHAS_LANGUAGE": language})
            self.assertEqual(result.returncode == 0,
                             language in {"actions", "python", "ruby", "javascript-typescript"})

    def test_review_guard_rejects_privileged_events_and_invalid_severity(self):
        script = document("actions/ghas-dependency-review/action.yml")["runs"]["steps"][0]["run"]
        for event, severity in [("pull_request", "low"), ("pull_request", "critical"),
                                ("pull_request_target", "low"), ("push", "low"), ("pull_request", "none")]:
            result = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                                    env={**os.environ, "GHAS_EVENT": event, "GHAS_SEVERITY": severity})
            self.assertEqual(result.returncode == 0, event == "pull_request" and severity != "none")


if __name__ == "__main__":
    unittest.main()
