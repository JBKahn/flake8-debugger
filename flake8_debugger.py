"""Extension for flake8 that finds usage of the debugger."""
import ast


__version__ = '2.0.0'

DEBUGGER_ERROR_CODE = 'T002'


def flake8ext(f):
    """Decorate flake8 extension function."""
    f.name = 'flake8-debugger'
    f.version = __version__
    return f


def format_debugger_message(item_type, item_found, name_used):
    return '{0} {1} for {2} found as {3}'.format(DEBUGGER_ERROR_CODE, item_type, item_found, name_used)


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
                            yield 'import', debugger, node.names[index].asname or debugger
                        else:
                            yield 'import', debugger, node.module

            elif isinstance(node, ast.ImportFrom):
                trace_methods = debuggers.values()
                import ipdb; ipdb.set_trace()
                traces_found = set(filter(lambda trace: trace in module_names, trace_methods))
                if not traces_found:
                    continue
                for trace in traces_found:
                    trace_index = trace in module_names and module_names.index(trace)
                    if hasattr(node.names[trace_index], 'asname'):
                        yield 'import', node.module, node.module
                        yield 'set_trace', node.module, node.names[trace_index].asname or debuggers[node.module]


def check_for_set_trace_usage(logical_line, checker_state):
    for node in ast.walk(ast.parse(logical_line)):
        if isinstance(node, ast.Call):
            import ipdb; ipdb.set_trace()
            trace_methods = [checker_state['debuggers_found'][alias]['set_trace'] for alias in checker_state['debuggers_found'].keys()]
            if (getattr(node.func, 'attr', None) in trace_methods or getattr(node.func, 'id', None) in trace_methods):
                debugger_name = None
                for debugger in checker_state.keys():
                    trace_method_name = checker_state[debugger]['set_trace']
                    if (
                        (hasattr(node.func, 'value') and node.func.value.id == debugger) or
                        (hasattr(node.func, 'id') and trace_method_name and node.func.id == trace_method_name)
                    ):
                        debugger_name = debugger
                        break

                if not debugger_name:
                    debuggers_found = checker_state.keys()
                    if len(debuggers_found) == 1:
                        debugger_name = debuggers_found[0]
                    else:
                        debugger_name = 'debugger'
                set_trace_name = hasattr(node.func, 'attr') and node.func.attr or hasattr(node.func, 'id') and node.func.id
                yield debugger_name, set_trace_name


@flake8ext
def debugger_usage(logical_line, checker_state=None, noqa=None):
    if noqa:
        return
    if 'debuggers_found' not in checker_state:
        checker_state['debuggers_found'] = {}
    generator = check_for_debugger_import(logical_line, checker_state.copy())
    for type_found, item_imported, item_alias in generator:
        if item_imported is not None:
            previous_state = checker_state['debuggers_found'].get(item_alias, {})
            previous_state[type_found] = item_imported
            previous_state['set_trace'] = previous_state.get('set_trace', debuggers[item_imported])
            checker_state['debuggers_found'][item_alias] = previous_state
            yield 0, format_debugger_message(type_found, item_imported, item_alias)

    generator = check_for_set_trace_usage(logical_line, checker_state.copy())
    for set_trace_used, set_trace_alias in generator:
        if set_trace_used is not None:
            yield 0, format_debugger_message('trace method', set_trace_used, set_trace_alias)
