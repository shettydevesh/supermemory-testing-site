"""
Test script for the General Question Analyzer
Tests both accuracy and performance
"""

import time
from general_question_analyzer import get_analyzer


def test_accuracy():
    """Test the accuracy of the analyzer on various inputs."""
    analyzer = get_analyzer()

    # Test cases: (query, expected_is_general)
    test_cases = [
        # General greetings - should be detected
        ("hi", True),
        ("hello", True),
        ("hey", True),
        ("Hi!", True),
        ("HELLO", True),
        ("heyyyy", True),
        ("hey there", True),
        ("hello friend", True),

        # Well-being questions - should be detected
        ("how are you", True),
        ("how are you doing", True),
        ("what's up", True),
        ("how's it going", True),
        ("How are you?", True),

        # Identity questions - should be detected
        ("who are you", True),
        ("what are you", True),
        ("what's your name", True),
        ("tell me about yourself", True),

        # Knowledge queries - should NOT be detected
        ("what is the weather", False),
        ("tell me about machine learning", False),
        ("how does photosynthesis work", False),
        ("where is the documentation", False),
        ("explain quantum computing", False),
        ("what are the benefits of exercise", False),
        ("find information about Python", False),
        ("search for API documentation", False),

        # Edge cases
        ("", False),  # Empty
        ("  ", False),  # Whitespace only
        ("a", False),  # Single character
        ("?", False),  # Just punctuation
    ]

    passed = 0
    failed = 0
    failures = []

    print("Testing Analyzer Accuracy")
    print("=" * 60)

    for query, expected_is_general in test_cases:
        is_general, response = analyzer.analyze(query)

        if is_general == expected_is_general:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"
            failures.append((query, expected_is_general, is_general))

        print(f"{status}: '{query}' → is_general={is_general} (expected={expected_is_general})")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failures:
        print("\nFailed Test Cases:")
        for query, expected, actual in failures:
            print(f"  '{query}': expected {expected}, got {actual}")

    return failed == 0


def test_performance():
    """Test the performance of the analyzer."""
    analyzer = get_analyzer()

    test_queries = [
        "hi",
        "how are you",
        "what is machine learning",
        "explain the benefits of exercise",
        "hey there how are you doing today",
    ]

    print("\n" + "=" * 60)
    print("Testing Analyzer Performance")
    print("=" * 60)

    # Warm-up run (first call might be slower due to Python internals)
    for query in test_queries:
        analyzer.analyze(query)

    # Actual performance test
    iterations = 1000
    results = {}

    for query in test_queries:
        start_time = time.perf_counter()

        for _ in range(iterations):
            analyzer.analyze(query)

        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / iterations) * 1000

        results[query] = avg_time_ms
        print(f"Query: '{query}'")
        print(f"  Average time: {avg_time_ms:.4f} ms over {iterations} iterations")

    print("\n" + "=" * 60)
    overall_avg = sum(results.values()) / len(results)
    print(f"Overall average time: {overall_avg:.4f} ms")

    if overall_avg < 1.0:
        print("✓ Performance target achieved (< 1 ms)")
    else:
        print("⚠ Performance target not achieved (goal: < 1 ms)")

    return overall_avg < 1.0


def test_response_variety():
    """Test that responses vary to avoid repetition."""
    analyzer = get_analyzer()

    print("\n" + "=" * 60)
    print("Testing Response Variety")
    print("=" * 60)

    test_query = "hi"
    responses = []

    for i in range(5):
        _, response = analyzer.analyze(test_query)
        responses.append(response)
        print(f"Response {i+1}: {response}")

    unique_responses = len(set(responses))
    print(f"\nUnique responses: {unique_responses} out of {len(responses)}")

    if unique_responses > 1:
        print("✓ Response variety confirmed")
        return True
    else:
        print("✗ No response variety detected")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GENERAL QUESTION ANALYZER TEST SUITE")
    print("=" * 60 + "\n")

    accuracy_pass = test_accuracy()
    performance_pass = test_performance()
    variety_pass = test_response_variety()

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Accuracy Test: {'✓ PASSED' if accuracy_pass else '✗ FAILED'}")
    print(f"Performance Test: {'✓ PASSED' if performance_pass else '✗ FAILED'}")
    print(f"Variety Test: {'✓ PASSED' if variety_pass else '✗ FAILED'}")

    if accuracy_pass and performance_pass and variety_pass:
        print("\n🎉 All tests passed! The analyzer is ready for production.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
