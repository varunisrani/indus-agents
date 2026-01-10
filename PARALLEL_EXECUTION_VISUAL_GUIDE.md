# Parallel Execution Visual Guide

## Before vs After Improvements

### BEFORE (Issues from User Log)

```
User: Run Planner + Critic in parallel...

[Coder] Parallel handoff to Planner, Critic: Create a comprehensive...
╭─── TOOL USAGE: [OK] handoff_to_agent ───╮
STOP [Agent Coder] Handoff requested

[Critic] Finding files: **/*.md
[Critic] Creating file: critic_report.md
[Critic] Handing off to Coder: ## Critic Report Complete...

[Planner] Creating file: critic-report.md  ❌ WRONG FILE!
[Planner] Handing off to Coder: Plan complete...  ❌ NESTED HANDOFF!

[Coder] Reading file: plan.md
[Coder] Reading file: critic-report.md
[Coder] Creating todo list...
... (flow continues but confused)
```

**Problems:**
- ❌ No clear "PARALLEL START" or "PARALLEL END" markers
- ❌ Planner created wrong file (`critic-report.md`)
- ❌ Both agents tried to handoff back to Coder (nested handoffs)
- ❌ Hard to see which agent is doing what
- ❌ No summary of parallel execution results

---

### AFTER (With Improvements)

```
User: Run Planner + Critic in parallel...

[Coder] Parallel handoff to Planner, Critic: Create a comprehensive...

╔══════════════════════════════════ PARALLEL EXECUTION START ══════════════════════════════════╗
║ From Agent: Coder
║ Target Agents: Planner, Critic
║ Message: Create a comprehensive specification for a Todo App...
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

▶ Starting parallel branch: Planner
▶ Starting parallel branch: Critic

[Planner] Creating file: plan.md  ✅ CORRECT FILE!
[Planner] Handing off to Coder: Plan complete...  ❌ BLOCKED (parallel branch)
⚠ Warning: Planner attempted nested handoff (ignored in parallel mode)

[Critic] Finding files: **/*.md
[Critic] Creating file: critic_report.md  ✅ CORRECT FILE!
[Critic] Handing off to Coder: ## Critic Report Complete...  ❌ BLOCKED (parallel branch)
⚠ Warning: Critic attempted nested handoff (ignored in parallel mode)

✓ Completed parallel branch: Planner (3.1s)
✓ Completed parallel branch: Critic (2.5s)

╔════════════════════════════════ PARALLEL EXECUTION COMPLETE ═════════════════════════════════╗
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Agent    ┃   Status   ┃ Duration ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Planner  │ ✓ Success  │   3.10s  │
│ Critic   │ ✓ Success  │   2.50s  │
└──────────┴────────────┴──────────┘
╚══════════════════════════════════════════════════════════════════════════════════════════════╝

→ Aggregating results in: Coder

[Coder] Reading file: plan.md
[Coder] Reading file: critic_report.md
[Coder] Creating todo list...
... (flow continues correctly)
```

**Improvements:**
- ✅ Clear "PARALLEL EXECUTION START" box
- ✅ Shows which agents are running in parallel
- ✅ Each agent creates the correct file
- ✅ Nested handoffs are blocked and logged
- ✅ Clear "PARALLEL EXECUTION COMPLETE" summary
- ✅ Shows success/failure status for each branch
- ✅ Shows timing for each branch
- ✅ Clear "Aggregating results" message
- ✅ Flow continues correctly after aggregation

---

## Execution Flow Diagram

### Single Handoff (Normal)
```
┌──────────┐
│  Coder   │ ← Entry Agent
└─────┬────┘
      │ handoff_to_agent(agent_name="Planner")
      ↓
┌──────────┐
│ Planner  │ ← Creates plan.md
└─────┬────┘
      │ handoff_to_agent(agent_name="Coder")
      ↓
┌──────────┐
│  Coder   │ ← Implements
└──────────┘
```

### Parallel Handoff (New Feature)
```
                    ┌──────────┐
                    │  Coder   │ ← Entry Agent
                    └─────┬────┘
                          │ handoff_to_agent(agent_names=["Planner", "Critic"])
                          │
        ╔═════════════════╧═════════════════╗
        ║   PARALLEL EXECUTION START        ║
        ╚═════════════════╤═════════════════╝
                          │
              ┌───────────┴───────────┐
              │                       │
              ↓                       ↓
        ┌──────────┐            ┌──────────┐
        │ Planner  │            │  Critic  │
        │ (Branch) │            │ (Branch) │
        └─────┬────┘            └─────┬────┘
              │                       │
              │ Creates plan.md       │ Creates critic_report.md
              │ (isolated registry)   │ (isolated registry)
              │                       │
              │ ❌ handoff blocked    │ ❌ handoff blocked
              │                       │
              └───────────┬───────────┘
                          │
        ╔═════════════════╧═════════════════╗
        ║   PARALLEL EXECUTION COMPLETE     ║
        ║                                   ║
        ║   ┌─────────┬─────────┬────────┐ ║
        ║   │ Planner │ Success │ 3.10s  │ ║
        ║   │ Critic  │ Success │ 2.50s  │ ║
        ║   └─────────┴─────────┴────────┘ ║
        ╚═════════════════╤═════════════════╝
                          │
                          ↓ Aggregation
                    ┌──────────┐
                    │  Coder   │ ← Merges results
                    └─────┬────┘
                          │
                          ↓ Continues implementation
                    ┌──────────┐
                    │  Coder   │ ← Implements
                    └──────────┘
```

---

## Registry Forking for Parallel Branches

### Root Registry (Coder)
```
┌─────────────────────────────────┐
│ ToolRegistry (root)             │
├─────────────────────────────────┤
│ _tools: {shared definitions}    │
│ _pending_handoff: None          │
│ _is_parallel_branch: False      │
│ _write_lock: <shared>           │
│ context: <original>             │
└─────────────────────────────────┘
```

### Forked Registry (Planner Branch)
```
┌─────────────────────────────────┐
│ ToolRegistry (Planner-branch)   │
├─────────────────────────────────┤
│ _tools: {shared definitions} ←──┼─ Shared with root
│ _pending_handoff: None          │ ← Isolated
│ _is_parallel_branch: True       │ ← Blocks handoffs
│ _write_lock: <shared>        ←──┼─ Shared (prevents concurrent writes)
│ context: <cloned>               │ ← Isolated
└─────────────────────────────────┘
```

### Forked Registry (Critic Branch)
```
┌─────────────────────────────────┐
│ ToolRegistry (Critic-branch)    │
├─────────────────────────────────┤
│ _tools: {shared definitions} ←──┼─ Shared with root
│ _pending_handoff: None          │ ← Isolated
│ _is_parallel_branch: True       │ ← Blocks handoffs
│ _write_lock: <shared>        ←──┼─ Shared (prevents concurrent writes)
│ context: <cloned>               │ ← Isolated
└─────────────────────────────────┘
```

**Key Points:**
- ✅ Tool definitions are shared (consistent schemas)
- ✅ Pending handoffs are isolated (no race conditions)
- ✅ Write lock is shared (prevents concurrent file writes)
- ✅ Context is cloned (isolated state)
- ✅ `_is_parallel_branch` flag blocks nested handoffs

---

## Console Output Color Guide

| Element | Color | Example |
|---------|-------|---------|
| Parallel Start/End Box | Bright Cyan | `╔══════════════════════════════════╗` |
| Branch Start | Bright Yellow | `▶ Starting parallel branch: Planner` |
| Branch Success | Green | `✓ Completed parallel branch: Planner (3.10s)` |
| Branch Error | Red | `✗ Completed parallel branch: Planner (3.10s)` |
| Warning | Yellow | `⚠ Warning: Planner attempted nested handoff` |
| Aggregation | Bright Magenta | `→ Aggregating results in: Coder` |
| Agent Name | Bold Bright Blue | `[Coder]` |
| Tool Usage | Yellow | `TOOL USAGE: [OK] handoff_to_agent` |

---

## Testing the Feature

### Quick Test Command
```bash
python test_parallel_execution.py
```

### Interactive Test
```bash
python example_agency_improved_anthropic.py
```

Then enter:
```
Run Planner + Critic in parallel: Planner drafts a spec for a calculator app; 
Critic lists top 3 risks. Then merge and implement.
```

### Expected Files Created
- ✅ `plan.md` (by Planner)
- ✅ `critic_report.md` (by Critic)
- ✅ `calculator/` folder with implementation (by Coder)

---

## Troubleshooting

### Issue: "Handoff not allowed: You are running in a parallel branch"
**Cause:** A parallel branch agent tried to call `handoff_to_agent`  
**Solution:** This is expected behavior. Parallel branches should complete their task and return results to the aggregator.

### Issue: Planner creates wrong file
**Cause:** Prompt confusion  
**Solution:** Updated prompts now explicitly state which files each agent should create.

### Issue: No parallel execution logs visible
**Cause:** Old version without enhanced logging  
**Solution:** Make sure you're using the updated `src/indusagi/agency.py` with the new console output.

### Issue: Concurrent file write errors
**Cause:** Multiple branches trying to write to the same file  
**Solution:** The shared `_write_lock` prevents this. If you still see issues, ensure agents are writing to different files.

---

## Summary

The parallel execution feature now provides:
1. **Clear visual feedback** with bordered boxes and color-coded output
2. **Prevention of nested handoffs** to avoid infinite loops
3. **Thread-safe file operations** with shared write locks
4. **Isolated branch state** to prevent race conditions
5. **Automatic result aggregation** back to a designated agent
6. **Comprehensive error handling** with clear warning messages

This makes the parallel execution feature production-ready and easy to debug!
