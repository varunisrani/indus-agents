# Test New Page Workflow

You are testing a newly added page in the echad-ai church management system. Follow this exact workflow:

## Phase 1: Environment Setup
1. Run `testsprite_bootstrap_tests` with:
   - `localPort`: 3002 (Next.js dev server)
   - `type`: frontend
   - `projectPath`: C:\Users\Varun israni\echad-ai
   - `testScope`: codebase

2. Run `testsprite_generate_code_summary` to analyze the codebase structure

## Phase 2: Custom Test Plan Generation (Manual, NOT TestSprite MCP)
3. **DO NOT** use testsprite_generate_frontend_test_plan
4. Instead, analyze the page and create a CUSTOM test plan
   - **UPDATE EXISTING FILE**: `testsprite_tests/testsprite_frontend_test_plan.json`
   - Do NOT create a new file
   - Include ONLY REQUIRED tests for the newly added page
   - Test ONLY essential features of that specific page
   - Do NOT include: sidebar tests, general app tests, nice-to-have features
   - Each test case must be necessary for validating the page functionality

### Test Plan Structure (Update testsprite_tests/testsprite_frontend_test_plan.json):
```json
{
  "testCases": [
    {
      "testId": "PAGE001",
      "testName": "[REQUIRED] Page Load and Core Rendering",
      "description": "Verify page loads correctly - ONLY core/essential components",
      "steps": [
        "Navigate to page URL",
        "Verify page loads without errors",
        "Verify essential components render"
      ],
      "expectedResult": "Page loads without errors"
    },
    {
      "testId": "PAGE002",
      "testName": "[REQUIRED] Primary Feature - [Feature Name]",
      "description": "Test the main critical feature of this page",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expectedResult": "Critical feature works correctly"
    },
    {
      "testId": "PAGE003",
      "testName": "[REQUIRED] Essential User Interaction",
      "description": "Test essential user interaction required for page functionality",
      "steps": ["Step 1", "Step 2"],
      "expectedResult": "User interaction works as expected"
    }
  ],
  "pageUrl": "/the-page-url",
  "pageName": "New Page Display Name",
  "loginRequired": true,
  "loginCredentials": {
    "email": "solovpxoffical@gmail.com",
    "password": "Hello@1955"
  },
  "focusArea": "ONLY required tests for this specific page - NO extra/nice-to-have tests",
  "excludeTests": ["Sidebar tests", "General app navigation", "Header tests", "Secondary features", "Nice-to-have functionality"],
  "testStrategy": "Lean and focused - only essential tests needed to validate page works",
  "additionalInstruction": "Execute ONLY required test cases from testsprite_frontend_test_plan.json. Focus only on [PAGE_NAME] critical functionality. Skip all non-essential tests."
}
```

### Important Notes:
- ⚠️ **UPDATE the file**: `testsprite_tests/testsprite_frontend_test_plan.json`
- ⚠️ **Never create a new test plan file**
- ✅ Include ONLY REQUIRED tests - be lean and focused
- ✅ Mark tests with [REQUIRED] prefix
- ✅ Each test must validate essential functionality
- ✅ Exclude: secondary features, nice-to-have tests, general app tests
- ✅ Test only what's necessary for page validation

## Phase 3: User Approval
5. Display the generated test plan to the user
6. Ask for approval: "Does this test plan cover all REQUIRED features of the new page? (Remember: only essential tests, no extras)"
7. Emphasize that test plan is LEAN and focused on critical functionality only
8. Wait for user confirmation before proceeding

### What NOT to do in Phase 3:
- ❌ Do NOT add extra tests beyond what's required
- ❌ Do NOT include secondary features
- ❌ Do NOT add nice-to-have test scenarios
- ❌ Do NOT test non-critical functionality

## Phase 4: Execute Tests
8. After user approval, run `testsprite_generate_code_and_execute` with:
   - `projectName`: echad-ai
   - `projectPath`: C:\Users\Varun israni\echad-ai
   - `testIds`: [] (run all tests from testsprite_tests/testsprite_frontend_test_plan.json)
   - `additionalInstruction`: "Execute all test cases from testsprite_tests/testsprite_frontend_test_plan.json. Focus only on the specified page. Generate detailed pass/fail report for each test case."

9. Review test results and provide:
   - ✅ Passed tests count
   - ❌ Failed tests count
   - 🔍 Issues found (if any)
   - 📋 Recommendations for fixes

### Important Reminder:
- ✅ Uses test cases from: `testsprite_tests/testsprite_frontend_test_plan.json`
- ✅ Only tests the newly added page
- ✅ No sidebar or general app tests

## What This Workflow Does
✅ Initializes test environment properly
✅ Analyzes your specific page code
✅ Creates LEAN and FOCUSED test plan (ONLY required tests)
✅ NO generic sidebar/header tests
✅ NO secondary or nice-to-have features
✅ Only tests CRITICAL functionality of that page
✅ Gets your approval before running expensive tests
✅ Executes and generates detailed report
✅ Minimizes testing time by focusing on essentials

## Usage
When you add a new page:
1. Tell Claude Code: "I added a new page at /member-dashboard/bible-studies"
2. Provide page name and main features
3. Follow the workflow phases above

### File Management
- **File to Update**: `testsprite_tests/testsprite_frontend_test_plan.json`
- **Action**: UPDATE existing file, never create new ones
- **Content**: Custom test cases for your specific page only

---

**Remember**:
- This workflow ensures LEAN and FOCUSED testing for your new page - ONLY essential tests!
- Always update `testsprite_tests/testsprite_frontend_test_plan.json` with your custom test plan
- Get user approval before running expensive tests
- Include ONLY REQUIRED/CRITICAL features in your test plan
- NO extra, secondary, or nice-to-have tests
- Mark each test with [REQUIRED] prefix
- Minimize bloat - quality over quantity in test cases
