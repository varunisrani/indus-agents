# Todo Application - Comprehensive Specification

## Executive Summary

A modern, full-featured todo application built with Next.js 14 (App Router), TypeScript, and shadcn/ui components. The application provides a clean, responsive interface for task management with real-time updates, persistent storage, and an excellent user experience.

---

## 1. Core Features

### 1.1 Task Management
- **Create Task**
  - Quick add via input field at top of list
  - Detailed creation via modal/form
  - Support for bulk import (future enhancement)
  
- **Edit Task**
  - Inline editing for title
  - Full edit modal for all properties
  - Auto-save on field change (debounced)

- **Delete Task**
  - Single task deletion with confirmation
  - Bulk delete for completed tasks
  - Soft delete with trash bin (30-day retention)

- **Task Completion**
  - Checkbox/toggle for completion status
  - Visual distinction (strikethrough, dimmed)
  - Completion animation
  - Undo completion (with toast notification)

### 1.2 Task Properties
- **Title**: Required, max 200 characters
- **Description**: Optional, rich text support (markdown)
- **Priority**: Low / Medium / High / Critical
- **Due Date**: Optional date and time picker
- **Status**: Todo / In Progress / Completed / Archived
- **Tags/Categories**: Optional, multi-select
- **Created At**: Auto-generated timestamp
- **Updated At**: Auto-generated timestamp

### 1.3 Organization & Filtering
- **View Modes**
  - All tasks
  - Active tasks (not completed)
  - Completed tasks
  - By priority
  - By due date (overdue, today, upcoming)
  
- **Sorting**
  - By due date (ascending/descending)
  - By priority (high to low)
  - By creation date
  - By completion status
  - Manual drag-and-drop reordering

- **Search**: Full-text search across title and description
- **Tag Filtering**: Filter by one or multiple tags

### 1.4 User Experience Features
- **Keyboard Shortcuts**
  - `Ctrl/Cmd + N`: New task
  - `Ctrl/Cmd + F`: Focus search
  - `Ctrl/Cmd + K`: Quick command palette
  - `Enter`: Save/Submit
  - `Escape`: Cancel/Close modal
  
- **Drag & Drop**: Reorder tasks within lists
- **Toast Notifications**: Feedback for all actions
- **Loading States**: Skeleton screens during data fetch
- **Error Handling**: Graceful error messages with retry options
- **Empty States**: Helpful prompts when no tasks exist
- **Responsive Design**: Mobile-first, works on all screen sizes

### 1.5 Advanced Features (Future)
- **Subtasks**: Nested task hierarchy
- **Recurring Tasks**: Daily, weekly, monthly patterns
- **Reminders**: Push notifications for due tasks
- **Collaboration**: Share lists with other users
- **Export**: JSON, CSV, PDF formats
- **Themes**: Light/dark mode toggle
- **Statistics**: Completion rate, productivity charts

---

## 2. Data Model

### 2.1 Task Entity

```typescript
interface Task {
  // Primary identifiers
  id: string;                    // UUID v4
  userId?: string;               // Optional: for multi-user support
  
  // Core properties
  title: string;                 // Required, max 200 chars
  description?: string;          // Optional, markdown supported
  status: TaskStatus;            // Enum: 'todo' | 'in-progress' | 'completed' | 'archived'
  priority: TaskPriority;        // Enum: 'low' | 'medium' | 'high' | 'critical'
  
  // Dates
  dueDate?: Date;                // ISO 8601 datetime
  completedAt?: Date;            // Auto-set when status = 'completed'
  createdAt: Date;               // Auto-generated
  updatedAt: Date;               // Auto-updated on changes
  
  // Organization
  tags: string[];                // Array of tag strings
  order: number;                 // For manual sorting
  
  // Soft delete
  isDeleted: boolean;            // Soft delete flag
  deletedAt?: Date;              // Auto-set on delete
  
  // Metadata
  completedSubtasks?: number;    // For future subtask feature
  totalSubtasks?: number;        // For future subtask feature
}

type TaskStatus = 'todo' | 'in-progress' | 'completed' | 'archived';
type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
```

### 2.2 Tag Entity (Future)

```typescript
interface Tag {
  id: string;
  name: string;
  color: string;                 // Hex color code
  userId?: string;
}
```

### 2.3 User Settings (Future)

```typescript
interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  defaultView: TaskView;
  defaultSort: SortOption;
  notificationsEnabled: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### 2.4 Data Validation Rules

```typescript
// Validation schemas (using Zod)
const TaskSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  description: z.string().max(5000).optional(),
  status: z.enum(['todo', 'in-progress', 'completed', 'archived']),
  priority: z.enum(['low', 'medium', 'high', 'critical']),
  dueDate: z.date().optional(),
  tags: z.array(z.string().max(50)).max(10),
  order: z.number().int().min(0),
});
```

---

## 3. User Interface

### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  Header                                                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │ Logo/Brand   │  │ Search Bar  │  │ Actions/Theme    │ │
│  └──────────────┘  └─────────────┘  └──────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Main Content                                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Quick Add Task Input                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌─────────┬─────────────────────────────────────────┐  │
│  │ Sidebar │  Task List Area                         │  │
│  │         │                                         │  │
│  │ Filters │  ┌─────────────────────────────────┐   │  │
│  │ - All   │  │ Task Card 1                     │   │  │
│  │ - Todo  │  ├─────────────────────────────────┤   │  │
│  │ - Done  │  │ Task Card 2                     │   │  │
│  │         │  ├─────────────────────────────────┤   │  │
│  │ Tags    │  │ Task Card 3                     │   │  │
│  │ - Work  │  └─────────────────────────────────┘   │  │
│  │ - Home │                                         │  │
│  └─────────┴─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Component Hierarchy

```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── SearchBar
│   │   └── ActionButtons (ThemeToggle, CommandPalette)
│   ├── Sidebar
│   │   ├── FilterList
│   │   ├── TagCloud
│   │   └── StatsSummary
│   └── MainContent
│       ├── QuickAddTask
│       ├── TaskFilters (Sort, View toggle)
│       └── TaskList
│           └── TaskCard (repeated)
│               ├── Checkbox
│               ├── TaskTitle
│               ├── TaskMetadata (priority, due date)
│               ├── TaskActions (Edit, Delete)
│               └── TagList
├── Modals
│   ├── TaskFormModal (Create/Edit)
│   ├── DeleteConfirmModal
│   └── SettingsModal
└── Shared
    ├── Toast
    ├── LoadingSpinner
    ├── EmptyState
    └── ErrorBoundary
```

### 3.3 Task Card Design

```
┌────────────────────────────────────────────────────┐
│  [✓]  Task title with priority badge                │
│       ┌──────────┐  ┌──────────────────┐           │
│       │ HIGH     │  │ Due: Jan 15, 2025│           │
│       └──────────┘  └──────────────────┘           │
│       Optional description preview...               │
│       ┌─────┐ ┌─────┐ ┌─────┐                       │
│       │Work│ │Home│ │+Tag│                       │
│       └─────┘ └─────┘ └─────┘                       │
│                              [Edit] [Delete]        │
└────────────────────────────────────────────────────┘
```

### 3.4 Responsive Breakpoints

- **Mobile** (< 640px): Single column, collapsible sidebar (drawer)
- **Tablet** (640px - 1024px): Sidebar becomes icon-only rail
- **Desktop** (> 1024px): Full sidebar with labels

### 3.5 Accessibility (WCAG 2.1 AA)
- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators visible
- Color contrast minimum 4.5:1
- Screen reader announcements for state changes

---

## 4. Technical Stack

### 4.1 Framework & Runtime
- **Framework**: Next.js 14 (App Router)
  - Server Components for performance
  - Client Components for interactivity
  - Built-in API routes for backend
  - File-based routing
  
- **Runtime**: Node.js 18+ / Edge runtime where applicable

### 4.2 Language & Type Safety
- **Language**: TypeScript 5+
  - Strict mode enabled
  - Path aliases configured
  - Type checking in CI/CD
  
- **Linting**: ESLint + Prettier
  - Airbnb style guide
  - Import sorting
  - Auto-format on save

### 4.3 UI Components & Styling
- **Component Library**: shadcn/ui (Radix UI primitives)
  - Accessible, unstyled components
  - Full customization via Tailwind
  - Excellent keyboard navigation
  
- **Styling**: Tailwind CSS 3.4+
  - Utility-first approach
  - Design tokens for consistency
  - Dark mode support
  
- **Icons**: Lucide React
  - Tree-shakeable
  - Consistent design
  - 1000+ icons

- **Animations**: Framer Motion
  - Smooth transitions
  - Page transitions
  - Micro-interactions

### 4.4 Forms & Validation
- **Form Library**: React Hook Form 7
  - Minimal re-renders
  - Built-in validation
  - TypeScript support
  
- **Validation**: Zod 3
  - Schema validation
  - Type inference
  - Error messages

### 4.5 State Management
- **Client State**: Zustand 4
  - Lightweight (no boilerplate)
  - TypeScript support
  - DevTools integration
  
- **Server State**: TanStack Query 5
  - Caching and revalidation
  - Optimistic updates
  - Background refetching
  - Offline support

### 4.6 Data Persistence
- **Primary Storage**: IndexedDB (via Dexie.js)
  - Offline-first
  - 250MB+ storage
  - Structured data queries
  - Browser-native, no server needed
  
- **Optional Backend Sync**: Supabase (future)
  - PostgreSQL database
  - Real-time subscriptions
  - Auth integration
  - Row-level security

### 4.7 Development Tools
- **Package Manager**: pnpm (fast, efficient)
- **Monorepo**: Turborepo (if scaling)
- **Testing**: Vitest + Testing Library
- **E2E Testing**: Playwright
- **Git Hooks**: Husky + lint-staged
- **CI/CD**: GitHub Actions

### 4.8 Additional Libraries
- **Date Handling**: date-fns (lightweight alternative to Moment.js)
- **Markdown Rendering**: react-markdown
- **Drag & Drop**: @dnd-kit/core
- **Hotkeys**: react-hotkeys-hook
- **Notifications**: react-hot-toast

---

## 5. State Management

### 5.1 State Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client State                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Zustand Stores                                    │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │  │
│  │  │ TaskStore   │ │ FilterStore │ │ UIStore     │  │  │
│  │  │ - tasks     │ │ - filter    │ │ - theme     │  │  │
│  │  │ - loading   │ │ - sort      │ │ - modal     │  │  │
│  │  │ - error     │ │ - search    │ │ - sidebar   │  │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                   Server State (TanStack Query)          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Queries & Mutations                              │  │
│  │  - useTasks()                                     │  │
│  │  - useCreateTask()                                │  │
│  │  - useUpdateTask()                                │  │
│  │  - useDeleteTask()                                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                   Persistence Layer                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  IndexedDB (Dexie.js)                              │  │
│  │  - Tasks table                                     │  │
│  │  - Tags table                                      │  │
│  │  - Settings table                                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Zustand Store Implementation

```typescript
// stores/taskStore.ts
interface TaskStore {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  
  // Actions
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  deleteTask: (id: string) => void;
  toggleTaskStatus: (id: string) => void;
  
  // Computed
  getActiveTasks: () => Task[];
  getCompletedTasks: () => Task[];
  getOverdueTasks: () => Task[];
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,
  
  setTasks: (tasks) => set({ tasks }),
  
  addTask: (task) => set((state) => ({
    tasks: [...state.tasks, task]
  })),
  
  updateTask: (id, updates) => set((state) => ({
    tasks: state.tasks.map(task =>
      task.id === id ? { ...task, ...updates } : task
    )
  })),
  
  deleteTask: (id) => set((state) => ({
    tasks: state.tasks.filter(task => task.id !== id)
  })),
  
  toggleTaskStatus: (id) => set((state) => ({
    tasks: state.tasks.map(task =>
      task.id === id
        ? {
            ...task,
            status: task.status === 'completed' ? 'todo' : 'completed',
            completedAt: task.status === 'completed' ? undefined : new Date()
          }
        : task
    )
  })),
  
  getActiveTasks: () => get().tasks.filter(t => t.status !== 'completed'),
  getCompletedTasks: () => get().tasks.filter(t => t.status === 'completed'),
  getOverdueTasks: () => get().tasks.filter(t => 
    t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'completed'
  ),
}));
```

### 5.3 Filter Store

```typescript
// stores/filterStore.ts
interface FilterStore {
  filter: 'all' | 'active' | 'completed';
  sortBy: 'dueDate' | 'priority' | 'createdAt' | 'manual';
  sortOrder: 'asc' | 'desc';
  searchQuery: string;
  selectedTags: string[];
  
  setFilter: (filter: FilterStore['filter']) => void;
  setSortBy: (sortBy: FilterStore['sortBy']) => void;
  setSearchQuery: (query: string) => void;
  toggleTag: (tag: string) => void;
  resetFilters: () => void;
}
```

### 5.4 Data Flow

1. **Initial Load**: 
   - App mounts → TanStack Query fetches from IndexedDB
   - Data populates Zustand store
   - Components render from store

2. **User Action** (e.g., Create Task):
   - Form submission → Optimistic update to Zustand
   - TanStack Mutation sends to IndexedDB
   - On success: confirm update
   - On error: rollback optimistic update

3. **Filtering/Sorting**:
   - Filter store updates
   - Derived selectors compute filtered list
   - Components re-render with filtered data

---

## 6. API/Data Persistence

### 6.1 Storage Strategy: IndexedDB (Offline-First)

**Why IndexedDB?**
- No server required (pure client-side app)
- Works offline
- Large storage capacity (250MB+)
- Structured data queries
- Persistent across sessions
- Fast for local operations

### 6.2 Database Schema (Dexie.js)

```typescript
// db/index.ts
import Dexie, { Table } from 'dexie';

export class TodoDatabase extends Dexie {
  tasks!: Table<Task>;
  tags!: Table<Tag>;
  settings!: Table<UserSettings>;

  constructor() {
    super('TodoAppDB');
    this.version(1).stores({
      tasks: 'id, userId, status, priority, dueDate, createdAt, order',
      tags: 'id, userId, name',
      settings: 'userId'
    });
  }
}

export const db = new TodoDatabase();
```

### 6.3 Data Access Layer

```typescript
// lib/db/tasks.ts
import { db } from '@/db';
import { Task } from '@/types';

export const taskRepository = {
  // Read all
  getAll: async (): Promise<Task[]> => {
    return await db.tasks.orderBy('order').toArray();
  },
  
  // Read with filters
  getByStatus: async (status: Task['status']): Promise<Task[]> => {
    return await db.tasks.where('status').equals(status).toArray();
  },
  
  // Create
  create: async (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>): Promise<Task> => {
    const newTask: Task = {
      ...task,
      id: crypto.randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    await db.tasks.add(newTask);
    return newTask;
  },
  
  // Update
  update: async (id: string, updates: Partial<Task>): Promise<void> => {
    await db.tasks.update(id, {
      ...updates,
      updatedAt: new Date()
    });
  },
  
  // Delete (soft)
  softDelete: async (id: string): Promise<void> => {
    await db.tasks.update(id, {
      isDeleted: true,
      deletedAt: new Date(),
      updatedAt: new Date()
    });
  },
  
  // Delete (permanent)
  delete: async (id: string): Promise<void> => {
    await db.tasks.delete(id);
  },
  
  // Bulk operations
  bulkCreate: async (tasks: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>[]): Promise<Task[]> => {
    const newTasks = tasks.map(task => ({
      ...task,
      id: crypto.randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date(),
    }));
    await db.tasks.bulkAdd(newTasks);
    return newTasks;
  }
};
```

### 6.4 API Routes (Next.js - Optional Backend)

```typescript
// app/api/tasks/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { taskRepository } from '@/lib/db/tasks';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get('status');
  
  const tasks = status
    ? await taskRepository.getByStatus(status as Task['status'])
    : await taskRepository.getAll();
    
  return NextResponse.json(tasks);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const task = await taskRepository.create(body);
  return NextResponse.json(task, { status: 201 });
}

// app/api/tasks/[id]/route.ts
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json();
  await taskRepository.update(params.id, body);
  return NextResponse.json({ success: true });
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await taskRepository.delete(params.id);
  return NextResponse.json({ success: true });
}
```

### 6.5 TanStack Query Integration

```typescript
// hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskRepository } from '@/lib/db/tasks';
import { useTaskStore } from '@/stores/taskStore';
import { toast } from 'react-hot-toast';

export function useTasks() {
  const queryClient = useQueryClient();
  const setTasks = useTaskStore(state => state.setTasks);
  
  // Query
  const query = useQuery({
    queryKey: ['tasks'],
    queryFn: taskRepository.getAll,
    onSuccess: (data) => setTasks(data)
  });
  
  // Create mutation
  const createMutation = useMutation({
    mutationFn: taskRepository.create,
    onSuccess: (task) => {
      queryClient.invalidateQueries(['tasks']);
      toast.success('Task created');
    }
  });
  
  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Task> }) =>
      taskRepository.update(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks']);
      toast.success('Task updated');
    }
  });
  
  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: taskRepository.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks']);
      toast.success('Task deleted');
    }
  });
  
  return {
    ...query,
    createTask: createMutation.mutate,
    updateTask: updateMutation.mutate,
    deleteTask: deleteMutation.mutate,
  };
}
```

### 6.6 Data Sync Strategy (Future - Backend Integration)

When adding backend sync (Supabase/Firebase):

```typescript
// Sync service
class SyncService {
  private syncQueue: Task[] = [];
  
  async sync() {
    // 1. Push local changes to server
    for (const task of this.syncQueue) {
      await api.tasks.update(task.id, task);
    }
    
    // 2. Pull latest from server
    const serverTasks = await api.tasks.getAll();
    
    // 3. Merge with local (server wins for conflicts)
    await this.mergeTasks(serverTasks);
    
    // 4. Clear queue
    this.syncQueue = [];
  }
  
  async mergeTasks(serverTasks: Task[]) {
    const localTasks = await taskRepository.getAll();
    
    for (const serverTask of serverTasks) {
      const localTask = localTasks.find(t => t.id === serverTask.id);
      
      if (!localTask) {
        // New task from server
        await taskRepository.create(serverTask);
      } else if (new Date(serverTask.updatedAt) > new Date(localTask.updatedAt)) {
        // Server is newer
        await taskRepository.update(serverTask.id, serverTask);
      }
    }
  }
}
```

### 6.7 Backup & Export

```typescript
// lib/backup.ts
export async function exportData(): Promise<string> {
  const tasks = await taskRepository.getAll();
  const tags = await tagRepository.getAll();
  
  const data = {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    tasks,
    tags
  };
  
  return JSON.stringify(data, null, 2);
}

export async function importData(jsonData: string): Promise<void> {
  const data = JSON.parse(jsonData);
  
  // Validate schema
  if (!data.tasks || !Array.isArray(data.tasks)) {
    throw new Error('Invalid backup file');
  }
  
  // Clear existing data
  await db.tasks.clear();
  await db.tags.clear();
  
  // Import data
  await db.tasks.bulkAdd(data.tasks);
  if (data.tags) {
    await db.tags.bulkAdd(data.tags);
  }
  
  toast.success(`Imported ${data.tasks.length} tasks`);
}
```

---

## 7. Security & Privacy

### 7.1 Data Privacy
- All data stored locally (client-side only)
- No external API calls by default
- No telemetry or analytics
- No user tracking

### 7.2 Input Sanitization
- XSS prevention via React's built-in escaping
- CSRF protection via SameSite cookies (if backend added)
- Content Security Policy headers
- Input validation via Zod schemas

### 7.3 Future Security (Multi-User)
- Authentication: NextAuth.js
- Authorization: Row-level security (Supabase)
- Data encryption at rest
- HTTPS only
- Rate limiting

---

## 8. Performance Considerations

### 8.1 Optimization Strategies
- **Code Splitting**: Route-based splitting with Next.js
- **Lazy Loading**: Components loaded on demand
- **Virtual Scrolling**: For large task lists (react-window)
- **Debouncing**: Search input (300ms)
- **Memoization**: React.memo for expensive components
- **Image Optimization**: Next.js Image component (if avatars added)

### 8.2 Bundle Size Targets
- Initial JS: < 100KB gzipped
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s

### 8.3 IndexedDB Performance
- Indexes on frequently queried fields
- Batch operations for bulk updates
- Cleanup of soft-deleted items (30-day job)

---

## 9. Testing Strategy

### 9.1 Unit Tests (Vitest)
- Store logic (Zustand)
- Repository functions
- Utility functions
- Validation schemas

### 9.2 Integration Tests
- Component interactions
- Form submissions
- Data flow from store to UI

### 9.3 E2E Tests (Playwright)
- User journeys (create, edit, delete tasks)
- Filtering and sorting
- Offline functionality
- Cross-browser testing

### 9.4 Accessibility Tests
- axe-core for automated a11y checks
- Keyboard navigation flows
- Screen reader testing (NVDA/JAWS)

---

## 10. Deployment

### 10.1 Recommended Platforms
- **Vercel** (recommended): Zero-config Next.js deployment
- **Netlify**: Alternative with great DX
- **GitHub Pages**: Static export option
- **Self-hosted**: Docker container

### 10.2 Build Configuration

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone', // For Docker
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-icons']
  }
};

module.exports = nextConfig;
```

### 10.3 Environment Variables

```bash
# .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=TodoApp
```

---

## 11. Future Enhancements

### 11.1 Phase 2 Features
- Subtasks with nested hierarchy
- Recurring tasks (daily, weekly, custom)
- Task templates
- Rich task descriptions (markdown editor)
- File attachments
- Voice input (Web Speech API)

### 11.2 Phase 3 Features
- Multi-user collaboration
- Real-time sync (WebSockets)
- Mobile apps (React Native / Capacitor)
- Calendar view
- Kanban board view
- Gantt chart for project planning
- Integrations (Google Calendar, Notion, etc.)

### 11.3 AI Features
- Smart task suggestions
- Auto-tagging using NLP
- Priority recommendations
- Due date predictions
- Summarization of long descriptions

---

## 12. Success Criteria

### 12.1 Functional Requirements
- ✅ Users can create, edit, delete, and complete tasks
- ✅ Tasks can be filtered by status, priority, due date, and tags
- ✅ Search works across all task properties
- ✅ Data persists across browser sessions
- ✅ Application works offline

### 12.2 Non-Functional Requirements
- ✅ Page load time < 2 seconds
- ✅ WCAG 2.1 AA compliant
- ✅ Works on modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Responsive on mobile, tablet, and desktop
- ✅ No console errors in production

### 12.3 User Experience
- ✅ Intuitive interface requiring no tutorial
- ✅ Fast, responsive interactions
- ✅ Clear feedback for all actions
- ✅ Graceful error handling
- ✅ Delightful micro-interactions

---

## Appendix A: File Structure

```
todo-app/
├── app/
│   ├── (routes)/
│   │   ├── page.tsx                 # Home page
│   │   ├── layout.tsx               # Root layout
│   │   └── loading.tsx              # Loading state
│   ├── api/
│   │   └── tasks/
│   │       ├── route.ts             # GET, POST
│   │       └── [id]/
│   │           └── route.ts         # PATCH, DELETE
│   └── globals.css                  # Global styles
├── components/
│   ├── ui/                          # shadcn components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── task/
│   │   ├── TaskCard.tsx
│   │   ├── TaskForm.tsx
│   │   ├── TaskList.tsx
│   │   └── QuickAdd.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainContent.tsx
│   └── shared/
│       ├── Toast.tsx
│       ├── Loading.tsx
│       └── ErrorBoundary.tsx
├── lib/
│   ├── db/
│   │   ├── index.ts                 # Dexie setup
│   │   └── tasks.ts                 # Task repository
│   ├── hooks/
│   │   ├── useTasks.ts
│   │   ├── useFilters.ts
│   │   └── useKeyboardShortcuts.ts
│   ├── utils/
│   │   ├── date.ts
│   │   ├── validation.ts
│   │   └── cn.ts                    # Class name utility
│   └── constants.ts
├── stores/
│   ├── taskStore.ts
│   ├── filterStore.ts
│   └── uiStore.ts
├── types/
│   ├── task.ts
│   ├── filter.ts
│   └── index.ts
├── public/
│   └── icons/
├── .env.local
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## Appendix B: Package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-toast": "^1.1.5",
    "dexie": "^3.2.4",
    "framer-motion": "^10.16.4",
    "lucide-react": "^0.294.0",
    "react-hook-form": "^7.48.2",
    "zod": "^3.22.4",
    "@tanstack/react-query": "^5.12.2",
    "zustand": "^4.4.7",
    "date-fns": "^2.30.0",
    "react-hot-toast": "^2.4.1",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.9.0",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "typescript": "^5.2.2",
    "tailwindcss": "^3.3.5",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.53.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.3",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "playwright": "^1.40.0"
  }
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-15  
**Status**: Ready for Implementation
