import unittest
from tools import find_files, manage_files, git_manager
import os
import shutil
from pathlib import Path

class TestRobotTools(unittest.TestCase):
    def setUp(self):
        # Create a dummy test environment in the current directory
        self.test_dir = Path("test_env")
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "test_file.txt").write_text("hello")
        (self.test_dir / "sub").mkdir(exist_ok=True)
        (self.test_dir / "sub" / "other.pdf").write_text("fake pdf")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_find_files(self):
        # We need to search in our test_dir, manage_files allows generic paths or defaults to Docs
        # find_files defaults to Documents but accepts search_path
        results = find_files("test_file", search_path=str(self.test_dir))
        self.assertTrue(any("test_file.txt" in r for r in results))

    def test_manage_files_copy(self):
        src = str(self.test_dir / "test_file.txt")
        target = str(self.test_dir / "target")
        manage_files("copy", [src], target)
        self.assertTrue((Path(target) / "test_file.txt").exists())

    def test_git_manager_init(self):
        # Test git init in a safe temp dir
        repo_dir = self.test_dir / "repo"
        repo_dir.mkdir()
        (repo_dir / "code.py").write_text("print('hi')")
        
        # We won't push, just init and commit
        result = git_manager(str(repo_dir))
        self.assertIn("Git operations successful", result)
        self.assertTrue((repo_dir / ".git").exists())

if __name__ == "__main__":
    unittest.main()
