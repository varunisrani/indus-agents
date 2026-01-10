# Parallel Execution - Quick Reference Card

## 🚀 Quick Start

### Run a Parallel Execution
```bash
python example_agency_improved_anthropic.py
```

Then enter:
```
Run Planner + Critic in parallel: [describe what each should do]
```

### Run Automated Test
```bash
python test_parallel_execution.py
```

---

## 📋 What You'll See

### 1. Parallel Start
```
╔══════════════════════════════════ PARALLEL EXECUTION START ══════════════════════════════════╗
║ From Agent: Coder
║ Target Agents: Planner, Critic
║ Message: [your message]
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

### 2. Branch Execution
```
▶ Starting parallel branch: Planner
▶ Starting parallel branch: Critic
[Planner] Creating file: plan.md
[Critic] Creating file: critic_report.md
```

### 3. Completion Summary
```
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
```

### 4. Aggregation
```
→ Aggregating results in: Coder
```

---

## 🎯 Agent Responsibilities

| Agent | Creates | Does NOT Create |
|-------|---------|-----------------|
| **Planner** | `plan.md` | ❌ `critic_report.md` |
| **Critic** | `critic_report.md` | ❌ `plan.md` |
| **Coder** | Application files | ✅ Implements |

---

## 🔒 Safety Rules

1. ✅ Parallel branches run simultaneously
2. ✅ Each branch has isolated state
3. ❌ Parallel branches CANNOT call `handoff_to_agent`
4. ✅ File writes are thread-safe (shared lock)
5. ✅ Results automatically aggregate to Coder

---

## 🎨 Console Colors

| Color | Meaning |
|-------|---------|
| 🔵 Cyan | Parallel execution boundaries |
| 🟡 Yellow | Branch start / warnings |
| 🟢 Green | Success |
| 🔴 Red | Error |
| 🟣 Magenta | Aggregation |

---

## ⚠️ Common Warnings

### "Handoff not allowed: You are running in a parallel branch"
**What it means:** A parallel branch tried to call `handoff_to_agent`  
**Is it bad?** No, this is expected and prevented by design  
**What to do:** Nothing, the branch will complete normally

### "Warning: [Agent] attempted nested handoff (ignored)"
**What it means:** Same as above, just logged for visibility  
**Is it bad?** No, this is working as designed  
**What to do:** Nothing, continue normally

---

## 📁 Expected Files

After a parallel run with Planner + Critic:
- ✅ `plan.md` (by Planner)
- ✅ `critic_report.md` (by Critic)
- ✅ Application files (by Coder after aggregation)

---

## 🐛 Troubleshooting

### No parallel execution logs visible
**Fix:** Make sure you're using the latest `src/indusagi/agency.py`

### Planner creates wrong file
**Fix:** Updated prompts now prevent this

### Concurrent write errors
**Fix:** Shared write lock prevents this automatically

### Windows mkdir errors
**Note:** This is a separate issue with the Bash tool on Windows, not related to parallel execution

---

## 📚 Full Documentation

- **`IMPROVEMENTS_SUMMARY.md`** - High-level overview
- **`PARALLEL_EXECUTION_IMPROVEMENTS.md`** - Technical details
- **`PARALLEL_EXECUTION_VISUAL_GUIDE.md`** - Visual diagrams and troubleshooting

---

## 💡 Example Prompts

### Simple Parallel
```
Run Planner + Critic in parallel: Planner creates spec for calculator app; 
Critic lists top 3 risks.
```

### Complex Parallel
```
Run Planner + Critic in parallel:
- Planner: Draft comprehensive spec for todo app with categories, priorities, due dates
- Critic: Analyze security risks, data loss scenarios, and UX issues

After both complete, Coder should implement in todo-app/ folder.
```

---

## ✅ Verification Checklist

After running parallel execution, verify:
- [ ] Saw "PARALLEL EXECUTION START" box
- [ ] Saw both branches start
- [ ] Saw completion messages for both branches
- [ ] Saw summary table with status and timing
- [ ] Saw "Aggregating results in: Coder"
- [ ] Both expected files were created
- [ ] No errors in console output

---

## 🎯 Key Takeaways

1. **Clear Visibility**: You now see exactly when parallel execution starts and ends
2. **No Confusion**: Each agent knows exactly which files to create
3. **Safe Execution**: Thread-safe with isolated state
4. **Automatic Aggregation**: Results merge back to Coder automatically
5. **Easy Debugging**: Rich console output with colors and tables

---

## 🚀 Ready to Use!

The parallel execution feature is production-ready. Just run:
```bash
python example_agency_improved_anthropic.py
```

And try a parallel prompt!
