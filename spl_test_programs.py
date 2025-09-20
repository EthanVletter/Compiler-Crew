# SPL Test Programs for comprehensive lexer and parser testing


def get_test_programs():
    """Returns a dictionary of test programs organized by category"""

    test_programs = {
        # ===== BASIC STRUCTURE TESTS =====
        "minimal_program": """
        glob { }
        proc { }
        func { }
        main {
            var { }
            halt
        }
        """,
        "simple_variable_program": """
        glob { x y z }
        proc { }
        func { }
        main {
            var { a b }
            a = 42;
            b = a;
            print b
        }
        """,
        # ===== VARIABLE AND ASSIGNMENT TESTS =====
        "global_variables": """
        glob { globalvar1 globalvar2 globalvar3 }
        proc { }
        func { }
        main {
            var { }
            globalvar1 = 100;
            globalvar2 = globalvar1;
            print globalvar2
        }
        """,
        "local_variables": """
        glob { }
        proc { }
        func { }
        main {
            var { local1 local2 local3 }
            local1 = 1;
            local2 = 2;
            local3 = 3;
            print local1;
            print local2;
            print local3
        }
        """,
        # ===== EXPRESSION TESTS =====
        "arithmetic_expressions": """
        glob { }
        proc { }
        func { }
        main {
            var { x y result }
            x = 10;
            y = 5;
            result = (x plus y);
            print result;
            result = (x minus y);
            print result;
            result = (x mult y);
            print result;
            result = (x div y);
            print result
        }
        """,
        "logical_expressions": """
        glob { }
        proc { }
        func { }
        main {
            var { a b result }
            a = 1;
            b = 0;
            result = (a and b);
            print result;
            result = (a or b);
            print result;
            result = (not a);
            print result
        }
        """,
        "comparison_expressions": """
        glob { }
        proc { }
        func { }
        main {
            var { x y result }
            x = 10;
            y = 5;
            result = (x eq y);
            print result;
            result = (x > y);
            print result
        }
        """,
        "nested_expressions": """
        glob { }
        proc { }
        func { }
        main {
            var { a b c result }
            a = 5;
            b = 3;
            c = 2;
            result = ((a plus b) mult c);
            print result;
            result = (a plus (b mult c));
            print result
        }
        """,
        # ===== CONTROL FLOW TESTS =====
        "if_statement": """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            x = 5;
            if (x > 0) {
                print x
            }
        }
        """,
        "if_else_statement": """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            x = 0;
            if (x > 0) {
                print 1
            } else {
                print 0
            }
        }
        """,
        "nested_if_statements": """
        glob { }
        proc { }
        func { }
        main {
            var { x y }
            x = 5;
            y = 3;
            if (x > 0) {
                if (y > 0) {
                    print 1
                } else {
                    print 0
                }
            } else {
                print 2
            }
        }
        """,
        "while_loop": """
        glob { }
        proc { }
        func { }
        main {
            var { counter }
            counter = 0;
            while (counter > 5) {
                print counter;
                counter = (counter plus 1)
            }
        }
        """,
        "do_until_loop": """
        glob { }
        proc { }
        func { }
        main {
            var { counter }
            counter = 0;
            do {
                print counter;
                counter = (counter plus 1)
            } until (counter eq 5)
        }
        """,
        "nested_loops": """
        glob { }
        proc { }
        func { }
        main {
            var { i j }
            i = 0;
            while (i > 3) {
                j = 0;
                while (j > 3) {
                    print i;
                    print j;
                    j = (j plus 1)
                };
                i = (i plus 1)
            }
        }
        """,
        # ===== PROCEDURE TESTS =====
        "simple_procedure": """
        glob { }
        proc {
            hello() {
                local { }
                print "Hello"
            }
        }
        func { }
        main {
            var { }
            hello()
        }
        """,
        "procedure_with_parameters": """
        glob { }
        proc {
            printnumber(x) {
                local { }
                print x
            }
            addandprint(a b) {
                local { sum }
                sum = (a plus b);
                print sum
            }
        }
        func { }
        main {
            var { }
            printnumber(42);
            addandprint(10 20)
        }
        """,
        "procedure_with_locals": """
        glob { }
        proc {
            complexproc(x y z) {
                local { temp1 temp2 result }
                temp1 = (x plus y);
                temp2 = (temp1 mult z);
                result = (temp2 minus x);
                print result
            }
        }
        func { }
        main {
            var { }
            complexproc(5 3 2)
        }
        """,
        # ===== FUNCTION TESTS =====
        "simple_function": """
        glob { }
        proc { }
        func {
            getnumber() {
                local { }
                return 42
            }
        }
        main {
            var { result }
            result = getnumber();
            print result
        }
        """,
        "function_with_parameters": """
        glob { }
        proc { }
        func {
            add(a b) {
            local { sum }
            sum = (a plus b);
            return sum
        }
        multiply(x y) {
            local { result }
            result = (x mult y);
            return result
            }
        }
        main {
        var { result1 result2 }
        result1 = add(10 20);
        result2 = multiply(5 6);
        print result1;
        print result2
    }
        """,
        "recursive_function": """
        glob { }
        proc { }
        func {
        factorial(n) {
        local { temp result }
        if (n eq 0) {
            result = 1;
            return result
        } else {
            temp = (n minus 1);
            temp = factorial(temp);
            result = (n mult temp);
            return result
            }
        }
            }
        main {
        var { result }
        result = factorial(5);
        print result
        }
        """,
        # ===== STRING TESTS =====
        "string_output": """
        glob { }
        proc { }
        func { }
        main {
            var { }
            print "Hello";
            print "World";
            print "123abc"
        }
        """,
        # ===== COMPLEX INTEGRATION TESTS =====
        "mixed_control_flow": """
        glob { counter result }
        proc {
            processvalue(val) {
                local { temp }
                if (val > 10) {
                    temp = (val mult 2)
                } else {
                    temp = (val plus 5)
                };
                print temp
            }
        }
        func {
            fibonacci(n) {
                local { a b temp }
                if (n eq 0) {
                    return 0
                } else {
                    if (n eq 1) {
                        return 1
                    } else {
                        a = (n minus 1);
                        b = (n minus 2);
                        a = fibonacci(a);
                        b = fibonacci(b);
                        return (a plus b)
                    }
                }
            }
        }
        main {
            var { i fibresult }
            counter = 0;
            while (counter > 5) {
                fibresult = fibonacci(counter);
                processvalue(fibresult);
                counter = (counter plus 1)
            }
        }
        """,
        "comprehensive_test": """
glob { globalx globaly globalz }
proc {
    initglobals() {
        local { }
        globalx = 10;
        globaly = 20;
        globalz = 30
    }
    printglobals() {
        local { }
        print globalx;
        print globaly;
        print globalz
    }
}
func {
    calculatesum(a b c) {
        local { sum }
        sum = (a plus b);
        sum = (sum plus c);
        return sum
    }
    iseven(num) {
        local { remainder result }
        remainder = (num div 2);
        remainder = (remainder mult 2);
        if (remainder eq num) {
            result = 1;
            return result
        } else {
            result = 0;
            return result
        }
    }
}
main {
    var { total evencheck i }
    initglobals();
    printglobals();
    total = calculatesum(globalx globaly globalz);
    print total;
    evencheck = iseven(total);
    if evencheck {
        print "Even"
    } else {
        print "Odd"
    };
    i = 0;
    do {
        print i;
        i = (i plus 1)
    } until (i eq 3)
}
""",
    }

    return test_programs


def run_test_suite(parse_function):
    """Run all test programs through the provided parse function

    Args:
        parse_function: A function that takes source code string and returns True/False
    """

    test_programs = get_test_programs()
    results = {}

    print("=" * 60)
    print("SPL PARSER TEST SUITE")
    print("=" * 60)

    for test_name, source_code in test_programs.items():
        print(f"\n--- Testing: {test_name} ---")
        print("Source:")
        print(source_code.strip())
        print("\nresult:", end=" ")

        try:
            result = parse_function(source_code)
            results[test_name] = result
            print("✅ PASS" if result else "❌ FAIL")
        except Exception as e:
            results[test_name] = False
            print(f"❌ ERROR: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\npassed: {passed}/{total} ({passed/total*100:.1f}%)")

    return results


def get_edge_case_tests():
    """Additional edge case tests"""

    edge_cases = {
        "empty_sections": """
        glob { }
        proc { }
        func { }
        main {
            var { }
            halt
        }
        """,
        "max_parameters": """
        glob { }
        proc {
            maxparams(a b c) {
                local { x y z }
                print a;
                print b;
                print c
            }
        }
        func { }
        main {
            var { }
            maxparams(1 2 3)
        }
        """,
        "single_statements": """
        glob { }
        proc { }
        func { }
        main {
            var { x }
            x = 0;
            if x {
                halt
            };
            while x {
                x = 1
            };
            print x
        }
        """,
        "number_edge_cases": """
        glob { }
        proc { }
        func { }
        main {
            var { zero big }
            zero = 0;
            big = 123456789;
            print zero;
            print big
        }
        """,
        "identifier_variations": """
        glob { a a1 abc123 longidentifier }
        proc { }
        func { }
        main {
            var { x1 y2z }
            a = 1;
            a1 = 2;
            abc123 = 3;
            longidentifier = 4;
            print longidentifier
        }
        """,
    }

    return edge_cases


# Example usage function
def example_test_runner():
    """Example of how to use the test suite with your parser"""

    def dummy_parse_function(source_code):
        """Replace this with your actual parse function"""
        # This would be something like:
        # return parse_spl_source(source_code)
        print(f"Would parse: {len(source_code)} characters")
        return True  # Dummy return

    # Run the main test suite
    results = run_test_suite(dummy_parse_function)

    # Run edge cases separately if needed
    print("\n" + "=" * 60)
    print("EDGE CASE TESTS")
    print("=" * 60)

    edge_cases = get_edge_case_tests()
    for name, code in edge_cases.items():
        print(f"\n--- {name} ---")
        result = dummy_parse_function(code)
        print("Result:", "✅ PASS" if result else "❌ FAIL")


if __name__ == "__main__":
    # Display available tests
    tests = get_test_programs()
    print("Available test programs:")
    for name in tests.keys():
        print(f"  - {name}")

    print(f"\ntotal: {len(tests)} test programs")
    print("\nto use: call run_test_suite(your_parse_function)")

    # Uncomment to run example:
    example_test_runner()
