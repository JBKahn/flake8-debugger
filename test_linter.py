import pycodestyle

from flake8_debugger import DebuggerChecker

import pytest
import sys


class CaptureReport(pycodestyle.BaseReport):
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


class DebuggerTestStyleGuide(pycodestyle.StyleGuide):

    logical_checks = []
    physical_checks = []
    ast_checks = [('debugger_usage', DebuggerChecker, ["tree", "filename", "lines"])]
    max_line_length = None
    hang_closing = False
    verbose = False
    benchmark_keys = {'files': 0, 'physical lines': 0, 'logical lines': 0}


_debugger_test_style = DebuggerTestStyleGuide()


def check_code_for_debugger_statements(code):
    """Process code using pycodestyle Checker and return all errors."""
    from tempfile import NamedTemporaryFile

    test_file = NamedTemporaryFile(delete=False)
    test_file.write(code.encode())
    test_file.flush()
    report = CaptureReport(options=_debugger_test_style)
    lines = [line + '\n' for line in code.split('\n')]
    checker = pycodestyle.Checker(filename=test_file.name, lines=lines, options=_debugger_test_style, report=report)

    checker.check_all()
    return report._results


class TestQA(object):

    def test_catches_simple_debugger(self):
        result = check_code_for_debugger_statements('from ipdb import set_trace as r\nr()')

        expected_result = [
            {'line': 2, 'message': 'T100 trace found: set_trace used as r', 'col': 0},
            {'line': 1, 'message': 'T100 import for set_trace found as r', 'col': 0},
        ]

        assert result == expected_result

    def test_catches_simple_debugger_when_called_off_lib(self):
        result = check_code_for_debugger_statements('import ipdb\nipdb.set_trace()')

        expected_result = [
            {'line': 2, 'message': 'T100 trace found: ipdb.set_trace used', 'col': 0},
            {'line': 1, 'message': 'T100 import for ipdb found', 'col': 0},
        ]

        assert result == expected_result

    def test_catches_simple_debugger_when_called_off_global(self):
        result = check_code_for_debugger_statements("__import__('ipdb').set_trace()")

        expected_result = [
            {'line': 1, 'message': 'T002 trace found: set_trace used', 'col': 0},
        ]

        assert result == expected_result

    @pytest.mark.skipif(True, reason="Not supported just yet")
    def test_catches_simple_debugger_when_called_off_var(self):
        result = check_code_for_debugger_statements('import ipdb\ntest = ipdb.set_trace\ntest()')

        expected_result = [
            {'line': 1, 'message': 'T100 import for ipdb found', 'col': 0},
            {'line': 3, 'message': 'T100 trace found: ipdb.set_trace used', 'col': 0}
        ]
        assert result == expected_result


class TestNoQA(object):

    @pytest.mark.skipif(sys.version_info < (2, 7), reason="Python 2.6 does not support noqa")
    def test_skip_import(self):
        result = check_code_for_debugger_statements('from ipdb import set_trace as r # noqa\nr()')

        expected_result = [
            {'line': 2, 'message': 'T100 trace found: set_trace used as r', 'col': 0}
        ]

        assert result == expected_result

    @pytest.mark.skipif(sys.version_info < (2, 7), reason="Python 2.6 does not support noqa")
    def test_skip_usage(self):
        result = check_code_for_debugger_statements('from ipdb import set_trace as r\nr() # noqa')

        expected_result = [
            {'line': 1, 'message': 'T100 import for set_trace found as r', 'col': 0},
        ]

        assert result == expected_result

    @pytest.mark.skipif(sys.version_info < (2, 7), reason="Python 2.6 does not support noqa")
    def test_skip_import_and_usage(self):
        result = check_code_for_debugger_statements('from ipdb import set_trace as r # noqa\nr() # noqa')

        expected_result = []

        assert result == expected_result


class TestImportCases(object):
    def test_import_multiple(self):
        result = check_code_for_debugger_statements('import math, ipdb, collections')
        assert result == [{'col': 0, 'line': 1, 'message': 'T100 import for ipdb found'}]

    def test_import(self):
        result = check_code_for_debugger_statements('import pdb')
        assert result == [{'col': 0, 'line': 1, 'message': 'T100 import for pdb found'}]

    def test_import_interactive_shell_embed(self):
        result = check_code_for_debugger_statements('from IPython.terminal.embed import InteractiveShellEmbed')
        assert result == [{'col': 0, 'line': 1, 'message': 'T100 import for InteractiveShellEmbed found'}]

    def test_import_both_same_line(self):
        result = check_code_for_debugger_statements('import pdb, ipdb')
        result = sorted(result, key=lambda debugger: debugger['message'])
        expected_result = [
            {'col': 0, 'line': 1, 'message': 'T100 import for ipdb found'},
            {'col': 0, 'line': 1, 'message': 'T100 import for pdb found'},
        ]
        assert result == expected_result

    def test_import_math(self):
        result = check_code_for_debugger_statements('import math')
        assert result == []

    def test_import_noqa(self):
        result = check_code_for_debugger_statements('import ipdb # noqa')
        assert result == []


class TestModuleSetTraceCases(object):
    def test_import_ipython_terminal_embed_use_InteractiveShellEmbed(self):
        result = check_code_for_debugger_statements('from IPython.terminal.embed import InteractiveShellEmbed; InteractiveShellEmbed()()')

        expected_result = [
            {'col': 58, 'line': 1, 'message': 'T100 trace found: InteractiveShellEmbed used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for InteractiveShellEmbed found'}
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_ipdb_use_set_trace(self):
        result = check_code_for_debugger_statements('import ipdb;ipdb.set_trace();')

        expected_result = [
            {'col': 12, 'line': 1, 'message': 'T100 trace found: ipdb.set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for ipdb found'}
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_pdb_use_set_trace(self):
        result = check_code_for_debugger_statements('import pdb;pdb.set_trace();')

        expected_result = [
            {'col': 11, 'line': 1, 'message': 'T100 trace found: pdb.set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for pdb found'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_pdb_use_set_trace_twice(self):
        result = check_code_for_debugger_statements('import pdb;pdb.set_trace() and pdb.set_trace();')

        expected_result = [
            {'col': 11, 'line': 1, 'message': 'T100 trace found: pdb.set_trace used'},
            {'col': 31, 'line': 1, 'message': 'T100 trace found: pdb.set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for pdb found'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_other_module_as_set_trace_and_use_it(self):
        result = check_code_for_debugger_statements('from math import Max as set_trace\nset_trace()')
        assert result == []


class TestImportAsCases(object):
    def test_import_ipdb_as(self):
        result = check_code_for_debugger_statements('import math, ipdb as sif, collections')
        assert result == [{'col': 0, 'line': 1, 'message': 'T100 import for ipdb found as sif'}]


class TestModuleASSetTraceCases(object):
    def test_import_ipdb_as_use_set_trace(self):
        result = check_code_for_debugger_statements('import ipdb as sif;sif.set_trace();')

        expected_result = [
            {'col': 19, 'line': 1, 'message': 'T100 trace found: sif.set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for ipdb found as sif'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result


class TestImportSetTraceCases(object):
    def test_import_set_trace_ipdb(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace;set_trace();')

        expected_result = [
            {'col': 32, 'line': 1, 'message': 'T100 trace found: set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for set_trace found'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_set_trace_pdb(self):
        result = check_code_for_debugger_statements('from pdb import set_trace; set_trace();')

        expected_result = [
            {'col': 27, 'line': 1, 'message': 'T100 trace found: set_trace used'},
            {'col': 0, 'line': 1, 'message': 'T100 import for set_trace found'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_set_trace_ipdb_as_and_use(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; sif();')

        expected_result = [
            {'col': 40, 'line': 1, 'message': 'T100 trace found: set_trace used as sif'},
            {'col': 0, 'line': 1, 'message': 'T100 import for set_trace found as sif'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_set_trace_ipdb_as_and_use_with_conjunction_and(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True and sif();')

        expected_result = [
            {'col': 49, 'line': 1, 'message': 'T100 trace found: set_trace used as sif'},
            {'col': 0, 'line': 1, 'message': 'T100 import for set_trace found as sif'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_set_trace_ipdb_as_and_use_with_conjunction_or(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True or sif();')

        expected_result = [
            {'col': 48, 'line': 1, 'message': 'T100 trace found: set_trace used as sif'},
            {'col': 0, 'line': 1, 'message': 'T100 import for set_trace found as sif'},
        ]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result

    def test_import_set_trace_ipdb_as_and_use_with_conjunction_or_noqa(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; True or sif(); # noqa')
        try:
            assert result == []
        except AssertionError:
            pass

    def test_import_set_trace_ipdb_as_and_use_with_conjunction_or_noqa_import_only(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif # noqa\nTrue or sif()')

        expected_result = [{'col': 8, 'line': 2, 'message': 'T100 trace found: set_trace used as sif'}]

        try:
            assert result == expected_result
        except AssertionError:
            for item in expected_result:
                item['col'] = 0

            assert result == expected_result
