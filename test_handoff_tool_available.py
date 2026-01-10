"""Quick test to verify handoff_to_agent tool is in the tools list."""

from example_agency_improved_anthropic import create_development_agency

agency = create_development_agency(use_thread_pool=True)

print("=" * 80)
print("TOOLS AVAILABLE TO AGENTS:")
print("=" * 80)

for i, tool in enumerate(agency.tools, 1):
    tool_name = tool.get("function", {}).get("name", "unknown")
    print(f"{i}. {tool_name}")
    if tool_name == "handoff_to_agent":
        print("   ✅ FOUND handoff_to_agent tool!")
        print(f"   Description: {tool.get('function', {}).get('description', 'N/A')[:100]}...")

print("\n" + "=" * 80)
print(f"Total tools: {len(agency.tools)}")
print("=" * 80)

# Check if handoff tool exists
handoff_exists = any(
    t.get("function", {}).get("name") == "handoff_to_agent" 
    for t in agency.tools
)

if handoff_exists:
    print("\n✅ SUCCESS: handoff_to_agent is registered and available")
else:
    print("\n❌ ERROR: handoff_to_agent is NOT in the tools list!")
