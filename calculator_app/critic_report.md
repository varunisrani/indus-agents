# Calculator App - Risk Assessment Report

## Summary
Reviewing the calculator app implementation plan. While the specification covers basic functionality, there are several critical risks around floating-point precision, input validation, and user experience that could lead to incorrect results or user frustration.

---

## Top 3 Risks (Severity-Ordered)

### 1. Floating-Point Precision Errors (CRITICAL)
**Why it matters:** JavaScript uses IEEE 754 floating-point arithmetic, which produces well-known precision errors. A calculator that displays incorrect results is fundamentally broken.

**Specific failures:**
- `0.1 + 0.2 = 0.30000000000000004` instead of `0.3`
- `0.7 * 0.1 = 0.06999999999999999` instead of `0.07`
- `1.005.toFixed(2)` returns `"1.00"` instead of `"1.01"`

**Where observed:** The plan mentions "Perform calculations" in `app.js` (line 23) without specifying precision handling strategies.

**Mitigation required:**
- Use decimal.js library or implement proper rounding (e.g., `Number.EPSILON` comparisons, `Math.round(num * 100) / 100`)
- Define maximum decimal places for display (typically 10-12 digits)
- Implement proper equality checks for floating-point comparison

---

### 2. Input Validation & State Management Gaps (HIGH)
**Why it matters:** Without robust input validation, users can trigger invalid operations, multiple operators in sequence, or overflow conditions that crash or confuse the calculator.

**Specific failures:**
- Multiple operators in sequence: `5 ++ 5` or `5 */ 3`
- Division by zero: `5 / 0` should show "Error" not `Infinity`
- Leading zeros: `0005` displays as `0005` instead of `5`
- Decimal edge cases: `5..5`, `5.`, `.5`, `5.5.5`
- Overflow: `999999999 * 999999999` exceeds display width
- Negative numbers: No clear way to input `-5`

**Where observed:** Plan mentions "Handle edge cases and errors (e.g., division by zero)" (line 24) but lacks comprehensive input validation strategy.

**Mitigation required:**
- Implement state machine for valid input sequences (digit → operator → digit)
- Disable operator buttons after first operator until digit entered
- Sanitize input: strip leading zeros, prevent multiple decimals
- Handle division by zero explicitly (return "Error", clear on next input)
- Add overflow detection and display "Overflow" or scientific notation

---

### 3. User Experience & Accessibility Issues (MEDIUM)
**Why it matters:** Poor UX leads to user errors, frustration, and inability to use the calculator effectively.

**Specific failures:**
- **No keyboard support:** Users must click buttons; cannot type numbers/operators
- **No clear/backspace:** Users cannot correct typos without full clear
- **No operation history:** Users cannot see previous calculation (e.g., `5 + 3 = 8` shows only `8`)
- **Display truncation:** Long numbers overflow display without scrolling/scaling
- **No visual feedback:** Active state unclear; users unsure if button press registered
- **Accessibility gaps:** No ARIA labels, keyboard navigation, or screen reader support
- **Mobile responsiveness:** Touch targets may be too small (<44px recommended)

**Where observed:** Plan mentions "responsive design" (line 19) but lacks specific UX/accessibility requirements.

**Mitigation required:**
- Add keyboard event listeners (Enter = equals, Escape = clear, Backspace = delete last digit)
- Implement backspace button to remove last character
- Show full expression in secondary display (e.g., `5 + 3` above result `8`)
- Add `overflow-x: auto` or font scaling for long numbers
- Add `:active` and `:focus` states for visual feedback
- Include ARIA labels: `aria-label="5"`, `role="button"`
- Ensure touch targets ≥44px for mobile

---

## Tests Required

### Unit Tests
- `testFloatingPointPrecision()`: Verify `0.1 + 0.2 === 0.3`
- `testDivisionByZero()`: Verify `5 / 0` returns "Error"
- `testMultipleOperators()`: Verify `5 ++ 5` is rejected or handled
- `testDecimalInput()`: Verify `5..5`, `.5`, `5.` handled correctly
- `testLeadingZeros()`: Verify `0005` displays as `5`

### Integration Tests
- `testFullCalculationFlow()`: Verify `5 + 3 * 2 = 11` (order of operations)
- `testClearAfterError()`: Verify "Error" state clears on next input
- `testKeyboardInput()`: Verify keyboard events trigger correct button actions

### Edge Case Tests
- `testOverflow()`: Verify `999999999 * 999999999` handled gracefully
- `testNegativeNumbers()`: Verify `-5 + 3 = -2` works correctly
- `testMaximumDigits()`: Verify display truncates or scales at max width

### Accessibility Tests
- `testKeyboardNavigation()`: Verify Tab order and Enter/Escape work
- `testScreenReader()`: Verify ARIA labels announced correctly
- `testTouchTargets()`: Verify buttons ≥44px on mobile

---

## Next Steps for Coder

1. **Add precision handling to `app.js`**: Implement `decimal.js` or custom rounding before displaying results. Test with `0.1 + 0.2`.

2. **Implement input validation state machine**: Add logic to prevent invalid operator sequences and handle division by zero explicitly.

3. **Add keyboard support and backspace**: Map keyboard events to button handlers and add backspace functionality to `index.html`/`app.js`.

4. **Add secondary display for expression**: Show `5 + 3` above result `8` to improve UX and transparency.

5. **Include ARIA labels and focus states**: Add accessibility attributes to buttons in `index.html` and ensure `:focus` styles in `styles.css`.
