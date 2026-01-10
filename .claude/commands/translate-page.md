---
name: translate-page
description: Add i18next internationalization to any page for English, Japanese, and Hindi
tags: [i18n, translation, internationalization]
---

# Translate Page with i18next

This command adds i18next internationalization support to any page in the codebase, translating it into English, Japanese (ja), and Hindi (hi).

## Usage

```
/translate-page <file-path>
```

**Example:**
```
/translate-page app/member-dashboard/page.tsx
```

## What This Command Does

1. **Reads the target page** and identifies all hardcoded text strings
2. **Creates translation JSON files** for English, Japanese, and Hindi in `locales/{locale}/`
3. **Updates the page component** to use i18next hooks and translation keys
4. **Makes URLs locale-aware** for navigation links
5. **Adds LanguageSwitcher component** to the page
6. **Updates configuration** files to include the new namespace
7. **Updates middleware** if needed for new routes

## Implementation Steps

### Step 1: Analyze the Target Page

Read the file provided by the user and:
- Extract all hardcoded text strings (headings, paragraphs, button text, labels, etc.)
- Identify navigation links that need to be locale-aware
- Note the component structure and imports

### Step 2: Create Namespace Name

Generate a namespace name from the file path:
- `app/member-dashboard/page.tsx` → `member-dashboard`
- `app/pastor-events/page.tsx` → `pastor-events`
- Strip `app/`, `/page.tsx`, and special characters

### Step 3: Create Translation Files

Create three JSON files in the `locales/` directory:

**File Structure:**
```
locales/
├── en/{namespace}.json
├── ja/{namespace}.json
└── hi/{namespace}.json
```

**Translation Key Naming Convention:**
- Use descriptive nested keys
- Group related strings together
- Examples:
  - `header.title`
  - `buttons.submit`
  - `features.analytics.title`
  - `features.analytics.description`

### Step 4: Translate Strings

For each string found:

**English (en):** Keep original text

**Japanese (ja):** Translate to Japanese
- Use natural Japanese translations
- Keep technical terms like "AI", "Dashboard" in original form or katakana

**Hindi (hi):** Translate to Hindi (Devanagari script)
- Use natural Hindi translations
- Keep technical terms that are commonly used in English

### Step 5: Update Page Component

**CRITICAL: Follow this exact pattern to avoid translation keys showing instead of translations**

Add these imports at the top:
```typescript
import '@/lib/i18n/client'
import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import LanguageSwitcher from '@/app/components/LanguageSwitcher'
```

Add the translation hook and language synchronization:
```typescript
export default function YourComponent() {
  const { t, i18n, ready } = useTranslation(['{namespace}'])

  // State for language loading - MUST be declared before useEffect
  const [isLanguageLoading, setIsLanguageLoading] = useState(true)

  // CRITICAL FIX: Ensure translations are loaded for the current locale
  useEffect(() => {
    const syncLanguage = async () => {
      try {
        setIsLanguageLoading(true)
        // Get locale from cookie
        const cookies = document.cookie.split(';').map(c => c.trim())
        const localeCookie = cookies.find(c => c.startsWith('i18next='))
        if (localeCookie) {
          const locale = localeCookie.split('=')[1]
          if (locale && locale !== i18n.language) {
            await i18n.changeLanguage(locale)
          }
        }
        // Ensure namespace is loaded
        await i18n.loadNamespaces('{namespace}')
      } finally {
        setIsLanguageLoading(false)
      }
    }

    if (i18n) {
      syncLanguage()
    }
  }, [i18n])

  // CRITICAL: Wait for translations to load before rendering
  if (!ready || isLanguageLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    )
  }

  // Your component JSX here...
}
```

Replace all hardcoded strings with translation keys:
```typescript
// Before
<h1>Welcome to Dashboard</h1>

// After
<h1>{t('{namespace}:header.title')}</h1>
```

Add locale-aware URLs:
```typescript
const currentLocale = i18n.language
const localizedUrl = currentLocale === 'en'
  ? '/some-page'
  : `/${currentLocale}/some-page`
```

Add LanguageSwitcher component (if not present):
```typescript
<LanguageSwitcher className="absolute top-4 right-4 z-10" />
```

**Why This Pattern is Required:**

The issue we discovered: Translation keys (like `header.title`) display instead of actual translations because:
1. i18next initializes with a default language, but doesn't automatically sync with the cookie from middleware
2. Namespaces need to be explicitly loaded with `i18n.loadNamespaces()`
3. Components render before translations are ready, showing keys instead of values

**This pattern fixes it by:**
1. Reading the `i18next` cookie set by middleware
2. Explicitly changing i18next language to match the cookie
3. Explicitly loading the namespace
4. Showing a loading state until everything is ready
5. Only rendering the component when `ready && !isLanguageLoading`

### Step 6: Update Configuration Files

**Update `lib/i18n/types.ts`:**
Add the new namespace to the union type:
```typescript
export type TranslationNamespace =
  | 'common'
  | 'pastor-login'
  | 'pastor-signup'
  | 'home'
  | '{namespace}' // Add new namespace
```

**Update `lib/i18n/config.ts`:**
Add the namespace to the `ns` array:
```typescript
ns: ['common', 'pastor-login', 'pastor-signup', 'home', '{namespace}'],
```

### Step 7: Update Middleware (if needed)

If the page has locale-prefixed routes that need to be public, add them to `middleware.ts`:
```typescript
const isPublicRoute = createRouteMatcher([
  // ... existing routes
  "/ja/{route-path}(.*)",
  "/hi/{route-path}(.*)",
])
```

### Step 8: Verify and Test

After implementation:
1. Ensure the dev server compiles without errors
2. Check that all translation keys are defined in all three languages
3. Verify no hardcoded strings remain (except technical identifiers)
4. Test that language switching works correctly

## Best Practices

### Translation Key Guidelines

1. **Use descriptive keys:**
   - ✅ Good: `features.analytics.title`
   - ❌ Bad: `text1`

2. **Group related content:**
   ```json
   {
     "features": {
       "analytics": {
         "title": "Analytics",
         "description": "Track your metrics"
       }
     }
   }
   ```

3. **Keep consistent structure across locales:**
   - All three JSON files should have identical key structures
   - Only values should differ

### Component Update Guidelines

1. **Don't translate:**
   - Variable names
   - Class names
   - Technical identifiers
   - Icon names
   - API endpoints

2. **Do translate:**
   - User-facing text
   - Headings and titles
   - Button labels
   - Descriptions
   - Help text
   - Error messages
   - Placeholder text

3. **Locale-aware URLs:**
   - Apply to navigation links (Link href)
   - Apply to router.push() calls
   - Keep API routes unchanged

### Special Cases

**Dynamic Content:**
If content comes from database/API, don't translate in component. Note it for backend i18n.

**Pluralization:**
If needed, use i18next pluralization:
```typescript
t('items', { count: 5 }) // "5 items"
```

**Variables in Translations:**
```json
{
  "welcome": "Welcome, {{name}}!"
}
```
```typescript
t('welcome', { name: userName })
```

## Example Output

After running `/translate-page app/example/page.tsx`:

**Files Created:**
- `locales/en/example.json`
- `locales/ja/example.json`
- `locales/hi/example.json`

**Files Modified:**
- `app/example/page.tsx` (i18n integrated)
- `lib/i18n/types.ts` (namespace added)
- `lib/i18n/config.ts` (namespace added)
- `middleware.ts` (routes added if needed)

## Notes

- The i18n infrastructure (lib/i18n/, LanguageSwitcher) must already exist
- Japanese and Hindi translations are auto-generated but should be reviewed by native speakers
- Technical accuracy is prioritized over literal translation
- The command preserves existing code structure and styling

## After Running the Command

1. **Review translations** - Check Japanese and Hindi translations for accuracy
2. **Test all three languages** - Verify switching works correctly
3. **Check responsive design** - Ensure translations don't break layout
4. **Verify URLs** - Test that navigation maintains locale

---

## Troubleshooting

### Issue: Translation Keys Display Instead of Translations

**Symptoms:**
- You see `header.title` instead of "Dashboard"
- You see `metrics.totalMembers` instead of "Total members"
- Raw translation keys appear throughout the page

**Root Cause:**
The component renders before i18next has:
1. Synchronized with the locale cookie from middleware
2. Loaded the namespace translations
3. Changed to the correct language

**Solution:**
Ensure your component follows the **exact pattern in Step 5** above:

1. ✅ Import `useEffect` and `useState` from React
2. ✅ Get `i18n` and `ready` from `useTranslation` hook (not just `t`)
3. ✅ Add `isLanguageLoading` state initialized to `true`
4. ✅ Add the `useEffect` that syncs language from cookie
5. ✅ Add the loading check: `if (!ready || isLanguageLoading) return <Loading />`

**Verification:**
```typescript
// ❌ WRONG - Missing language sync
const { t } = useTranslation(['namespace'])

// ✅ CORRECT - With language sync
const { t, i18n, ready } = useTranslation(['namespace'])
const [isLanguageLoading, setIsLanguageLoading] = useState(true)

useEffect(() => {
  const syncLanguage = async () => {
    try {
      setIsLanguageLoading(true)
      const cookies = document.cookie.split(';').map(c => c.trim())
      const localeCookie = cookies.find(c => c.startsWith('i18next='))
      if (localeCookie) {
        const locale = localeCookie.split('=')[1]
        if (locale && locale !== i18n.language) {
          await i18n.changeLanguage(locale)
        }
      }
      await i18n.loadNamespaces('namespace')
    } finally {
      setIsLanguageLoading(false)
    }
  }
  if (i18n) syncLanguage()
}, [i18n])

if (!ready || isLanguageLoading) return <Loading />
```

### Issue: Translations Work in English but Not in Japanese/Hindi

**Symptoms:**
- English translations work fine
- Switching to Japanese or Hindi shows keys or English fallback

**Root Cause:**
Translation JSON files are missing or have incorrect structure

**Solution:**
1. Verify all three translation files exist:
   - `locales/en/{namespace}.json`
   - `locales/ja/{namespace}.json`
   - `locales/hi/{namespace}.json`

2. Verify JSON structure is identical across all three files:
   ```json
   // All three files must have the same keys
   {
     "header": {
       "title": "..."  // Only values differ
     }
   }
   ```

3. Check browser console for i18next errors about missing translations

### Issue: Some Translations Work, Others Don't

**Symptoms:**
- Some text displays correctly, other text shows keys
- Inconsistent translation behavior

**Root Cause:**
Missing translation keys in JSON files

**Solution:**
1. Open browser DevTools console
2. Look for warnings like: `i18next: key 'some.key' not found`
3. Add missing keys to all three translation JSON files
4. Ensure nested structure matches exactly

### Issue: Translations Don't Update When Switching Languages

**Symptoms:**
- LanguageSwitcher doesn't change the displayed language
- Page stays in same language after switching

**Root Cause:**
Component not re-rendering when language changes

**Solution:**
Ensure you're using the `t` function from `useTranslation` hook, not storing translations in state:

```typescript
// ❌ WRONG - Translations won't update
const title = t('header.title')
return <h1>{title}</h1>

// ✅ CORRECT - Translations update when language changes
return <h1>{t('header.title')}</h1>
```

---

## Implementation

When this command is invoked:

1. Ask user for the file path if not provided
2. Read and analyze the target file
3. Extract all text strings systematically
4. Create translation files with proper translations
5. Update the component with i18n hooks
6. Update configuration files
7. Show summary of changes made
8. Provide testing instructions
