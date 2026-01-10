"""Simple test to see if thread pool agents respond."""

import os
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set")
    exit(1)

from example_agency_improved_anthropic import create_development_agency

print("Creating agency with thread pool...")
agency = create_development_agency(
    use_thread_pool=True,
    thread_response_timeout=30  # 30 seconds for testing
)

print(f"Agency created. Isolated agents: {list(agency._isolated_agents.keys())}")
print(f"Handoff queue: {agency.handoff_queue}")

# Simple test: just ask Coder to do something simple (no handoff)
print("\n" + "="*80)
print("TEST 1: Simple request (no handoff)")
print("="*80)

try:
    result = agency.process(
        "Create a file called test.txt with content 'Hello World'",
        use_tools=True,
        tools=agency.tools,
        tool_executor=agency.tool_executor
    )
    print(f"\nSUCCESS! Response: {result.response[:200]}")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    agency.shutdown()
    print("\nAgency shut down.")
