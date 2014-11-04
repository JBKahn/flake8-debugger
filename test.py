from flake8_debugger import check_code_for_debugger_statements, format_debugger_message, DEBUGGER_ERROR_CODE
from nose.tools import assert_equal


class Flake8DebuggerTestCases(object):
    def generate_error_statement(self, line, col, item_type, item_found, name_used):
        return {
            'message': format_debugger_message(item_type, item_found, name_used),
            'line': line,
            'col': col
        }


class TestImportCases(Flake8DebuggerTestCases):
    def test_import_multiple(self):
        result = check_code_for_debugger_statements('import math, ipdb, collections')
        assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb')])

    def test_import(self):
        result = check_code_for_debugger_statements('import pdb')
        assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb')])


class TestModuleSetTraceCases(Flake8DebuggerTestCases):
    def test_import_ipdb_use_set_trace(self):
        result = check_code_for_debugger_statements('import ipdb;ipdb.set_trace();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                self.generate_error_statement(1, 12, 'set_trace', 'ipdb', 'set_trace')
            ]
        )

    def test_import_pdb_use_set_trace(self):
        result = check_code_for_debugger_statements('import pdb;pdb.set_trace();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                self.generate_error_statement(1, 11, 'set_trace', 'pdb', 'set_trace')
            ]
        )


class TestImportAsCases(Flake8DebuggerTestCases):
    def test_import_ipdb_as(self):
        result = check_code_for_debugger_statements('import math, ipdb as sif, collections')
        assert_equal(result, [self.generate_error_statement(1, 0, 'import', 'ipdb', 'sif')])


class TestModuleASSetTraceCases(Flake8DebuggerTestCases):
    def test_import_ipdb_as_use_set_trace(self):
        result = check_code_for_debugger_statements('import ipdb as sif;sif.set_trace();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'ipdb', 'sif'),
                self.generate_error_statement(1, 19, 'set_trace', 'ipdb', 'set_trace')
            ]
        )


class TestImportSetTraceCases(Flake8DebuggerTestCases):
    def test_import_set_trace_ipdb(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace;set_trace();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                self.generate_error_statement(1, 32, 'set_trace', 'debugger', 'set_trace')
            ]
        )

    def test_import_set_trace_pdb(self):
        result = check_code_for_debugger_statements('from pdb import set_trace; set_trace();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'pdb', 'pdb'),
                self.generate_error_statement(1, 27, 'set_trace', 'debugger', 'set_trace')
            ]
        )

    def test_import_set_trace_ipdb_as_and_use(self):
        result = check_code_for_debugger_statements('from ipdb import run, set_trace as sif; sif();')
        assert_equal(result,
            [
                self.generate_error_statement(1, 0, 'import', 'ipdb', 'ipdb'),
                self.generate_error_statement(1, 40, 'set_trace', 'debugger', 'sif')
            ]
        )
