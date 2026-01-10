"""
Test script for parallel agent execution feature.

This script tests the parallel handoff functionality where one agent
can fan out to multiple agents concurrently and aggregate their results.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API key is available
if not os.getenv("ANTHROPIC_API_KEY"):
    print("❌ Error: ANTHROPIC_API_KEY not found in environment")
    print("Please add it to your .env file")
    exit(1)

print("✓ API key found, creating agency...")

# Import after env check
from example_agency_improved_anthropic import create_development_agency

# Create the agency
agency = create_development_agency()

print("\n" + "="*80)
print("PARALLEL EXECUTION TEST")
print("="*80)

# Test 1: Simple parallel handoff to Planner and Critic
test_prompt = """
Run Planner + Critic in parallel:
- Planner: Create a spec for a simple calculator app (HTML/CSS/JS)
- Critic: List top 3 risks for a calculator app

After both complete, Coder should review both outputs and provide a summary.
"""

print("\n📝 Test Prompt:")
print(test_prompt)
print("\n" + "-"*80)
print("Starting parallel execution...")
print("-"*80 + "\n")

try:
    result = agency.process(
        test_prompt,
        use_tools=True,
        tools=agency.tools,
        tool_executor=agency.tool_executor
    )
    
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"\n✓ Final Agent: {result.final_agent}")
    print(f"✓ Total Time: {result.total_time:.2f}s")
    print(f"✓ Agents Used: {' → '.join(result.agents_used)}")
    print(f"✓ Total Handoffs: {len(result.handoffs)}")
    
    if result.parallel_results:
        print(f"\n✓ Parallel Executions: {len(result.parallel_results)}")
        for pr in result.parallel_results:
            status = "✓ Success" if pr.success else f"✗ Error: {pr.error}"
            print(f"  - {pr.agent}: {status} ({pr.processing_time:.2f}s)")
    
    print("\n" + "="*80)
    print("FINAL RESPONSE")
    print("="*80)
    print(result.response)
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("="*80)
    
    # Verify expected files were created
    import os
    expected_files = ["plan.md", "critic_report.md"]
    print("\n📁 Checking for expected files:")
    for file in expected_files:
        if os.path.exists(file):
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} NOT FOUND")
    
except Exception as e:
    print("\n" + "="*80)
    print("❌ TEST FAILED")
    print("="*80)
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
