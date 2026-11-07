"""Shared helper so every test records its input, expected result, and actual result."""


def check(test_case, label, given, expected, actual):
    """Print an input/expected/actual line, then assert they match."""
    status = "PASS" if expected == actual else "FAIL"
    print(f"\n  [{status}] {label}\n      input:    {given}\n      expected: {expected}\n      actual:   {actual}")
    test_case.assertEqual(expected, actual, label)
