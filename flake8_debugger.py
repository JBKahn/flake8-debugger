import ast
import tokenize

from sys import stdin

__version__ = '1.3.2'

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
    pdb_found = False
    ipdb_found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            pdb_found_here = False
            ipdb_found_here = False
            if hasattr(node, 'module') and node.module not in ['ipdb', 'pdb']:
                continue
            elif hasattr(node, 'module'):
                ipdb_found = ipdb_found_here = node.module == 'ipdb'
                pdb_found = pdb_found_here = not ipdb_found

            module_names = (hasattr(node, 'names') and [module_name.name for module_name in node.names]) or []
            if isinstance(node, ast.Import):
                if 'ipdb' in module_names:
                    ipdb_index = module_names.index('ipdb')
                    if hasattr(node.names[ipdb_index], 'asname'):
                        ipdb_name = node.names[ipdb_index].asname or ipdb_name
                        ipdb_found = ipdb_found_here = True

                if 'pdb' in module_names:
                    pdb_index = module_names.index('pdb')
                    if hasattr(node.names[pdb_index], 'asname'):
                        pdb_name = node.names[pdb_index].asname or pdb_name
                        pdb_found = pdb_found_here = True

            elif isinstance(node, ast.ImportFrom):
                if 'set_trace' not in module_names:
                    continue
                trace_index = 'set_trace' in module_names and module_names.index('set_trace')
                if hasattr(node.names[trace_index], 'asname'):
                    if pdb_found_here:
                        pdb_set_trace_name = node.names[trace_index].asname or pdb_set_trace_name
                    if ipdb_found_here:
                        ipdb_set_trace_name = node.names[trace_index].asname or ipdb_set_trace_name

            if node.lineno not in noqa:
                if ipdb_found_here:
                    errors.append({
                        "message": format_debugger_message('import', 'ipdb', ipdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
                if pdb_found_here:
                    errors.append({
                        "message": format_debugger_message('import', 'pdb', pdb_name),
                        "line": node.lineno,
                        "col": node.col_offset
                    })
        elif isinstance(node, ast.Call):
            if (
                (
                    hasattr(node.func, 'attr') and node.func.attr in [pdb_set_trace_name, ipdb_set_trace_name] or
                    hasattr(node.func, 'id') and node.func.id in [pdb_set_trace_name, ipdb_set_trace_name]
                ) and node.lineno not in noqa
            ):
                if (hasattr(node.func, 'value') and node.func.value.id == pdb_name) and pdb_found:
                    debugger_name = pdb_name
                elif (hasattr(node.func, 'value') and node.func.value.id == ipdb_name) and ipdb_found:
                    debugger_name = ipdb_name
                else:
                    if not pdb_found:
                        debugger_name = ipdb_name
                    elif not ipdb_found:
                        debugger_name = pdb_name
                    else:
                        debugger_name = 'debugger'
                if not pdb_found and not ipdb_found:
                    continue
                set_trace_name = hasattr(node.func, 'attr') and node.func.attr or hasattr(node.func, 'id') and node.func.id
                errors.append({
                    "message": format_debugger_message('set_trace', debugger_name, set_trace_name),
                    "line": node.lineno,
                    "col": node.col_offset
                })
    return errors
