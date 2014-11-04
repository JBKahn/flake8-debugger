import pep8
import ast
import tokenize

from sys import stdin

__version__ = '1.3'

DEBUGGER_ERROR_CODE = 'T002'


class DebugStatementChecker(object):
    name = 'flake8-debugger'
    version = __version__

    def __init__(self, tree, filename='(none)', builtins=None):
        self.tree = tree
        self.filename = (filename == 'stdin' and stdin) or filename

    def run(self):
        if self.filename == stdin:
            noqa = get_noqa_lines(self.filename)
        else:
            with open(self.filename, 'r') as file_to_check:
                noqa = get_noqa_lines(file_to_check.readlines())

        errors = check_tree_for_debugger_statements(self.tree, noqa)

        for error in errors:
            yield (error.get("line"), error.get("col"), error.get("message"), type(self))


def get_noqa_lines(code):
    tokens = tokenize.generate_tokens(lambda L=iter(code): next(L))
    noqa = [token[2][0] for token in tokens if token[0] == tokenize.COMMENT and (token[1].endswith('noqa') or (isinstance(token[0], str) and token[0].endswith('noqa')))]
    return noqa


def check_code_for_debugger_statements(code):
    tree = ast.parse(code)
    noqa = get_noqa_lines(code.split("\n"))
    return check_tree_for_debugger_statements(tree, noqa)


def format_debugger_message(item_type, item_found, name_used):
    return '{0} {1} for {2} found as {3}'.format(DEBUGGER_ERROR_CODE, item_type, item_found, name_used)


def check_tree_for_debugger_statements(tree, noqa):
    errors = []
    ipdb_name = 'ipdb'
    ipdb_set_trace_name = 'set_trace'
    pdb_name = 'pdb'
    pdb_set_trace_name = 'set_trace'
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            pdb_found = False
            ipdb_found = False
            if hasattr(node, 'module') and node.module not in ['ipdb', 'pdb']:
                continue
            elif hasattr(node, 'module'):
                ipdb_found = node.module == 'ipdb'
                pdb_found = not ipdb_found
            if hasattr(node, 'names'):
                module_names = [module_name.name for module_name in node.names]

                if 'ipdb' in module_names:
                    ipdb_index = module_names.index('ipdb')
                    if hasattr(node.names[ipdb_index], 'asname'):
                        ipdb_name = node.names[ipdb_index].asname or ipdb_name
                        ipdb_found = True

                if 'pdb' in module_names:
                    pdb_index = module_names.index('pdb')
                    if  hasattr(node.names[pdb_index], 'asname'):
                        pdb_name = node.names[pdb_index].asname or pdb_name
                        pdb_found = True

            if node.lineno not in noqa:
                if ipdb_found:
                    errors.append({
                        "message": format_debugger_message('import', 'ipdb', ipdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
                if pdb_found:
                    errors.append({
                        "message": format_debugger_message('import', 'pdb', pdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
        elif isinstance(node, ast.ImportFrom):
            pdb_found = False
            ipdb_found = False
            if hasattr(node, 'module') and node.module not in ['ipdb', 'pdb']:
                continue
            else:
                ipdb_found = node.module == 'ipdb'
                pdb_found = not ipdb_found

            module_names = [module_name.name for module_name in node.names]
            if 'set_trace' not in module_names:
                continue
            trace_index = 'set_trace' in module_names and module_names.index('set_trace')
            if hasattr(node.names[trace_index], 'asname'):
                if pdb_found:
                    pdb_set_trace_name = node.names[trace_index].asname or pdb_set_trace_name
                if ipdb_found:
                    ipdb_set_trace_name = node.names[trace_index].asname or ipdb_set_trace_name
            if node.lineno not in noqa:
                if ipdb_found:
                    errors.append({
                        "message": format_debugger_message('import', 'ipdb', ipdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
                if pdb_found:
                    errors.append({
                        "message": format_debugger_message('import', 'pdb', pdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
        elif hasattr(node, 'value') and  isinstance(node.value, ast.Call):
            if (hasattr(node.value.func, 'attr') and node.value.func.attr == pdb_set_trace_name or hasattr(node.value.func, 'id') and node.value.func.id == pdb_set_trace_name) and node.lineno not in noqa:
                if (hasattr(node.value.func, 'value') and node.value.func.value.id == pdb_name):
                    debugger_name = 'pdb'
                elif (hasattr(node.value.func, 'value') and node.value.func.value.id == ipdb_name):
                    debugger_name = 'ipdb'
                else:
                    debugger_name = 'debugger'
                errors.append({
                    "message": format_debugger_message('set_trace', debugger_name, pdb_set_trace_name),
                    "line": node.lineno,
                    "col": node.col_offset
                })
            elif (hasattr(node.value.func, 'attr') and node.value.func.attr == ipdb_set_trace_name or hasattr(node.value.func, 'id') and node.value.func.id == ipdb_set_trace_name) and node.lineno not in noqa:
                if (hasattr(node.value.func, 'value') and node.value.func.value.id == ipdb_name):
                    debugger_name = 'ipdb'
                elif (hasattr(node.value.func, 'value') and node.value.func.value.id == pdb_name):
                    debugger_name = 'pdb'
                else:
                    debugger_name = 'debugger'
                errors.append({
                    "message": format_debugger_message('set_trace', debugger_name, ipdb_set_trace_name),
                    "line": node.lineno,
                    "col": node.col_offset
                })
    return errors
