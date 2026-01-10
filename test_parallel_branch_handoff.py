"""
Quick test to verify parallel branch handoff blocking works.
"""
from indusagi.tools import ToolRegistry
from indusagi.tools.handoff import handoff_to_agent, set_current_agency

# Create a mock agency
class MockAgency:
    pass

agency = MockAgency()
set_current_agency(agency)

# Test 1: Normal registry (should work)
print("Test 1: Normal registry handoff")
normal_registry = ToolRegistry()
result = handoff_to_agent(
    agent_name="Planner",
    message="Test message",
    tool_registry=normal_registry
)
print(f"Result: {result[:50]}...")
print(f"Pending handoff set: {normal_registry._pending_handoff is not None}")
print()

# Test 2: Parallel branch registry (should be blocked)
print("Test 2: Parallel branch handoff (should be blocked)")
branch_registry = normal_registry.fork(name="test-branch", is_parallel_branch=True)
print(f"Branch registry _is_parallel_branch: {branch_registry._is_parallel_branch}")
result = handoff_to_agent(
    agent_name="Coder",
    message="Test message from branch",
    tool_registry=branch_registry
)
print(f"Result: {result[:80]}...")
print(f"Pending handoff set: {branch_registry._pending_handoff is not None}")
print()

# Test 3: Verify the flag is set correctly
print("Test 3: Verify fork sets flag correctly")
fork1 = normal_registry.fork(name="fork1")
print(f"fork1 _is_parallel_branch: {fork1._is_parallel_branch}")
fork2 = normal_registry.fork(name="fork2", is_parallel_branch=False)
print(f"fork2 _is_parallel_branch: {fork2._is_parallel_branch}")
