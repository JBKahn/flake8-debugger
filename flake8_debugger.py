"""Extension for flake8 that finds usage of the debugger."""
import ast
from itertools import chain

import pycodestyle


__version__ = '3.1.0'

DEBUGGER_ERROR_CODE = 'T100'

debuggers = {
    'pdb': ['set_trace'],
    'pudb': ['set_trace'],
    'ipdb': ['set_trace', 'sset_trace'],
    'IPython.terminal.embed': ['InteractiveShellEmbed'],
    'IPython.frontend.terminal.embed': ['InteractiveShellEmbed'],
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
        debugger_method_names = list(chain(self.debuggers_traces_names.values(), *debuggers.values()))
        is_debugger_function = getattr(node.func, "id", None) in debugger_method_names
        if is_debugger_function:
            if node.func.id in self.debuggers_traces_names.values():
                debugger_method = next(item[0] for item in self.debuggers_traces_names.items() if item[1] == node.func.id)
                entry = self.debuggers_used.setdefault((node.lineno, node.col_offset), [])
                if debugger_method == node.func.id:
                    entry.append('{0} trace found: {1} used'.format(DEBUGGER_ERROR_CODE, node.func.id))
                else:
                    entry.append('{0} trace found: {1} used as {2}'.format(DEBUGGER_ERROR_CODE, debugger_method, node.func.id))

        is_debugger_attribute = getattr(node.func, "attr", None) in debugger_method_names
        if is_debugger_attribute:
            caller = getattr(node.func.value, "id", None)
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
                if name_node.name in debuggers[node.module]:
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
