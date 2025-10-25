# test_integration.py - Integration script for testing your SPL parser

import sys
import os

# Add current directory to path so we can import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def convert_lexer_token_to_parser_string(token):
    """Convert a lexer Token to a string the parser expects"""
    # For identifiers, numbers, and strings, use the token type name
    if token.type == "IDENT":
        return "IDENT"
    elif token.type == "NUMBER":
        return "NUMBER"
    elif token.type == "STRING":
        return "STRING"
    else:
        # For keywords and symbols, use the actual token value
        return token.value


def parse_spl_source(source_code):
    """Parse SPL source code using your lexer and parser"""
    try:
        # Import your modules
        from lexer import Lexer, LexerError
        from parser import SLRParser, build_spl_grammar

        print(f"Input source ({len(source_code)} chars):")
        print("-" * 40)
        print(source_code.strip())
        print("-" * 40)

        # Tokenize
        try:
            lexer = Lexer(source_code)
            tokens = list(lexer)
            print(f"\n✅ Lexing successful - {len(tokens)} tokens:")
            for i, token in enumerate(tokens):
                print(f"  {i:2d}: {token}")
        except LexerError as e:
            print(f"❌ Lexer error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected lexer error: {e}")
            return False

        # Convert to parser format
        parser_tokens = [
            convert_lexer_token_to_parser_string(token) for token in tokens
        ]
        print(f"\nConverted tokens for parser: {parser_tokens}")

        # Parse
        try:
            grammar = build_spl_grammar()
            parser = SLRParser(grammar)
            print(f"\n🔄 Starting parse...")

            result = parser.parse(parser_tokens)
            print(f"Parse result: {'✅ SUCCESS' if result else '❌ FAILED'}")
            return result

        except Exception as e:
            print(f"❌ Parser error: {e}")
            import traceback

            traceback.print_exc()
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure lexer.py and Parser.py are in the same directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_individual_program(name, source_code):
    """Test a single program"""
    print("=" * 80)
    print(f"TEST: {name}")
    print("=" * 80)

    result = parse_spl_source(source_code)

    print(f"\n🏁 Final result: {'✅ PASS' if result else '❌ FAIL'}")
    return result


def run_selected_tests():
    """Run a selection of key tests"""

    # Import the test programs
    from spl_test_programs import get_test_programs, get_edge_case_tests

    # Select key tests to run
    all_tests = get_test_programs()
    edge_tests = get_edge_case_tests()

    selected_tests = {
        # Basic tests
        "minimal_program": all_tests["minimal_program"],
        "simple_variable_program": all_tests["simple_variable_program"],
        # Expression tests
        "arithmetic_expressions": all_tests["arithmetic_expressions"],
        # Control flow
        "if_statement": all_tests["if_statement"],
        "while_loop": all_tests["while_loop"],
        # Procedures and functions
        "simple_procedure": all_tests["simple_procedure"],
        "simple_function": all_tests["simple_function"],
        # Edge cases
        "empty_sections": edge_tests["empty_sections"],
        "max_parameters": edge_tests["max_parameters"],
    }

    results = {}

    print("🧪 RUNNING SELECTED SPL PARSER TESTS")
    print("=" * 80)

    for test_name, source_code in selected_tests.items():
        try:
            result = test_individual_program(test_name, source_code)
            results[test_name] = result
            print("\n" + "⏸️ " * 20 + "\n")  # Separator between tests
        except KeyboardInterrupt:
            print("\n❌ Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Final summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print("-" * 80)
    print(f"Results: {passed}/{total} passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed!")
    elif passed > total * 0.7:
        print("👍 Most tests passed - good progress!")
    else:
        print("🔧 Several tests failed - check the issues above")

    return results


def quick_test():
    """Run a single simple test to verify everything is working"""

    simple_program = """
    glob { }
    proc { }
    func { }
    main {
        var { x }
        x = 42;
        print x
    }
    """

    print("🚀 QUICK TEST")
    return test_individual_program("quick_test", simple_program)


def main():
    """Main function - choose what to run"""

    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1] == "selected":
            run_selected_tests()
        elif sys.argv[1] == "all":
            from spl_test_programs import get_test_programs, run_test_suite

            run_test_suite(parse_spl_source)
        else:
            print("Usage: python test_integration.py [quick|selected|all]")
    else:
        print("SPL Parser Test Integration")
        print("Options:")
        print("  python test_integration.py quick     - Run one simple test")
        print("  python test_integration.py selected  - Run key tests")
        print("  python test_integration.py all       - Run all tests")
        print("\nRunning quick test by default...")
        quick_test()


if __name__ == "__main__":
    main()
