# /test-page - Intelligent Test Generation Command

Generate and execute Playwright E2E tests for any page in the echad-ai application using Pure Claude-based test generation.

## ⚠️ IMPORTANT - CREDENTIALS FIRST

**This command ALWAYS collects login credentials as the FIRST step before generating any tests.**

## Usage

```
/test-page /member-dashboard
/test-page /pastor-events --focus="event creation"
/test-page /prayer-requests --role="member"
```

---

# PHASE 0: Collect User Credentials (MANDATORY - ALWAYS FIRST)

Before any test generation, page analysis, or file creation, I MUST ask the user for login credentials.

**Why**: Tests need valid credentials to simulate real user logins. Credentials are only used in this session and during test execution.

## Credential Collection Process

I will ask the user the following questions:

**Question 1: Email Address**
- Prompt: "What email address should I use for login testing?"
- Example: "test.pastor@church.com" or "solovpxofficial@gmail.com"
- Required: Yes

**Question 2: Password**
- Prompt: "What password should I use for login testing?"
- Example: "Hello@1955"
- Required: Yes

**Question 3: User Role**
- Prompt: "What is the user role for this account?"
- Options: Pastor / Member / Admin
- Required: Yes

**Question 4: Additional Credentials (Optional)**
- Prompt: "Do you need tests for multiple roles? (If yes, provide credentials for second role)"
- Options: Yes (provide email/password/role) / No
- Required: No

## Credential Storage & Security

### During Test Generation:
- ✅ Store credentials in memory (temporary variable)
- ✅ Use in generated test files with ⚠️ warnings
- ✅ Show in test plan with [REDACTED] in JSON file
- ✅ Create README.md with security warnings

### After Test Execution:
- ✅ Remind user to secure/remove credentials before committing
- ✅ Suggest using environment variables
- ✅ Recommend adding test files to .gitignore

### DO NOT:
- ❌ Save credentials to any JSON configuration files
- ❌ Commit test files with embedded credentials
- ❌ Hardcode credentials in command file
- ❌ Store credentials in logs or reports

---

# PHASE 1: Page Analysis & Discovery

After collecting credentials, analyze the target page:

1. **Identify page structure**
   - Main components and features
   - Forms and input fields
   - Buttons and interactive elements
   - Navigation elements

2. **Detect authentication requirements**
   - Does this page require login?
   - Are there role-based restrictions?
   - What auth flow is used?

3. **Map user workflows**
   - Primary use cases
   - Core feature interactions
   - Data flow and dependencies

4. **Identify critical features**
   - What are the 1-2 main features of this page?
   - What would users do most often?
   - What could break the user experience?

---

# PHASE 2: Lean Test Plan Generation

Generate a REQUIRED tests only (4-8 critical tests per page):

## Test Categories (Pick 1-2 from each):

### A. Page Load & Authentication (ALWAYS)
- `[PAGE]001_REQUIRED_Page_Load_Authentication` - Verify page loads after login

### B. Core Feature #1 (PICK 1)
- `[PAGE]002_REQUIRED_Create_Feature` - Add/create main feature
- `[PAGE]002_REQUIRED_View_Feature` - Display main feature
- `[PAGE]002_REQUIRED_Search_Feature` - Search/filter main feature

### C. Core Feature #2 (PICK 1)
- `[PAGE]003_REQUIRED_Edit_Feature` - Edit/update feature
- `[PAGE]003_REQUIRED_Delete_Feature` - Delete with confirmation
- `[PAGE]003_REQUIRED_Interact_Feature` - Button interactions (RSVP, Enroll, etc.)

### D. Error Handling (PICK 1)
- `[PAGE]004_REQUIRED_Error_Handling` - Handle API/network errors
- `[PAGE]004_REQUIRED_Validation_Errors` - Handle form validation errors

### E. Console Check (ALWAYS)
- `[PAGE]005_REQUIRED_No_Console_Errors` - Verify no JavaScript errors

## Test Plan JSON Structure

```json
{
  "meta": {
    "pageName": "Page Display Name",
    "pageUrl": "/page-url",
    "testDate": "2025-10-30",
    "testStrategy": "Lean - REQUIRED tests only (4-8 tests)",
    "testScope": "Critical path & core features only"
  },
  "authentication": {
    "required": true,
    "role": "[USER_PROVIDED_ROLE]",
    "credentials": {
      "email": "[REDACTED]",
      "password": "[REDACTED]"
    }
  },
  "testCases": [
    {
      "testId": "PAGE001",
      "testName": "[REQUIRED] Page Load and Authentication",
      "category": "functional",
      "priority": "Critical",
      "description": "Verify page loads successfully after user login",
      "steps": [
        {
          "action": "Navigate to page URL",
          "element": "page",
          "details": "/page-url"
        },
        {
          "action": "Wait for page load",
          "element": "DOMContentLoaded",
          "details": "Wait until page fully loads"
        },
        {
          "action": "Verify content visible",
          "element": "main content",
          "details": "Check key UI elements are present"
        }
      ],
      "expectedResult": "Page loads without errors, all main elements visible"
    },
    {
      "testId": "PAGE002",
      "testName": "[REQUIRED] Core Feature Functionality",
      "category": "functional",
      "priority": "Critical",
      "description": "Test primary feature interaction",
      "steps": [...],
      "expectedResult": "Feature works as expected"
    }
  ],
  "excludedTests": [
    "Sidebar navigation (tested in other tests)",
    "Footer display (tested in other tests)",
    "Full responsive design (tested separately)",
    "Secondary features (out of scope)",
    "Exhaustive edge cases (focus on critical path)"
  ]
}
```

---

# PHASE 3: Python Test File Generation

Generate Playwright test files with user-provided credentials.

## Test File Template

```python
"""
⚠️ SECURITY WARNING ⚠️
This test file contains login credentials.
DO NOT commit this file to version control with actual credentials.
BEFORE COMMITTING:
1. Replace credentials with environment variables: os.getenv('TEST_EMAIL'), os.getenv('TEST_PASSWORD')
2. Or delete this test file after use
3. Or add to .gitignore
"""

import asyncio
import os
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    """
    Test ID: [PAGE]001
    Test Name: [REQUIRED] Page Load and Authentication
    Description: Verify page loads after user login
    """
    pw = None
    browser = None
    context = None

    try:
        # Initialize Playwright
        pw = await async_api.async_playwright().start()

        # Launch headless browser with optimizations
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ]
        )

        # Create browser context
        context = await browser.new_context()
        context.set_default_timeout(5000)

        # Create new page
        page = await context.new_page()

        # STEP 1: Navigate to page
        print("[TEST] Navigating to http://localhost:3002/page-url")
        await page.goto("http://localhost:3002/page-url", wait_until="commit", timeout=10000)

        # STEP 2: Wait for page load
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except Exception:
            pass

        # STEP 3: Wait for iframes to load
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except Exception:
                pass

        # STEP 4: Authenticate if required
        print("[TEST] Performing login authentication")
        frame = context.pages[-1]

        # Fill email (⚠️ REPLACE BEFORE COMMIT - use environment variable in production)
        email_input = frame.locator('xpath=//input[@type="email" or @placeholder="Email"]').first
        await email_input.fill('[USER_PROVIDED_EMAIL]')  # ⚠️ REPLACE WITH: os.getenv('TEST_EMAIL')
        await page.wait_for_timeout(1000)

        # Click Continue button
        continue_btn = frame.locator('xpath=//button[contains(text(), "Continue")]').first
        await continue_btn.click(timeout=5000)
        await page.wait_for_timeout(2000)

        # Fill password (⚠️ REPLACE BEFORE COMMIT - use environment variable in production)
        password_input = frame.locator('xpath=//input[@type="password"]').first
        await password_input.fill('[USER_PROVIDED_PASSWORD]')  # ⚠️ REPLACE WITH: os.getenv('TEST_PASSWORD')
        await page.wait_for_timeout(1000)

        # Click Submit/Continue button
        submit_btn = frame.locator('xpath=//button[contains(text(), "Continue") or contains(text(), "Submit")]').first
        await submit_btn.click(timeout=5000)
        await page.wait_for_timeout(3000)

        # STEP 5: Verify page loaded after login
        print("[TEST] Verifying page content is visible")
        await expect(frame.locator('xpath=//main | //div[@role="main"]').first).to_be_visible(timeout=30000)

        print("[PASS] Test completed successfully")
        await asyncio.sleep(2)

    except AssertionError as e:
        print(f"[FAIL] Assertion failed: {str(e)}")
        raise

    except Exception as e:
        print(f"[ERROR] Test failed with error: {str(e)}")
        raise

    finally:
        # Cleanup: Close context, browser, and playwright
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

# Run test
if __name__ == "__main__":
    asyncio.run(run_test())
```

## Naming Convention

Generated test files follow this pattern:

```
[PAGE_ID][TEST_NUMBER]_REQUIRED_[Feature_Name].py

Examples:
- EVT001_REQUIRED_Page_Load_Authentication.py
- EVT002_REQUIRED_Create_Event_Form.py
- EVT003_REQUIRED_Edit_Event_Functionality.py
- DASH001_REQUIRED_Dashboard_Load.py
- DASH002_REQUIRED_Activity_Feed_Display.py
```

---

# PHASE 4: File Organization & Structure

Auto-organize generated test files into intelligent directory structure:

## Directory Structure

```
testsprite_tests/
└── [page-name]-tests/
    ├── README.md (⚠️ SECURITY WARNING)
    ├── test_plan.json (credentials REDACTED)
    ├── [PAGE]001_REQUIRED_*.py
    ├── [PAGE]002_REQUIRED_*.py
    ├── [PAGE]003_REQUIRED_*.py
    ├── [PAGE]004_REQUIRED_*.py
    ├── [PAGE]005_REQUIRED_*.py
    └── test_results.json (after execution)
```

## Security README Template

```markdown
# [Page Name] Test Suite

⚠️ **SECURITY WARNING** ⚠️

This folder contains test files with embedded login credentials.

## DO NOT COMMIT

These test files contain actual email addresses and passwords.
**DO NOT commit them to git without securing credentials first.**

## How to Secure Before Committing

### Option 1: Use Environment Variables (Recommended)
```bash
# Create .env file in project root
TEST_EMAIL=your-email@example.com
TEST_PASSWORD=your-password

# Update test files to read from .env
import os
email = os.getenv('TEST_EMAIL')
password = os.getenv('TEST_PASSWORD')
```

### Option 2: Add to .gitignore
```
# .gitignore
testsprite_tests/*-tests/*.py
testsprite_tests/*-tests/test_results.json
```

### Option 3: Delete After Use
```bash
rm -rf testsprite_tests/[page-name]-tests/
```

## Test Execution

```bash
python [PAGE]001_REQUIRED_*.py
```

## Generated: 2025-10-30
## Expires: [30 days from generation]
```

---

# PHASE 5: Execution & Reporting

Execute generated tests and generate comprehensive report.

## Execution Steps

1. **Run each test file** in sequence:
   ```bash
   cd testsprite_tests/[page-name]-tests/
   python [PAGE]001_REQUIRED_*.py
   python [PAGE]002_REQUIRED_*.py
   # ... etc
   ```

2. **Capture results**:
   - Pass/Fail status
   - Execution time
   - Error messages (if any)
   - Screenshots (on failure)

3. **Generate test_results.json**:
   ```json
   {
     "testRunDate": "2025-10-30T14:30:00Z",
     "pageUrl": "/page-url",
     "totalTests": 5,
     "passed": 5,
     "failed": 0,
     "passRate": "100%",
     "testResults": [
       {
         "testId": "PAGE001",
         "testName": "[REQUIRED] Page Load and Authentication",
         "status": "PASSED",
         "executionTime": "8.234s",
         "message": "Test passed successfully"
       }
     ],
     "summary": "All critical tests passed"
   }
   ```

---

# PHASE 5b: Post-Execution Security Reminder

After tests execute, remind user about credential security:

```
✅ Tests completed successfully!

⚠️ IMPORTANT SECURITY REMINDER ⚠️

Your login credentials are embedded in these test files:
- testsprite_tests/[page-name]-tests/[PAGE]00X_REQUIRED_*.py

BEFORE COMMITTING TO GIT:

1. Convert to environment variables:
   ```bash
   export TEST_EMAIL="your-email"
   export TEST_PASSWORD="your-password"
   ```

2. OR add to .gitignore:
   ```
   testsprite_tests/*-tests/*.py
   ```

3. OR delete test files:
   ```bash
   rm -rf testsprite_tests/[page-name]-tests/
   ```

Credentials will be deleted from memory once this session ends.
```

---

# Implementation Guidelines

## Lean Testing Philosophy

### ✅ INCLUDE (Critical Path Only)
- Page load & authentication (always)
- Primary feature #1 (create/view/search)
- Primary feature #2 (edit/delete/interact)
- Critical error handling
- Console error check

**Total: 4-8 tests per page (target: 5-6 tests)**

### ❌ EXCLUDE (Out of Scope)
- Sidebar navigation (tested separately)
- Footer/header components (tested separately)
- Full responsive design suite (do separate responsive tests)
- Secondary/tertiary features (focus on critical path)
- Exhaustive edge cases
- Performance tests
- Accessibility tests (unless critical)

## Element Locators

Prefer this order:

1. **XPath** (most flexible):
   ```python
   frame.locator('xpath=//button[contains(text(), "Submit")]')
   ```

2. **Text Content** (when unique):
   ```python
   frame.locator('text=Create Event')
   ```

3. **CSS Selectors** (when available):
   ```python
   frame.locator('button.primary-action')
   ```

4. **Data Attributes** (best practice):
   ```python
   frame.locator('[data-testid="submit-button"]')
   ```

## Assertions

Always verify:
- Element visibility
- Text content (exact matches)
- No console errors
- Page load states

```python
await expect(locator.first).to_be_visible(timeout=30000)
await expect(locator).to_contain_text("Expected Text")
```

---

# Example: Complete Test Generation Flow

## Input
```
Command: /test-page /pastor-events
```

## Phase 0: Credentials Prompt
```
Q1: Email? → pastor.test@church.com
Q2: Password? → SecurePass123!
Q3: Role? → pastor
Q4: Multiple roles? → No
```

## Phase 1: Analysis
```
Analyzing /pastor-events page...
✓ Page structure identified
✓ Auth required: Yes (pastor role)
✓ Main features: Create, Edit, Delete, View, Search
✓ Key flows: Create event → Edit → Delete
```

## Phase 2: Test Plan
```
Generated test plan:
1. EVT001_REQUIRED_Page_Load_Authentication
2. EVT002_REQUIRED_Create_Event_Form
3. EVT003_REQUIRED_Edit_Event_Functionality
4. EVT004_REQUIRED_Delete_Event_Confirmation
5. EVT005_REQUIRED_No_Console_Errors

Total: 5 lean tests (critical path only)
```

## Phase 3: Test Files
```
Generated files:
✓ EVT001_REQUIRED_Page_Load_Authentication.py (120 lines)
✓ EVT002_REQUIRED_Create_Event_Form.py (150 lines)
✓ EVT003_REQUIRED_Edit_Event_Functionality.py (140 lines)
✓ EVT004_REQUIRED_Delete_Event_Confirmation.py (130 lines)
✓ EVT005_REQUIRED_No_Console_Errors.py (90 lines)

All files include:
✓ Credentials (with ⚠️ warnings)
✓ Proper cleanup (try/finally)
✓ Clear assertions
```

## Phase 4: Organization
```
Created structure:
testsprite_tests/
└── pastor-events-tests/
    ├── README.md (security warning)
    ├── test_plan.json (redacted credentials)
    ├── EVT001_REQUIRED_*.py
    ├── EVT002_REQUIRED_*.py
    ├── EVT003_REQUIRED_*.py
    ├── EVT004_REQUIRED_*.py
    └── EVT005_REQUIRED_*.py
```

## Phase 5: Execution
```
Running tests...
✅ EVT001_REQUIRED_Page_Load_Authentication [8.2s]
✅ EVT002_REQUIRED_Create_Event_Form [12.5s]
✅ EVT003_REQUIRED_Edit_Event_Functionality [11.8s]
✅ EVT004_REQUIRED_Delete_Event_Confirmation [10.3s]
✅ EVT005_REQUIRED_No_Console_Errors [7.9s]

Results: 5/5 passed (100%)
```

## Phase 5b: Security Reminder
```
⚠️ SECURITY REMINDER
Test files contain your credentials at:
  testsprite_tests/pastor-events-tests/EVT00X_*.py

BEFORE COMMITTING:
1. Replace with environment variables
2. Add to .gitignore
3. Or delete test files
```

---

# Best Practices

1. **Always ask for credentials first** (Phase 0)
2. **Keep tests lean** (4-8 per page)
3. **Focus on critical path** (what users do most)
4. **Use clear descriptions** (what is being tested)
5. **Add security warnings** (to every test file)
6. **Create README.md** (in every test directory)
7. **Save test plan as JSON** (for documentation)
8. **Remind about credential security** (after execution)

---

# Troubleshooting

## Tests Can't Find Elements
- Verify XPath is correct
- Check element is visible on page
- Wait longer for elements to appear (increase timeout)
- Use browser dev tools to inspect element

## Authentication Fails
- Verify credentials are correct
- Check login page hasn't changed (new flow)
- Ensure account has access to page
- Check if page requires specific role

## Tests Time Out
- Increase timeout values (30000ms = 30 seconds)
- Check if page is loading slowly
- Verify network connection
- Check if localhost:3002 is running

## Console Errors
- Fix JavaScript errors in page code
- These are actual bugs, not test issues
- Refer to browser developer console (F12)

---

# Security Checklist

Before committing test files:

- [ ] Have you replaced hardcoded credentials with environment variables?
- [ ] Are test files in .gitignore if still containing credentials?
- [ ] Have you deleted test files after use if not needed?
- [ ] Did you remind team about credential security?
- [ ] Are only test_plan.json files committed (with redacted credentials)?
- [ ] Have you documented where actual credentials are stored?

---

**Command Version**: 1.0
**Last Updated**: 2025-10-30
**Framework**: Playwright (Python async)
**Target**: echad-ai (localhost:3002)