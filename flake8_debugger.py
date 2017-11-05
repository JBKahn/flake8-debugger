"""Extension for flake8 that finds usage of the debugger."""
import ast
from itertools import chain

import pycodestyle


__version__ = '2.0.0'

DEBUGGER_ERROR_CODE = 'T002'

#
# def flake8ext(f):
#     """Decorate flake8 extension function."""
#     f.name = 'flake8-debugger'
#     f.version = __version__
#     return f

#
# def format_debugger_message(import_type, item_imported, item_alias, trace_method, trace_alias):
#     if import_type == 'import':
#         if item_imported == item_alias:
#             return '{0} import for {1} found'.format(DEBUGGER_ERROR_CODE, item_alias)
#         else:
#             return '{0} import for {1} found as {2}'.format(DEBUGGER_ERROR_CODE, item_imported, item_alias)
#     elif import_type == 'import_trace':
#         if trace_method == trace_alias:
#             return '{0} import for {1}.{2} found'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method)
#         else:
#             return '{0} import for {1}.{2} found as {3}'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method, trace_alias)
#     elif import_type == 'trace_used':
#         if trace_method == trace_alias:
#             return '{0} trace found: {1}.{2} used'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method)
#         else:
#             return '{0} trace found: {1}.{2} used as {3}'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method, trace_alias)

# def check_for_debugger_import(logical_line, checker_state):
#     for node in ast.walk(ast.parse(logical_line)):
#         if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
#
#             if hasattr(node, 'module') and node.module not in debuggers.keys():
#                 continue
#
#             module_names = (hasattr(node, 'names') and [module_name.name for module_name in node.names]) or []
#             if isinstance(node, ast.Import):
#                 for debugger in debuggers.keys():
#                     if debugger in module_names:
#                         index = module_names.index(debugger)
#                         yield 'import', debugger, getattr(node.names[index], 'asname', None) or debugger, debuggers[debugger], debuggers[debugger]
#
#             elif isinstance(node, ast.ImportFrom):
#                 trace_methods = debuggers.values()
#                 traces_found = set([trace for trace in trace_methods if trace in module_names])
#                 if not traces_found:
#                     continue
#                 for trace in traces_found:
#                     trace_index = trace in module_names and module_names.index(trace)
#                     yield 'import_trace', node.module, node.module, debuggers[node.module], getattr(node.names[trace_index], 'asname', None) or debuggers[node.module]
#
#
# def check_for_set_trace_usage(logical_line, checker_state):
#     for node in ast.walk(ast.parse(logical_line)):
#         if isinstance(node, ast.Call):
#             trace_methods = [checker_state['debuggers_found'][debugger]['trace_alias'] for debugger in checker_state['debuggers_found'].keys()]
#             if (getattr(node.func, 'attr', None) in trace_methods or getattr(node.func, 'id', None) in trace_methods):
#                 for debugger, debugger_info in checker_state['debuggers_found'].items():
#                     trace_method_name = checker_state['debuggers_found'][debugger]['trace_alias']
#                     if (
#                         (hasattr(node.func, 'value') and node.func.value.id == debugger_info['alias']) or
#                         (hasattr(node.func, 'id') and trace_method_name and node.func.id == trace_method_name)
#                     ):
#                         yield 'trace_used', debugger, debugger_info['alias'], debugger_info['trace_method'], debugger_info['trace_alias']
#                         break
#
#
# @flake8ext
# def debugger_usage(logical_line, checker_state=None, noqa=None):
#     if 'debuggers_found' not in checker_state:
#         checker_state['debuggers_found'] = {}
#     generator = check_for_debugger_import(logical_line, checker_state.copy())
#
#     for import_type, item_imported, item_alias, trace_method, trace_alias in generator:
#         if item_imported is not None:
#             checker_state['debuggers_found'][item_imported] = {
#                 'alias': item_alias, 'trace_method': trace_method, 'trace_alias': trace_alias
#             }
#             if not noqa:
#                 yield 0, format_debugger_message(import_type, item_imported, item_alias, trace_method, trace_alias)
#
#     if not noqa:
#         generator = check_for_set_trace_usage(logical_line, checker_state.copy())
#         for usage in generator:
#             yield 0, format_debugger_message(*usage)


debuggers = {
    'pdb': 'set_trace',
    'ipdb': 'set_trace',
    'IPython.terminal.embed': 'InteractiveShellEmbed',
    'IPython.frontend.terminal.embed': 'InteractiveShellEmbed',
}


VIOLATIONS = {
    'found': {
        'set_trace': 'T001 set_trace found.',
        'InteractiveShellEmbed': 'T003 InteractiveShellEmbed found.',
    },
    'declared': {
        'print': 'T101 Python 2.x reserved word print used.',
        'pprint': 'T103 pprint declared',
    },
}


class DebuggerFinder(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super(DebuggerFinder, self).__init__(*args, **kwargs)
        self.debuggers_used = {}
        self.debuggers_traces_redefined = {}
        self.debuggers_traces_names = {}
        self.debugger_traces_imported = {}
        self.debuggers_names = {}
        self.debuggers_redefined = {}
        self.debuggers_imported = {}

    def visit_Call(self, node):
        debugger_method_names = chain(debuggers.values(), self.debuggers_traces_names.values())
        is_debugger_function = getattr(node.func, "id", None) in list(debugger_method_names)
        if is_debugger_function:
            if node.func.id in self.debuggers_traces_names.values():
                debugger_method = next(item[0] for item in self.debuggers_traces_names.items() if item[1] == node.func.id)
                entry = self.debuggers_used.setdefault((node.lineno, node.col_offset), [])
                if debugger_method == node.func.id:
                    entry.append('{0} trace found: {1} used'.format(DEBUGGER_ERROR_CODE, node.func.id))
                else:
                    entry.append('{0} trace found: {1} used as {2}'.format(DEBUGGER_ERROR_CODE, debugger_method, node.func.id))

        debugger_method_names = chain(debuggers.values(), self.debuggers_traces_names.values())
        is_debugger_attribute = getattr(node.func, "attr", None) in list(debugger_method_names)
        if is_debugger_attribute:
            caller = node.func.value.id
            entry = self.debuggers_used.setdefault((node.lineno, node.col_offset), [])
            if caller in self.debuggers_names.values():
                entry.append('{0} trace found: {1}.{2} used'.format(DEBUGGER_ERROR_CODE, caller, node.func.attr))
            else:
                entry.append('{0} trace found: {1} used'.format(DEBUGGER_ERROR_CODE, node.func.attr))
        self.generic_visit(node)

    def visit_Import(self, node):
        for name_node in node.names:
            if name_node.name in list(debuggers.keys()):
                if name_node.asname is not None:
                    self.debuggers_names[name_node.name] = name_node.asname
                    entry = self.debuggers_redefined.setdefault((node.lineno, node.col_offset), [])
                    entry.append('{0} import for {1} found as {2}'.format(DEBUGGER_ERROR_CODE, name_node.name, name_node.asname))
                else:
                    self.debuggers_names[name_node.name] = name_node.name
                    entry = self.debuggers_imported.setdefault((node.lineno, node.col_offset), [])
                    entry.append('{0} import for {1} found'.format(DEBUGGER_ERROR_CODE, name_node.name))

    def visit_ImportFrom(self, node):
        if node.module in list(debuggers.keys()):
            for name_node in node.names:
                if name_node.name == debuggers[node.module]:
                    if name_node.asname is not None:
                        self.debuggers_traces_names[name_node.name] = name_node.asname
                        entry = self.debuggers_traces_redefined.setdefault((node.lineno, node.col_offset), [])
                        entry.append('{0} import for {1} found as {2}'.format(DEBUGGER_ERROR_CODE, name_node.name, name_node.asname))
                    else:
                        self.debuggers_traces_names[name_node.name] = name_node.name
                        entry = self.debugger_traces_imported.setdefault((node.lineno, node.col_offset), [])
                        entry.append('{0} import for {1} found'.format(DEBUGGER_ERROR_CODE, name_node.name))


class DebuggerChecker(object):
    options = None
    name = 'flake8-debugger'
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        self.lines = None

    def load_file(self):
        if self.filename in ("stdin", "-", None):
            self.filename = "stdin"
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

        if not self.tree:
            self.tree = ast.parse("".join(self.lines))

    def run(self):
        if not self.tree or not self.lines:
            self.load_file()

        parser = DebuggerFinder()
        parser.visit(self.tree)
        for error, messages in parser.debuggers_used.items():
            if not pycodestyle.noqa(self.lines[error[0] - 1]):
                for message in messages:
                    yield (error[0], error[1], message, DebuggerChecker)

        for error, messages in chain(
                parser.debuggers_traces_redefined.items(),
                parser.debugger_traces_imported.items(),
                parser.debuggers_redefined.items(),
                parser.debuggers_imported.items(),
        ):
            if error not in parser.debuggers_used:
                if not pycodestyle.noqa(self.lines[error[0] - 1]):
                    for message in messages:
                        yield (error[0], error[1], message, DebuggerChecker)
