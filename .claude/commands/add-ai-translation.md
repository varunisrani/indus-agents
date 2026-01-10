---
name: add-ai-translation
description: Add AI-powered translation to any page using Groq API for database content and i18next for UI strings (8 languages)
tags: [ai, translation, groq, i18next, internationalization]
---

# Add AI Translation to Page

Add complete AI-powered translation to any Next.js page using:
- **Client-Side**: Groq API + Supabase cache for database content via `/api/translate/batch`
- **Client-Side**: react-i18next for UI strings
- **Languages**: en, ja, hi, ta, te, zh-CN, ko, ha

## Usage

```
/add-ai-translation <page-path>
```

**Examples:**
```
/add-ai-translation /events
/add-ai-translation /pastor-dashboard
/add-ai-translation /member-profile
```

---

## Implementation Workflow

### PHASE 1: Analyze Page 🔍

1. Find page file: `app/[path]/page.tsx`
2. Identify all components used
3. List database fields needing translation:
   - Names (first_name, last_name, etc.)
   - Addresses (address, city, state, country)
   - Descriptions, notes, bio
   - Status labels
   - Custom text fields
4. List UI strings needing translation:
   - Headers, titles, breadcrumbs
   - Button labels
   - Section headings
   - Form labels
   - Dialog messages
   - Error/success messages

**DO NOT Translate:**
- IDs, email addresses, phone numbers
- Dates, timestamps, numbers, monetary values
- URLs, boolean values, technical identifiers

---

### PHASE 2: Client-Side Database Translation 🚀

**CRITICAL: Use CLIENT-SIDE translation (like /membermanagement), NOT server-side translation**

Server actions should fetch data WITHOUT translation. Translation happens in the client-side hook.

**Step 1: Server Action - NO TRANSLATION**

`app/[path]/actions.ts`:
```typescript
'use server';

// Server action fetches data WITHOUT translation
export async function getData(params: any) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_MEMBER_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_MEMBER_ANON_KEY!
  );

  const { data } = await supabase
    .from('table_name')
    .select('*, related_table(*)')
    .eq('id', params.id);

  // Return raw data - NO translation here
  return {
    success: true,
    data: data
  };
}
```

**Step 2: Create Custom Hook with Translation**

`app/[path]/hooks/useData.ts`:
```typescript
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type { Locale } from '@/lib/types/translation.types';
import { logger } from '@/lib/utils/logger';
import { getData } from '../actions';

// Type definitions
interface TranslatableField {
  field: string;
  text: string;
  memberId: string;
}

interface TranslationResult {
  field: string;
  translated: string;
}

// Helper: Extract translatable fields from data
function extractTranslatableFields(items: any[]): TranslatableField[] {
  const fields: TranslatableField[] = [];

  items.forEach(item => {
    // Add each translatable field
    if (item.first_name) {
      fields.push({
        field: `${item.id}_first_name`,
        text: item.first_name,
        memberId: item.id
      });
    }
    if (item.last_name) {
      fields.push({
        field: `${item.id}_last_name`,
        text: item.last_name,
        memberId: item.id
      });
    }
    if (item.address) {
      fields.push({
        field: `${item.id}_address`,
        text: item.address,
        memberId: item.id
      });
    }
    // Add more fields as needed
  });

  return fields.filter(f => f.text && f.text.trim().length > 0);
}

// Helper: Apply translations to data
function applyTranslations(items: any[], translations: TranslationResult[]): any[] {
  const translationMap = new Map(
    translations.map(t => [t.field, t.translated])
  );

  return items.map(item => ({
    ...item,
    first_name: translationMap.get(`${item.id}_first_name`) || item.first_name,
    last_name: translationMap.get(`${item.id}_last_name`) || item.last_name,
    address: translationMap.get(`${item.id}_address`) || item.address,
    // Apply more fields as needed
  }));
}

// Helper: Call client-side translation API
async function translateData(
  fields: TranslatableField[],
  targetLocale: Locale
): Promise<TranslationResult[]> {
  try {
    // Client-side batching: split into chunks of 150 items
    const BATCH_SIZE = 150;
    const batches: TranslatableField[][] = [];

    for (let i = 0; i < fields.length; i += BATCH_SIZE) {
      batches.push(fields.slice(i, i + BATCH_SIZE));
    }

    logger.debug(`📦 Client-side batching: ${batches.length} batches for ${fields.length} fields`);

    // Process batches sequentially
    const allTranslations: TranslationResult[] = [];

    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      logger.debug(`🔄 Processing batch ${i + 1}/${batches.length} (${batch.length} items)`);

      const response = await fetch('/api/translate/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: batch,
          sourceLocale: 'en' as Locale,
          targetLocale,
        }),
      });

      if (!response.ok) {
        throw new Error(`Translation API error: ${response.statusText}`);
      }

      const data = await response.json();
      allTranslations.push(...(data.translations || []));
      logger.debug(`✅ Batch ${i + 1} complete`);
    }

    return allTranslations;
  } catch (error) {
    logger.error('❌ Translation API call failed:', error);
    throw error;
  }
}

export function useData() {
  const { i18n } = useTranslation();
  const currentLocale = (i18n.language || 'en') as Locale;

  const [data, setData] = useState<any[]>([]);
  const [translatedData, setTranslatedData] = useState<any[]>([]);
  const [translationLoading, setTranslationLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch data from server (no translation)
  const fetchData = useCallback(async (params: any) => {
    setIsLoading(true);
    try {
      const result = await getData(params);
      if (result.success) {
        setData(result.data);
      }
    } catch (error) {
      logger.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Translate data on client side
  const translateItems = useCallback(async (items: any[], locale: Locale) => {
    if (locale === 'en') {
      setTranslatedData(items);
      setTranslationLoading(false);
      return;
    }

    if (items.length === 0) {
      setTranslatedData([]);
      setTranslationLoading(false);
      return;
    }

    setTranslationLoading(true);
    try {
      logger.debug(`🌐 Translating ${items.length} items to ${locale}...`);

      const fields = extractTranslatableFields(items);
      const results = await translateData(fields, locale);
      const translated = applyTranslations(items, results);

      setTranslatedData(translated);
      logger.debug(`✅ Translation complete`);
    } catch (error) {
      logger.error('🔥 Translation failed, using original data:', error);
      setTranslatedData(items);
    } finally {
      setTranslationLoading(false);
    }
  }, []);

  // Watch for locale changes and retranslate
  useEffect(() => {
    if (data.length > 0) {
      logger.debug(`🔄 Locale changed to ${currentLocale}, triggering translation...`);
      translateItems(data, currentLocale);
    } else {
      setTranslatedData([]);
    }
  }, [currentLocale, data, translateItems]);

  return {
    data,
    translatedData,
    translationLoading,
    isLoading,
    fetchData
  };
}
```

**Step 3: Use Hook in Component**

```typescript
'use client';

import { useData } from './hooks/useData';
import { useTranslation } from 'react-i18next';

export default function Component() {
  const { t } = useTranslation('[page-name]');
  const { translatedData, translationLoading, isLoading, fetchData } = useData();

  useEffect(() => {
    fetchData({ /* params */ });
  }, []);

  if (isLoading || translationLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {translatedData.map(item => (
        <div key={item.id}>
          <h2>{item.first_name} {item.last_name}</h2>
          <p>{item.address}</p>
        </div>
      ))}
    </div>
  );
}
```

---

### PHASE 3: i18next Translation Files 📝

**Create `locales/en/[page-name].json`:**

```json
{
  "header": {
    "title": "Page Title",
    "breadcrumb": "Breadcrumb"
  },
  "sections": {
    "mainSection": "Main Section Title"
  },
  "buttons": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  },
  "labels": {
    "name": "Name",
    "email": "Email",
    "phone": "Phone"
  },
  "messages": {
    "success": "Success!",
    "error": "An error occurred",
    "loading": "Loading..."
  },
  "dialogs": {
    "confirmDelete": "Are you sure you want to delete?",
    "confirmCancel": "Are you sure you want to cancel?"
  }
}
```

**Create translations for 7 other languages:**
- `locales/ja/[page-name].json` (Japanese)
- `locales/hi/[page-name].json` (Hindi)
- `locales/ta/[page-name].json` (Tamil)
- `locales/te/[page-name].json` (Telugu)
- `locales/zh-CN/[page-name].json` (Simplified Chinese)
- `locales/ko/[page-name].json` (Korean)
- `locales/ha/[page-name].json` (Hausa)

**Translation Guidelines:**
- Use natural, contextually appropriate translations
- Keep technical terms in original form or transliterate
- Maintain consistent tone across languages
- Preserve placeholders like `{{name}}`

---

### PHASE 4: Update Components with i18next 🎨

**For each component, add:**

```typescript
'use client';

import { useTranslation } from 'react-i18next';

export default function Component({ data }) {
  const { t } = useTranslation('[page-name]');

  return (
    <div>
      <h1>{t('header.title')}</h1>
      <button>{t('buttons.save')}</button>
      <p>{t('labels.name')}: {data.name}</p>
    </div>
  );
}
```

**Update these components:**
1. Main layout component
2. Header/breadcrumb component
3. Sidebar component
4. Form components
5. Dialog/modal components
6. Any component with hardcoded text

---

### PHASE 5: Verify Middleware (Optional) ✅

Middleware already handles i18next cookie management. For client-side translation, you typically don't need to modify middleware.

If you need locale-aware routes to be public (like `/ja/some-page`), add them to `isPublicRoute`:

```typescript
const isPublicRoute = createRouteMatcher([
  // ... existing routes
  "/ja/[your-page-path](.*)",
  "/hi/[your-page-path](.*)",
  "/ta/[your-page-path](.*)",
  "/te/[your-page-path](.*)",
  "/zh-CN/[your-page-path](.*)",
  "/ko/[your-page-path](.*)",
  "/ha/[your-page-path](.*)",
]);
```

**Note:** With client-side translation, middleware doesn't need to set `x-locale` header since translation happens in browser, not on server.

---

### PHASE 6: Testing 🧪

**Test all 8 languages:**

```
http://localhost:3002/[path]              (English)
http://localhost:3002/ja/[path]           (Japanese)
http://localhost:3002/hi/[path]           (Hindi)
http://localhost:3002/ta/[path]           (Tamil)
http://localhost:3002/te/[path]           (Telugu)
http://localhost:3002/zh-CN/[path]        (Chinese)
http://localhost:3002/ko/[path]           (Korean)
http://localhost:3002/ha/[path]           (Hausa)
```

**Verification Checklist:**
- [ ] Database fields are translated (names, addresses, etc.)
- [ ] UI strings are translated (buttons, labels, etc.)
- [ ] Dialog messages are translated
- [ ] Growth stage labels are translated (if applicable)
- [ ] Second page load is instant (cache hit)
- [ ] No errors in browser console
- [ ] No errors in server console
- [ ] Layout looks correct in all languages
- [ ] Long translations don't break layout
- [ ] Check Network tab: `/api/translate/batch` calls visible
- [ ] First load shows translation batches in console
- [ ] Second load has no translation logs (cache hit)

**Cache Verification:**
```
First load:  Should see "🔄 Translating..." logs in BROWSER console
             Should see /api/translate/batch in Network tab
Second load: Should be instant, no translation logs, no API calls
```

---

## Quick Reference

### Translation Architecture

```
User visits /ja/member-profile/123
    ↓
Middleware extracts locale ('ja') → sets i18next cookie
    ↓
page.tsx renders with i18next (syncs from cookie)
    ↓
Component calls custom hook (useData)
    ↓
Hook calls server action: getData()
    ↓
Server action fetches raw data from Supabase (NO translation)
    ↓
Raw data returned to client hook
    ↓
Hook detects locale from i18next.language
    ↓
Hook calls translateData() with locale
    ↓
translateData() calls /api/translate/batch (CLIENT-SIDE)
    ↓
    ├─ API checks Supabase translation_cache
    ├─ Cache HIT: Returns instantly
    └─ Cache MISS: Calls Groq API → Stores in cache → Returns
    ↓
Translations returned to hook
    ↓
Hook applies translations to data
    ↓
Hook sets translatedData state
    ↓
Component renders with translated data
    ↓
UI strings translated via i18next
```

**Key Differences from Server-Side Approach:**
- ✅ Translation happens on CLIENT-SIDE (browser)
- ✅ Uses `/api/translate/batch` endpoint (fetch from browser)
- ✅ Works with server actions called from client components
- ✅ Locale from i18next, NOT from headers
- ✅ Translation triggered by useEffect watching locale changes
- ❌ NO `headers()` usage in server actions
- ❌ NO `translateFields()` in server actions

### Files Modified

**Always:**
- `app/[path]/actions.ts` - Server action WITHOUT translation
- `app/[path]/hooks/useData.ts` - Custom hook WITH client-side translation
- `app/[path]/page.tsx` or component - Use custom hook
- `locales/en/[page-name].json` - Create English strings
- `locales/ja/[page-name].json` - Create Japanese strings
- `locales/hi/[page-name].json` - Create Hindi strings
- `locales/ta/[page-name].json` - Create Tamil strings
- `locales/te/[page-name].json` - Create Telugu strings
- `locales/zh-CN/[page-name].json` - Create Chinese strings
- `locales/ko/[page-name].json` - Create Korean strings
- `locales/ha/[page-name].json` - Create Hausa strings

**Sometimes:**
- `middleware.ts` - Add locale routes if needed

---

## Common Issues & Fixes

### Issue: ⚠️ CRITICAL - Translation not working (Server-Side Approach Used)

**Symptoms:**
- Database fields still in English
- No translation logs in console
- Server actions called from client components

**Root Cause:**
You used the OLD server-side translation approach where server actions try to read locale from headers. **This does NOT work** when server actions are called from client components.

**Solution:**
Use CLIENT-SIDE translation (like /membermanagement):
1. Server action fetches data WITHOUT translation
2. Custom hook (useData) translates data client-side
3. Hook calls `/api/translate/batch` via fetch
4. Hook gets locale from `i18n.language`, NOT headers
5. useEffect watches locale changes and retranslates

**Code Pattern:**
```typescript
// ❌ WRONG - Server action with translation
export async function getData(id: string) {
  const headersList = await headers();
  const locale = headersList.get('x-locale'); // Won't work!
  const translations = await translateFields(fields, locale);
}

// ✅ CORRECT - Server action without translation
export async function getData(id: string) {
  const { data } = await supabase.from('table').select('*');
  return { success: true, data }; // Return raw data
}

// ✅ CORRECT - Client hook with translation
export function useData() {
  const { i18n } = useTranslation();
  const locale = i18n.language; // Get locale from i18next

  useEffect(() => {
    if (data.length > 0) {
      translateItems(data, locale); // Client-side translation
    }
  }, [locale, data]);
}
```

### Issue: Translation not working (other causes)

**Symptoms:**
- Database fields still in English
- No translation logs in console

**Solutions:**
1. Check server is running on correct port (look at terminal output)
2. Clear Next.js cache: `rm -rf .next`
3. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. Check Groq API key exists in `.env`: `GROQ_API_KEY=...`
5. Look for errors in browser console (client-side translation)
6. Check network tab for `/api/translate/batch` calls

### Issue: UI strings not translating

**Symptoms:**
- Buttons/labels still in English
- Translation keys showing instead of text

**Solutions:**
1. Verify translation files exist in `locales/[locale]/[page-name].json`
2. Check `useTranslation('[page-name]')` uses correct namespace
3. Verify translation keys match JSON structure exactly
4. Check browser console for i18next errors

### Issue: Translation is slow

**Symptoms:**
- Page takes 2-3 seconds to load every time
- No cache hits

**Solutions:**
1. Check Supabase `translation_cache` table exists
2. Verify cache writes are working (check database)
3. Look for cache errors in server logs
4. Check if `memberId` is being passed correctly to `translateFields()`

### Issue: Some fields translate, others don't

**Symptoms:**
- Names translate but addresses don't
- Inconsistent translation

**Solutions:**
1. Check all fields are in the `fields` array
2. Verify fields have non-empty text: `.filter(f => f.text && f.text.trim().length > 0)`
3. Check for null/undefined values in database
4. Look for translation errors in server logs

---

## Performance Notes

- **First load**: 2-3 seconds (Groq API call via `/api/translate/batch`)
- **Subsequent loads**: <100ms (cache hit from Supabase)
- **Cache storage**: Supabase `translation_cache` table
- **Cache duration**: Permanent (unless manually cleared)
- **Translation cost**: ~$0.005 per page first load
- **Model**: llama-3.3-70b-versatile (Groq)
- **Batching**: 150 fields per API call to avoid rate limits
- **Client-side**: Translation happens in browser, not server
- **Network**: Check browser DevTools Network tab for `/api/translate/batch` calls

---

## Translation Best Practices

### Database Content Translation
- **Names**: Transliterate (John → ジョン in Japanese)
- **Addresses**: Preserve street names, translate city/state/country
- **Descriptions**: Full translation with context awareness
- **Status labels**: Translate to equivalent terms

### UI String Translation
- **Consistency**: Use same terms across pages
- **Context**: Consider where text appears
- **Length**: Watch for layout breaks with long translations
- **Tone**: Match formality level of original

### What NOT to Translate
- Email addresses
- Phone numbers (keep format)
- URLs and endpoints
- Technical identifiers
- Code snippets
- Database IDs

---

## Example Usage

```bash
User: "Add AI translation to /events page"

Claude:
1. Analyzes app/events/page.tsx and components
2. Identifies database fields: event.name, event.description, event.location
3. Identifies UI strings: "Events", "Create Event", "Filter", etc.
4. Creates app/events/actions.ts with getData() (NO translation)
5. Creates app/events/hooks/useEventsData.ts with CLIENT-SIDE translation:
   - extractTranslatableFields()
   - translateData() calling /api/translate/batch
   - applyTranslations()
   - useEffect watching locale changes
6. Updates page.tsx to use custom hook
7. Creates locales/en/events.json
8. Creates 7 other language files (ja, hi, ta, te, zh-CN, ko, ha)
9. Updates EventsList, EventCard components with useTranslation
10. Tests in all 8 languages
11. Verifies cache is working (checks Network tab for /api/translate/batch)

Result: Complete translation in 8 languages with client-side caching!
```

**Reference Implementation:** See `/membermanagement` page for working example.

---

## End of Command

This command provides a **complete translation solution** that combines:
- CLIENT-SIDE AI-powered database translation (Groq API via `/api/translate/batch`)
- Professional UI string translation (react-i18next)
- Intelligent caching (Supabase)
- Support for 8 languages
- Production-ready performance
