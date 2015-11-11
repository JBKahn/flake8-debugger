import functools

from textwrap import dedent

try:
    from flake8 import pep8
except ImportError:
    import pep8

from flake8_debugger import debugger_usage

try:
    from unittest import skipIf
except ImportError:
    skipIf = None

from nose.tools import assert_equal, assert_true


if hasattr(pep8, 'BaseReport'):
    BaseReport = pep8.BaseReport
else:
    class BaseReport(object):
        def error(self, line_number, offset, text, check):
            code = text[0:4]
            return code


if hasattr(pep8, 'StyleGuide'):
    StyleGuide = pep8.StyleGuide
else:
    StyleGuide = object


class CaptureReport(BaseReport):
    """Collect the results of the checks."""

    def __init__(self, options):
        self._results = []
        super(CaptureReport, self).__init__(options)

    def error(self, line_number, offset, text, check):
        """Store each error."""
        code = super(CaptureReport, self).error(line_number, offset,
                                                text, check)
        if code:
            record = {
                'line': line_number,
                'col': offset,
                'message': '{0} {1}'.format(code, text[5:]),
            }
            self._results.append(record)
        return code


class PrintTestStyleGuide(StyleGuide):

    logical_checks = [
        ('debugger_usage', debugger_usage, ['logical_line', 'indent_level', 'checker_state', 'noqa']),
    ]
    physical_checks = []
    ast_checks = []
    max_line_length = None
    hang_closing = False
    verbose = False
    benchmark_keys = {'files': 0, 'physical lines': 0, 'logical lines': 0}


_print_test_style = PrintTestStyleGuide()
_inspect_checker = pep8.Checker('foo')

noqa_supported = hasattr(_inspect_checker, 'noqa')

if not noqa_supported:
    # remove noqa
    _print_test_style.logical_checks[0] = (
        'debugger_usage', debugger_usage, ['logical_line', 'checker_state'])


def old_pep8_message(report, text):
    """Capture old message."""
    filename, line_number, offset, error = text.split(':')
    line_number = int(line_number)
    offset = int(offset) - 1
    code = error[1:5]
    text = error[7:]
    report.error(line_number, offset, text, code)


def check_code_for_print_statements(code):
    """Process code using pep8 Checker and return all errors."""
    report = CaptureReport(options=_print_test_style)
    lines = [line + '\n' for line in code.split('\n')]
    if hasattr(pep8, 'options'):
        pep8.options = _print_test_style
        checker = pep8.Checker(lines=lines)
        pep8.message = functools.partial(old_pep8_message, report)
    else:
        checker = pep8.Checker(filename=None, lines=lines,
                               options=_print_test_style, report=report)


    checker.check_all()
    return report._results


class Flake8PrintTestCases(object):
    pass


if skipIf:
    skipIfUnsupported = functools.partial(
        skipIf,
        condition=not noqa_supported,
        reason='noqa is not supported on this flake8 version')
else:
    def skipIfUnsupported():
        def noop(*args, **kwargs):
            pass

        return noop

class TestNoQA(Flake8PrintTestCases):

    def test_catches_simple_print_python2(self):
        result = check_code_for_print_statements('from ipdb import set_trace as r\nr()')
        import ipdb; ipdb.set_trace()
        assert_equal(result, [{'col': 0, 'line': 1, 'message': 'T001 print statement found.'}])


#class TestImportCases(Flake8DebuggerTestCases):
    #def test_import_multiple(self):
        #result = check_code_for_debugger_statements('import math, ipdb, collections')
        #assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb')])

    #def test_import(self):
        #result = check_code_for_debugger_statements('import pdb')
        #assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb')])

    #def test_import_interactive_shell_embed(self):
        #result = check_code_for_debugger_statements('from IPython.terminal.embed import InteractiveShellEmbed')
        #assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'IPython.terminal.embed', 'IPython.terminal.embed')])

    #def test_import_both_same_line(self):
        #result = check_code_for_debugger_statements('import pdb, ipdb')
        #result = sorted(result, key=lambda debugger: debugger['message'])
        #assert_equal(
            #result,
            #[
                #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
            #]
        #)

    #def test_import_math(self):
        #result = check_code_for_debugger_statements('import math')
        #assert_equal(result, [])

    #def test_import_noqa(self):
        #result = check_code_for_debugger_statements('import ipdb # noqa')
        #assert_equal(result, [])


#class TestModuleSetTraceCases(Flake8DebuggerTestCases):
    #def test_import_ipython_terminal_embed_use_InteractiveShellEmbed(self):
        #result = check_code_for_debugger_statements('from IPython.terminal.embed import InteractiveShellEmbed; InteractiveShellEmbed()()')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'IPython.terminal.embed', 'IPython.terminal.embed'),
                    #self.generate_error_statement(1, 58, 'trace method', 'IPython.terminal.embed', 'InteractiveShellEmbed')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'IPython.terminal.embed', 'IPython.terminal.embed'),
                    #self.generate_error_statement(1, 79, 'trace method', 'IPython.terminal.embed', 'InteractiveShellEmbed')
                #]
            #)

    #def test_import_ipdb_use_set_trace(self):
        #result = check_code_for_debugger_statements('import ipdb;ipdb.set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 12, 'trace method', 'ipdb', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 26, 'trace method', 'ipdb', 'set_trace')
                #]
            #)

    #def test_import_pdb_use_set_trace(self):
        #result = check_code_for_debugger_statements('import pdb;pdb.set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 11, 'trace method', 'pdb', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 24, 'trace method', 'pdb', 'set_trace')
                #]
            #)

    #def test_import_pdb_use_set_trace_twice(self):
        #result = check_code_for_debugger_statements('import pdb;pdb.set_trace() and pdb.set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 11, 'trace method', 'pdb', 'set_trace'),
                    #self.generate_error_statement(1, 31, 'trace method', 'pdb', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 24, 'trace method', 'pdb', 'set_trace'),
                    #self.generate_error_statement(1, 44, 'trace method', 'pdb', 'set_trace')
                #]
            #)

    #def test_import_other_module_as_set_trace_and_use_it(self):
        #result = check_code_for_debugger_statements('from math import Max as set_trace\nset_trace()')
        #assert_equal(
            #result,
            #[]
        #)


#class TestImportAsCases(Flake8DebuggerTestCases):
    #def test_import_ipdb_as(self):
        #result = check_code_for_debugger_statements('import math, ipdb as sif, collections')
        #assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'ipdb', 'sif')])


#class TestModuleASSetTraceCases(Flake8DebuggerTestCases):
    #def test_import_ipdb_as_use_set_trace(self):
        #result = check_code_for_debugger_statements('import ipdb as sif;sif.set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'sif'),
                    #self.generate_error_statement(1, 19, 'trace method', 'sif', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'sif'),
                    #self.generate_error_statement(1, 32, 'trace method', 'sif', 'set_trace')
                #]
            #)


#class TestImportSetTraceCases(Flake8DebuggerTestCases):
    #def test_import_set_trace_ipdb(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace;set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 32, 'trace method', 'ipdb', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 41, 'trace method', 'ipdb', 'set_trace')
                #]
            #)

    #def test_import_set_trace_pdb(self):
        #result = check_code_for_debugger_statements('from pdb import set_trace; set_trace();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 27, 'trace method', 'pdb', 'set_trace')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                    #self.generate_error_statement(1, 36, 'trace method', 'pdb', 'set_trace')
                #]
            #)

    #def test_import_set_trace_ipdb_as_and_use(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; sif();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 40, 'trace method', 'ipdb', 'sif')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 43, 'trace method', 'ipdb', 'sif')
                #]
            #)

    #def test_import_set_trace_ipdb_as_and_use_with_conjunction_and(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True and sif();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 49, 'trace method', 'ipdb', 'sif')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 52, 'trace method', 'ipdb', 'sif')
                #]
            #)

    #def test_import_set_trace_ipdb_as_and_use_with_conjunction_or(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True or sif();')
        #try:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 48, 'trace method', 'ipdb', 'sif')
                #]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[
                    #self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                    #self.generate_error_statement(1, 51, 'trace method', 'ipdb', 'sif')
                #]
            #)

    #def test_import_set_trace_ipdb_as_and_use_with_conjunction_or_noqa(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True or sif(); # noqa')
        #try:
            #assert_equal(
                #result,
                #[]
            #)
        #except AssertionError:
            #pass

    #def test_import_set_trace_ipdb_as_and_use_with_conjunction_or_noqa_import_only(self):
        #result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif # noqa\nTrue or sif()')
        #try:
            #assert_equal(
                #result,
                #[self.generate_error_statement(2, 8, 'trace method', 'ipdb', 'sif')]
            #)
        #except AssertionError:
            #assert_equal(
                #result,
                #[self.generate_error_statement(2, 11, 'trace method', 'ipdb', 'sif')]
            #)
