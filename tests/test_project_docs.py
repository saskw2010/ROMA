from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_project_docs_exist():
    assert (REPO_ROOT / "PROJECTS.md").is_file()
    assert (REPO_ROOT / "projects" / "ghinek" / "README.md").is_file()


def test_readme_links_point_to_existing_project_docs():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "./PROJECTS.md" in readme
    assert "./projects/ghinek/README.md" in readme
