"""Read-only source comparison against an explicitly supplied local Git ref.

This detects identical files, not plagiarism or independent authorship. It never
reads .env, databases, Git credentials or the original project's secret files.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def digest(blob):
    return hashlib.sha256(blob.replace(b'\r\n', b'\n')).hexdigest()


def python_structure(blob):
    try:
        tree = ast.parse(blob.decode('utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                    node.body.pop(0)
        return ast.dump(tree, include_attributes=False) if tree.body else None
    except (ValueError, SyntaxError, UnicodeError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='e7b34807e384e802851f916332340b2f311b2941')
    args = parser.parse_args()
    revision = git('rev-parse', '--verify', args.ref + '^{commit}').decode().strip()
    reference_paths = git('ls-tree', '-r', '--name-only', revision, '--', 'app').decode().splitlines()
    original = {path: git('show', revision + ':' + path) for path in reference_paths}
    equal, structural = [], []
    current = [path for path in (ROOT / 'app').rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix in {'.py', '.js', '.css', '.html'}]
    for path in current:
        relative, blob = path.relative_to(ROOT).as_posix(), path.read_bytes()
        if len(blob.strip()) < 80:
            continue
        for previous, previous_blob in original.items():
            if digest(blob) == digest(previous_blob):
                equal.append({'current': relative, 'reference': previous})
            elif path.suffix == '.py' and previous.endswith('.py'):
                left, right = python_structure(blob), python_structure(previous_blob)
                if left and right and left == right:
                    structural.append({'current': relative, 'reference': previous})
    print(json.dumps({'reference_commit': revision, 'current_source_file_count': len(current),
                      'reference_source_file_count': len(original), 'identical_nontrivial_files': equal,
                      'identical_python_ast_ignoring_docstrings': structural,
                      'limitation': 'Full-file comparison; not proof of ownership, licensing or absence of shared fragments.'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
