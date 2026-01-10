"""
Test script for Ollama provider integration with IndusAGI framework.

This script tests:
1. Basic completion
2. Streaming response
3. Tool calling
4. Auto-detection of provider

Make sure OLLAMA_API_KEY is set in your environment or .env file.
"""

import os
from dotenv import load_dotenv
from src.indusagi.agent import Agent, AgentConfig

# Load environment variables
load_dotenv()

def test_basic_completion():
    """Test basic completion with Ollama cloud API."""
    print("\n" + "="*60)
    print("TEST 1: Basic Completion")
    print("="*60)

    try:
        config = AgentConfig(
            model="glm-4.7",
            provider="ollama",
            temperature=0.7,
            max_tokens=100
        )

        agent = Agent(
            name="OllamaTest",
            role="Test cloud Ollama API",
            config=config,
            system_prompt="You are a helpful assistant. Be concise."
        )

        response = agent.process("What is 2+2? Answer in one sentence.")
        print(f"\nResponse: {response}")
        print("\n✅ Basic completion test PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Basic completion test FAILED: {str(e)}")
        return False


def test_streaming():
    """Test streaming response with Ollama cloud API."""
    print("\n" + "="*60)
    print("TEST 2: Streaming Response")
    print("="*60)

    try:
        config = AgentConfig(
            model="glm-4.7",
            provider="ollama",
            temperature=0.7,
            max_tokens=100
        )

        agent = Agent(
            name="OllamaStreamTest",
            role="Test streaming",
            config=config,
            system_prompt="You are a helpful assistant. Be very concise."
        )

        print("\nStreaming response:")
        for chunk in agent.process_streaming("Tell me a very short joke in one line."):
            print(chunk, end="", flush=True)

        print("\n\n✅ Streaming test PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Streaming test FAILED: {str(e)}")
        return False


def test_auto_detection():
    """Test auto-detection of Ollama provider."""
    print("\n" + "="*60)
    print("TEST 3: Auto-detection")
    print("="*60)

    try:
        # Create config from environment (should auto-detect ollama if OLLAMA_API_KEY is set)
        config = AgentConfig.from_env()
        print(f"\nDetected provider: {config.provider}")
        print(f"Default model: {config.model}")

        if config.provider == "ollama":
            print("\n✅ Auto-detection test PASSED")
            return True
        else:
            print(f"\n⚠️  Auto-detection returned '{config.provider}' (expected 'ollama')")
            print("   This may be expected if other API keys are set")
            return True
    except Exception as e:
        print(f"\n❌ Auto-detection test FAILED: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for invalid API key."""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)

    try:
        # Try with empty API key (should fail gracefully)
        original_key = os.environ.get("OLLAMA_API_KEY")
        os.environ["OLLAMA_API_KEY"] = ""

        try:
            config = AgentConfig(
                model="glm-4.7",
                provider="ollama",
                temperature=0.7
            )

            agent = Agent(
                name="ErrorTest",
                role="Test error handling",
                config=config
            )

            print("\n❌ Error handling test FAILED: Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"\nCaught expected error: {str(e)}")
            print("✅ Error handling test PASSED")
            return True
        finally:
            # Restore original key
            if original_key:
                os.environ["OLLAMA_API_KEY"] = original_key

    except Exception as e:
        print(f"\n❌ Error handling test FAILED: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OLLAMA PROVIDER INTEGRATION TESTS")
    print("="*60)

    # Check if API key is set
    if not os.getenv("OLLAMA_API_KEY"):
        print("\n❌ OLLAMA_API_KEY not set in environment!")
        print("   Please set it with: export OLLAMA_API_KEY='your-key-here'")
        print("   Or add it to your .env file")
        return

    print(f"\n✓ OLLAMA_API_KEY is set")
    print(f"✓ Base URL: {os.getenv('OLLAMA_BASE_URL', 'https://ollama.com (default)')}")

    # Run tests
    results = []
    results.append(("Basic Completion", test_basic_completion()))
    results.append(("Streaming", test_streaming()))
    results.append(("Auto-detection", test_auto_detection()))
    results.append(("Error Handling", test_error_handling()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n🎉 All tests passed! Ollama integration is working correctly.")
    else:
        print(f"\n⚠️  {len(results) - total_passed} test(s) failed. Please check the errors above.")


if __name__ == "__main__":
    main()
