# Parallel Execution Improvements Summary

## Date: 2026-01-11

## Overview
Improved the parallel agent execution feature with clearer logging, better error handling, and prevention of nested handoffs in parallel branches.

## Issues Identified from User Log

From the user's provided `log.md`, the following issues were identified:

1. **No visible parallel execution indicators**: The console output didn't show clear "PARALLEL START" or "PARALLEL END" messages
2. **Agent confusion**: The Planner agent incorrectly created `critic-report.md` instead of only creating `plan.md`
3. **Flow stalling**: The parallel execution didn't properly return to the Coder for aggregation
4. **Nested handoffs**: Parallel branches could still call `handoff_to_agent`, causing confusion
5. **Windows command errors**: The Coder agent had issues with `mkdir` commands on Windows PowerShell

## Fixes Implemented

### 1. Enhanced Parallel Execution Logging (`src/indusagi/agency.py`)

Added clear, visually distinct console output for parallel execution stages:

- **Parallel Start**: Shows a bordered box with:
  - From Agent
  - Target Agents
  - Message preview
  
- **Branch Start**: Shows "▶ Starting parallel branch: [Agent]"

- **Branch End**: Shows "✓ Completed parallel branch: [Agent] (time)" with color-coded success/error

- **Parallel End**: Shows a summary table with:
  - Agent name
  - Status (✓ Success or ✗ Error)
  - Duration
  
- **Aggregation**: Shows "→ Aggregating results in: [Agent]"

**Example Output:**
```
╔══════════════════════════════════ PARALLEL EXECUTION START ══════════════════════════════════╗
║ From Agent: Coder
║ Target Agents: Planner, Critic
║ Message: Create a comprehensive specification for a Todo App...
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

▶ Starting parallel branch: Planner
▶ Starting parallel branch: Critic
✓ Completed parallel branch: Critic (2.5s)
✓ Completed parallel branch: Planner (3.1s)

╔════════════════════════════════ PARALLEL EXECUTION COMPLETE ═════════════════════════════════╗
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Agent    ┃   Status   ┃ Duration ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Planner  │ ✓ Success  │   3.10s  │
│ Critic   │ ✓ Success  │   2.50s  │
└──────────┴────────────┴──────────┘
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

→ Aggregating results in: Coder
```

### 2. Prevented Nested Handoffs in Parallel Branches

**Changes to `src/indusagi/tools/__init__.py`:**
- Added `_is_parallel_branch` flag to `ToolRegistry`
- Modified `fork()` method to mark forked registries as parallel branches
- Parallel branches are now isolated and cannot initiate handoffs

**Changes to `src/indusagi/tools/handoff.py`:**
- Added check for `_is_parallel_branch` flag
- Returns clear error message if handoff is attempted in a parallel branch:
  ```
  ⚠️ Handoff not allowed: You are running in a parallel branch.
  Parallel branches cannot initiate handoffs.
  Complete your assigned task and return results to the aggregator agent.
  ```

**Changes to `src/indusagi/agency.py`:**
- Added warning message when a parallel branch attempts a nested handoff
- Clears pending handoffs from branches after completion

### 3. Clarified Agent Responsibilities in Prompts

**Updated `example_agency_improved_anthropic_prompts/planner_instructions.md`:**
- Added critical warning at the top about file naming
- Emphasized that Planner ONLY creates `plan.md`
- Added explicit prohibition against creating `critic_report.md` or `critic-report.md`
- Strengthened the "Available tools" section with clear warnings

**Updated `example_agency_improved_anthropic_prompts/critic_instructions.md`:**
- Added critical warning at the top about file naming
- Emphasized that Critic ONLY creates `critic_report.md`
- Added explicit prohibition against creating `plan.md`

### 4. Created Test Script

**New file: `test_parallel_execution.py`**
- Automated test for parallel execution
- Tests Planner + Critic parallel handoff
- Verifies expected files are created
- Shows clear test results and timing

## How to Test

Run the test script:
```bash
python test_parallel_execution.py
```

Or run the interactive demo:
```bash
python example_agency_improved_anthropic.py
```

Then try this prompt:
```
Run Planner + Critic in parallel: Planner drafts a spec for a todo app; 
Critic lists top risks. Then merge - critic should create report md file 
and planner generate plan.md. After all that done, coder generates that 
application in html and css in a specific folder.
```

## Expected Behavior

1. **Coder receives request** and decides to fan out to Planner + Critic in parallel
2. **Parallel execution starts** with clear console logging
3. **Planner creates `plan.md`** (and ONLY plan.md)
4. **Critic creates `critic_report.md`** (and ONLY critic_report.md)
5. **Both branches complete** and show success status
6. **Results aggregate back to Coder** with clear "Aggregating results" message
7. **Coder reviews both outputs** and proceeds with implementation
8. **No nested handoffs** are allowed from parallel branches

## Technical Details

### Parallel Branch Isolation

Each parallel branch receives:
- A forked `ToolRegistry` with isolated `_pending_handoff` state
- A cloned `ToolContext` to prevent race conditions
- Shared `_write_lock` for file operations (prevents concurrent writes)
- `_is_parallel_branch = True` flag to prevent nested handoffs

### Event Flow

```
User Request
    ↓
Coder (entry agent)
    ↓
handoff_to_agent(agent_names=["Planner", "Critic"])
    ↓
Agency.process() detects parallel mode
    ↓
ThreadPoolExecutor spawns parallel branches
    ├─→ Planner branch (forked registry)
    └─→ Critic branch (forked registry)
    ↓
Both branches complete
    ↓
Results aggregated
    ↓
Handoff to Coder (aggregation_target)
    ↓
Coder continues with merged results
```

## Files Modified

1. `src/indusagi/agency.py` - Enhanced parallel execution logging
2. `src/indusagi/tools/__init__.py` - Added parallel branch flag
3. `src/indusagi/tools/handoff.py` - Prevented nested handoffs
4. `example_agency_improved_anthropic_prompts/planner_instructions.md` - Clarified file naming
5. `example_agency_improved_anthropic_prompts/critic_instructions.md` - Clarified file naming

## Files Created

1. `test_parallel_execution.py` - Automated test script
2. `PARALLEL_EXECUTION_IMPROVEMENTS.md` - This summary document

## Benefits

1. **Clear visibility**: Users can now see exactly when parallel execution starts, which branches are running, and when they complete
2. **Prevents confusion**: Agents can't create the wrong files or initiate nested handoffs
3. **Better debugging**: Rich console output makes it easy to diagnose issues
4. **Safer execution**: Thread-safe file operations and isolated branch state
5. **Testable**: Automated test script for regression testing

## Known Limitations

1. **Windows mkdir issues**: The Coder agent may still encounter issues with `mkdir` commands on Windows PowerShell. This is a separate issue related to bash tool execution on Windows.
2. **No recursive parallel handoffs**: Parallel branches cannot spawn their own parallel handoffs (by design)
3. **Aggregation always goes to specified target**: The aggregation_target must be reachable from the current agent via communication flows

## Next Steps (Optional Future Improvements)

1. Add retry logic for failed parallel branches
2. Add timeout configuration for parallel branches
3. Add progress indicators for long-running parallel branches
4. Add support for conditional parallel execution (e.g., "run Critic only if Planner succeeds")
5. Improve Windows compatibility for bash commands
