"""Extension for flake8 that finds usage of the debugger."""
import ast


__version__ = '2.1.0'

DEBUGGER_ERROR_CODE = 'T002'


def flake8ext(f):
    """Decorate flake8 extension function."""
    f.name = 'flake8-debugger'
    f.version = __version__
    return f


def format_debugger_message(import_type, item_imported, item_alias, trace_method, trace_alias):
    if import_type == 'import':
        if item_imported == item_alias:
            return '{0} import for {1} found'.format(DEBUGGER_ERROR_CODE, item_alias)
        else:
            return '{0} import for {1} found as {2}'.format(DEBUGGER_ERROR_CODE, item_imported, item_alias)
    elif import_type == 'import_trace':
        if trace_method == trace_alias:
            return '{0} import for {1}.{2} found'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method)
        else:
            return '{0} import for {1}.{2} found as {3}'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method, trace_alias)
    elif import_type == 'trace_used':
        if trace_method == trace_alias:
            return '{0} trace found: {1}.{2} used'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method)
        else:
            return '{0} trace found: {1}.{2} used as {3}'.format(DEBUGGER_ERROR_CODE, item_imported, trace_method, trace_alias)


debuggers = {
    'pdb': 'set_trace',
    'ipdb': 'set_trace',
    'IPython.terminal.embed': 'InteractiveShellEmbed',
    'IPython.frontend.terminal.embed': 'InteractiveShellEmbed',
}


def check_for_debugger_import(logical_line, checker_state):
    for node in ast.walk(ast.parse(logical_line)):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):

            if hasattr(node, 'module') and node.module not in debuggers.keys():
                continue

            module_names = (hasattr(node, 'names') and [module_name.name for module_name in node.names]) or []
            if isinstance(node, ast.Import):
                for debugger in debuggers.keys():
                    if debugger in module_names:
                        index = module_names.index(debugger)
                        if hasattr(node.names[index], 'asname'):
                            yield 'import', debugger, node.names[index].asname or debugger, debuggers[debugger], debuggers[debugger]
                        else:
                            yield 'import', debugger, debugger, debuggers[debugger], debuggers[debugger]

            elif isinstance(node, ast.ImportFrom):
                trace_methods = debuggers.values()
                traces_found = set([trace for trace in trace_methods if trace in module_names])
                if not traces_found:
                    continue
                for trace in traces_found:
                    trace_index = trace in module_names and module_names.index(trace)
                    if hasattr(node.names[trace_index], 'asname'):
                        yield 'import_trace', node.module, node.module, debuggers[node.module], node.names[trace_index].asname or debuggers[node.module]
                    else:
                        yield 'import_trace', node.module, node.module, debuggers[node.module], debuggers[node.module]


def check_for_set_trace_usage(logical_line, checker_state):
    for node in ast.walk(ast.parse(logical_line)):
        if isinstance(node, ast.Call):
            trace_methods = [checker_state['debuggers_found'][debugger]['trace_alias'] for debugger in checker_state['debuggers_found'].keys()]
            if (getattr(node.func, 'attr', None) in trace_methods or getattr(node.func, 'id', None) in trace_methods):
                for debugger, debugger_info in checker_state['debuggers_found'].items():
                    trace_method_name = checker_state['debuggers_found'][debugger]['trace_alias']
                    if (
                        (hasattr(node.func, 'value') and node.func.value.id == debugger_info['alias']) or
                        (hasattr(node.func, 'id') and trace_method_name and node.func.id == trace_method_name)
                    ):
                        yield 'trace_used', debugger, debugger_info['alias'], debugger_info['trace_method'], debugger_info['trace_alias']
                        break


@flake8ext
def debugger_usage(logical_line, checker_state=None, noqa=None):
    if 'debuggers_found' not in checker_state:
        checker_state['debuggers_found'] = {}
    generator = check_for_debugger_import(logical_line, checker_state.copy())

    for import_type, item_imported, item_alias, trace_method, trace_alias in generator:
        if item_imported is not None:
            checker_state['debuggers_found'][item_imported] = {
                'alias': item_alias, 'trace_method': trace_method, 'trace_alias': trace_alias
            }
            if not noqa:
                yield 0, format_debugger_message(import_type, item_imported, item_alias, trace_method, trace_alias)

    if not noqa:
        generator = check_for_set_trace_usage(logical_line, checker_state.copy())
        for usage in generator:
            yield 0, format_debugger_message(*usage)
