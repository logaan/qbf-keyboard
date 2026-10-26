import ast
import io
import json
from pathlib import Path
import subprocess
import tokenize
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def test_one_dependency_manifest(self):
        paths = subprocess.check_output(['git', 'ls-files', '*package.json'], cwd=ROOT, text=True).splitlines()
        self.assertEqual(paths, ['package.json'])
        lock = json.loads((ROOT / 'package-lock.json').read_text())
        self.assertFalse(any(v.get('resolved', '').startswith('git+ssh:') for v in lock['packages'].values()))

    def test_no_user_markdown(self):
        paths = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=ROOT, text=True).splitlines()
        self.assertTrue(all(Path(p).name.lower() in ('agents.md', 'todo.md') for p in paths))

    def test_no_python_comments_or_docstrings(self):
        paths = subprocess.check_output(['git', 'ls-files', '*.py'], cwd=ROOT, text=True).splitlines()
        for relative in paths:
            path = ROOT / relative
            source = path.read_text()
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                if token.type == tokenize.COMMENT:
                    self.assertTrue(token.string.startswith('#!'), f'{relative}:{token.start[0]}')
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    self.assertIsNone(ast.get_docstring(node), relative)

    def test_todo_format(self):
        lines = (ROOT / 'TODO.md').read_text().splitlines()
        self.assertTrue(lines)
        self.assertTrue(all(line.startswith(('- [ ] @agent ', '- [x] @agent ', '- [ ] @user ', '- [x] @user ', '  ')) for line in lines))


if __name__ == '__main__':
    unittest.main()
