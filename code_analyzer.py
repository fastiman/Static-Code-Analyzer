import argparse
import ast
import os
import re
import typing
from pathlib import Path


def argparse_init() -> 'path to dir or file':
    parser = argparse.ArgumentParser()
    parser.add_argument("user_path",
                        type=str, nargs='?',
                        help="Enter command-line argument user_path",
                        default=False)
    args = parser.parse_args()
    if not args.user_path:
        print("Path is not specified")
        exit(1)
    else:
        if os.path.exists(args.user_path):
            return args.user_path
        else:
            print("Path is not exists")
            exit(1)


class MyCodeAnalyser:
    def __init__(self, file_path: Path):
        self.file = file_path
        with open(self.file, "r") as f:
            self.code = f.readlines()
        self.S001 = "S001 Too long line"
        self.S002 = "S002 Indentation is not a multiple of four"
        self.S003 = "S003 Unnecessary semicolon"
        self.S004 = "S004 At least two spaces required before inline comments"
        self.S005 = "S005 TODO found"
        self.S006 = "S006 More than two blank lines used before this line"
        self.S007 = "S007 Too many spaces after "  # construction_name (def or class)
        self.S008 = "S008 Class name 'class_name' should be written in CamelCase"  # replace class_name
        self.S009 = "S009 Function name 'function_name' should be written in snake_case"  # replace function_name

    def check_code(self):
        for n, line in enumerate(self.code, start=1):
            self.check_001(n, line)
            self.check_002(n, line)
            self.check_003(n, line)
            self.check_004(n, line)
            self.check_005(n, line)
            self.check_006(self.code, n)
            self.check_007(n, line)
            self.check_008(n, line)
            self.check_009(n, line)

    def check_001(self, n, line):
        if len(line) > 79:
            print(f"{self.file}: Line {n}: {self.S001}")

    def check_002(self, n, line):
        if line.startswith(' '):
            spaces_count = len(line) - len(line.lstrip())
            if spaces_count % 4:
                print(f"{self.file}: Line {n}: {self.S002}")

    def check_003(self, n, line):
        template_003 = r'#.*'
        text_line_003 = re.sub(template_003, '', line)
        if text_line_003.rstrip().endswith(';'):
            print(f"{self.file}: Line {n}: {self.S003}")

    def check_004(self, n, line):
        if '#' in line:
            res = re.split(r'#', line)
            if res[0].strip() and not res[0].endswith('  '):
                print(f"{self.file}: Line {n}: {self.S004}")

    def check_005(self, n, line):
        if '#' in line and 'TODO' in line.upper():
            start_index = re.search('TODO', line.upper()).start()
            template_005 = r"[\"']"
            res1 = re.findall(template_005, line[:start_index])
            if not len(res1) % 2:
                print(f"{self.file}: Line {n}: {self.S005}")

    def check_006(self, code, n):
        if code[n - 4:n - 1] == ["\n", "\n", "\n"]:
            print(f"{self.file}: Line {n}: {self.S006}")

    def check_007(self, n, line):
        if 'def' in line:
            def_name = line.split('def')[1][1:]
            if def_name[0] != '_' and def_name[0] == ' ':
                print(f"{self.file}: Line {n}: {self.S007}'def'")
        if 'class' in line:
            class_name = line.split('class')[1][1:]
            if class_name[0] != '_' and class_name[0] == ' ':
                print(f"{self.file}: Line {n}: {self.S007}'class'")

    def check_008(self, n, line):
        if 'class' in line:
            class_name = line.split('class')[1][1:]
            if '(' in class_name:
                class_name_008 = class_name.split('(')[0].lstrip()
            else:
                class_name_008 = class_name[:].strip()[:-1]
            if '_' in class_name_008 \
                    or class_name_008[0] != class_name_008[0].upper():
                print(
                    f"{self.file}: Line {n}: "
                    f"{self.S008}".replace("class_name", class_name_008))

    def check_009(self, n, line):
        if 'def' in line:
            def_name = line.split('def')[1][1:]
            def_name_009 = def_name.strip().split('(')[0]
            if def_name_009[0] != '_' \
                    and def_name_009[0] == def_name_009[0].upper():
                print(
                    f"{self.file}: Line {n}: "
                    f"{self.S009}".replace("function_name", def_name_009))


class TreeAstAnalyzer:
    def __init__(self,
                 file_path: Path,
                 ast_tree: typing.Optional[ast.Module] = None,
                 ):
        self.tree = ast_tree
        self.file = file_path
        self.S010 = "S010 Argument name arg_name should be written in snake_case"
        self.S011 = "S011 Variable var_name should be written in snake_case"
        self.S012 = "S012 The default argument value is mutable"

    def check_010(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                list_args = [arg.arg for arg in node.args.args]
                for arg_name in list_args:
                    if re.match(r'^[A-Z]', arg_name):
                        print(f"{self.file}: Line {node.lineno}: {self.S010}"
                              .replace("arg_name", arg_name))

    def check_011(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                var_name = node.id
                if re.match(r'^[A-Z]', var_name):
                    print(f"{self.file}: Line {node.lineno}: {self.S011}"
                          .replace("var_name", var_name))

    def check_012(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                for item in node.args.defaults:
                    if isinstance(item, ast.List):
                        print(f"{self.file}: Line {node.lineno}: {self.S012}")

    def check_code(self):
        self.check_010()
        self.check_011()
        self.check_012()


if __name__ == '__main__':
    p = Path(argparse_init())
    if p.is_file() and p.match('*.py'):
        ca = MyCodeAnalyser(p)
        ca.check_code()
        with open(p, "r") as ftree:
            tree = ast.parse(ftree.read())
            tree_ast_analyzer = TreeAstAnalyzer(p, tree)
            tree_ast_analyzer.check_code()
    else:
        for file in sorted(p.glob('**/*.py')):
            if not file.name == 'tests.py':
                ca = MyCodeAnalyser(file)
                ca.check_code()
                with open(file, "r") as ftree:
                    tree = ast.parse(ftree.read())
                    tree_ast_analyzer = TreeAstAnalyzer(file, tree)
                    tree_ast_analyzer.check_code()
