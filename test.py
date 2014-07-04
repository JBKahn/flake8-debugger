from flake8_debugger import check_debug_statements, DEBUGGER_ERROR_MESSAGE, DEBUGGER_ERROR_CODE
from nose.tools import assert_equal


class Flake8DebuggerTestCases(object):
    def generate_error_statement(self, index):
        return (index, '{} {}'.format(DEBUGGER_ERROR_CODE, DEBUGGER_ERROR_MESSAGE))


class TestGenericCases(Flake8DebuggerTestCases):
    def test_skips_noqa(self):
        result = check_debug_statements('44 print 4 # noqa')
        assert result is None

    def test_catches_simple_ipdb_import(self):
        result = check_debug_statements('import ipdb')
        assert_equal(result, self.generate_error_statement(0))

    def test_catches_simple_pdb_import(self):
        result = check_debug_statements('import pdb')
        assert_equal(result, self.generate_error_statement(0))

    def test_catches_simple_ipdb_set_trace(self):
        result = check_debug_statements('ipdb.set_trace();')
        assert_equal(result, self.generate_error_statement(0))

    def test_catches_simple_pdb_set_trace(self):
        result = check_debug_statements('pdb.set_trace();')
        assert_equal(result, self.generate_error_statement(0))


class TestCommentsPDB(Flake8DebuggerTestCases):
    def test_pdb_in_inline_comment_is_not_a_false_positive(self):
        result = check_debug_statements('# import pdb')
        assert result is None

    def test_pdb_same_line_as_comment(self):
        result = check_debug_statements('import pdb # what should I do with this ?')
        assert_equal(result, self.generate_error_statement(0))


class TestCommentsIPDB(Flake8DebuggerTestCases):
    def test_ipdb_in_inline_comment_is_not_a_false_positive(self):
        result = check_debug_statements('# import ipdb')
        assert result is None

    def test_ipdb_same_line_as_comment(self):
        result = check_debug_statements('import ipdb # what should I do with this ?')
        assert_equal(result, self.generate_error_statement(0))


class TestSingleQuotesPDB(Flake8DebuggerTestCases):
    def test_print_in_one_single_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a(\'import pdb\', 25)')
        assert result is None

    def test_print_in_between_two_one_single_quote_single_line_string(self):
        result = check_debug_statements('a(\'import pdb\' import pdb \'import pdb\', 25)')
        assert_equal(result, self.generate_error_statement(3))

    def test_print_in_three_single_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a(\'\'\'import pdb\'\'\', 25)')
        assert result is None

    def test_print_in_between_two_three_single_quote_single_line_string(self):
        result = check_debug_statements('a(\'\'\'import pdb\'\'\' import pdb \'\'\'import pdb\'\'\', 25)')
        assert_equal(result, self.generate_error_statement(3))


class TestSingleQuotesIPDB(Flake8DebuggerTestCases):
    def test_print_in_one_single_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a(\'import ipdb\', 25)')
        assert result is None

    def test_print_in_between_two_one_single_quote_single_line_string(self):
        result = check_debug_statements('a(\'import ipdb\' import ipdb \'import ipdb\', 25)')
        assert_equal(result, self.generate_error_statement(3))

    def test_print_in_three_single_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a(\'\'\'import ipdb\'\'\', 25)')
        assert result is None

    def test_print_in_between_two_three_single_quote_single_line_string(self):
        result = check_debug_statements('a(\'\'\'import ipdb\'\'\' import ipdb \'\'\'import ipdb\'\'\', 25)')
        assert_equal(result, self.generate_error_statement(3))


class TestDoubleQuotesPDB(Flake8DebuggerTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a("import pdb", 25)')
        assert result is None

    def test_print_in_between_two_one_double_quote_single_line_string(self):
        result = check_debug_statements('a("import pdb" import pdb "import pdb", 25)')
        assert_equal(result, self.generate_error_statement(3))

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a("""import pdb""", 25)')
        assert result is None

    def test_print_in_between_two_three_double_quote_single_line_string(self):
        result = check_debug_statements('a("import pdb" import pdb "import pdb", 25)')
        assert_equal(result, self.generate_error_statement(3))


class TestDoubleQuotesIPDB(Flake8DebuggerTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a("import ipdb", 25)')
        assert result is None

    def test_print_in_between_two_one_double_quote_single_line_string(self):
        result = check_debug_statements('a("import ipdb" import ipdb "import ipdb", 25)')
        assert_equal(result, self.generate_error_statement(3))

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_debug_statements('a("""import ipdb""", 25)')
        assert result is None

    def test_print_in_between_two_three_double_quote_single_line_string(self):
        result = check_debug_statements('a("import ipdb" import ipdb "import ipdb", 25)')
        assert_equal(result, self.generate_error_statement(3))
