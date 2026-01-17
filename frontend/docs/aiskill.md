---
name: TypeScript Expert Coder
description: Comprehensive guide for expert-level TypeScript development with React, focusing on type safety, best practices, and modern patterns
version: 1.0.0
author: AI Assistant
tags: [typescript, react, frontend, best-practices, patterns]
---

# TypeScript Expert Coder Skill

A comprehensive guide for writing production-grade TypeScript code with React, emphasizing type safety, maintainability, and modern development patterns.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Type System Mastery](#type-system-mastery)
3. [React + TypeScript Patterns](#react--typescript-patterns)
4. [State Management](#state-management)
5. [API Integration](#api-integration)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Testing Strategies](#testing-strategies)
9. [Code Organization](#code-organization)
10. [Common Pitfalls](#common-pitfalls)

---

## Core Principles

### 1. Type Safety First
- **Always** prefer explicit types over `any`
- Use `unknown` instead of `any` when type is truly unknown
- Enable strict mode in `tsconfig.json`
- Leverage type inference where appropriate

```typescript
// ❌ Bad
function processData(data: any) {
  return data.value;
}

// ✅ Good
function processData<T extends { value: string }>(data: T): string {
  return data.value;
}
```

### 2. Immutability
- Use `readonly` for properties that shouldn't change
- Prefer `const` over `let`
- Use immutable update patterns

```typescript
// ✅ Good
interface User {
  readonly id: string;
  readonly name: string;
  readonly email: string;
}

const updateUser = (user: User, updates: Partial<User>): User => ({
  ...user,
  ...updates,
});
```

### 3. Composition Over Inheritance
- Favor interfaces and type composition
- Use utility types for transformations
- Leverage generics for reusability

---

## Type System Mastery

### Advanced Type Patterns

#### 1. Discriminated Unions
```typescript
type Success<T> = {
  status: 'success';
  data: T;
};

type Error = {
  status: 'error';
  error: string;
};

type Result<T> = Success<T> | Error;

function handleResult<T>(result: Result<T>) {
  if (result.status === 'success') {
    // TypeScript knows result.data exists here
    console.log(result.data);
  } else {
    // TypeScript knows result.error exists here
    console.error(result.error);
  }
}
```

#### 2. Utility Types
```typescript
// Pick specific properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit properties
type UserWithoutPassword = Omit<User, 'password'>;

// Make all properties optional
type PartialUser = Partial<User>;

// Make all properties required
type RequiredUser = Required<User>;

// Make all properties readonly
type ReadonlyUser = Readonly<User>;

// Extract return type
type FunctionReturn = ReturnType<typeof myFunction>;

// Extract parameters
type FunctionParams = Parameters<typeof myFunction>;
```

#### 3. Conditional Types
```typescript
type IsString<T> = T extends string ? true : false;

type Unwrap<T> = T extends Promise<infer U> ? U : T;

type NonNullable<T> = T extends null | undefined ? never : T;
```

#### 4. Mapped Types
```typescript
type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};
```

---

## React + TypeScript Patterns

### 1. Functional Components
```typescript
// ✅ Preferred: Function declaration with explicit return type
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  label, 
  onClick, 
  variant = 'primary',
  disabled = false 
}) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

### 2. Hooks with TypeScript
```typescript
// useState with explicit type
const [user, setUser] = useState<User | null>(null);

// useRef with proper typing
const inputRef = useRef<HTMLInputElement>(null);

// Custom hooks with generics
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}
```

### 3. Event Handlers
```typescript
// Form events
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  // Handle form submission
};

// Input events
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

// Click events
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.stopPropagation();
  // Handle click
};

// Keyboard events
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') {
    // Handle enter key
  }
};
```

### 4. Children Props
```typescript
// String children
interface Props {
  children: string;
}

// React node children
interface Props {
  children: React.ReactNode;
}

// Function as children (render props)
interface Props {
  children: (data: User) => React.ReactNode;
}

// Multiple children with specific types
interface Props {
  children: [React.ReactElement, React.ReactElement];
}
```

---

## State Management

### Zustand with TypeScript
```typescript
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      set({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
      });
    } catch (error) {
      throw error;
    }
  },

  logout: () => {
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  updateUser: (updates: Partial<User>) => {
    const currentUser = get().user;
    if (currentUser) {
      set({
        user: { ...currentUser, ...updates },
      });
    }
  },
}));
```

---

## API Integration

### Type-Safe API Client
```typescript
// API types
interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

// Generic API client
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    if (!response.ok) {
      throw await this.handleError(response);
    }
    return response.json();
  }

  async post<T, D = unknown>(
    endpoint: string, 
    data: D
  ): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw await this.handleError(response);
    }
    return response.json();
  }

  private async handleError(response: Response): Promise<ApiError> {
    const error = await response.json();
    return {
      message: error.message || 'An error occurred',
      code: error.code || 'UNKNOWN_ERROR',
      details: error.details,
    };
  }
}

// Usage with specific types
interface User {
  id: string;
  name: string;
  email: string;
}

interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
}

const api = new ApiClient('https://api.example.com');

// Type-safe API calls
const getUser = (id: string) => 
  api.get<User>(`/users/${id}`);

const createUser = (data: CreateUserRequest) => 
  api.post<User, CreateUserRequest>('/users', data);
```

---

## Error Handling

### Custom Error Types
```typescript
class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class ValidationError extends AppError {
  constructor(
    message: string,
    public fields: Record<string, string[]>
  ) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}
```

### Error Boundaries
```typescript
interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Something went wrong</div>;
    }

    return this.props.children;
  }
}
```

---

## Performance Optimization

### 1. Memoization
```typescript
// useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// useCallback for stable function references
const handleClick = useCallback(() => {
  doSomething(value);
}, [value]);

// React.memo for component memoization
const MemoizedComponent = React.memo<Props>(({ data }) => {
  return <div>{data}</div>;
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id;
});
```

### 2. Code Splitting
```typescript
// Lazy loading components
const LazyComponent = React.lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}
```

### 3. Virtual Scrolling
```typescript
interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
}

function VirtualList<T>({ items, itemHeight, renderItem }: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerHeight = 600;
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + containerHeight) / itemHeight)
  );
  
  const visibleItems = items.slice(startIndex, endIndex + 1);
  
  return (
    <div 
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight }}>
        <div style={{ transform: `translateY(${startIndex * itemHeight}px)` }}>
          {visibleItems.map((item, index) => 
            renderItem(item, startIndex + index)
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## Testing Strategies

### Unit Testing with TypeScript
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

describe('Button', () => {
  it('renders with correct label', () => {
    render(<Button label="Click me" onClick={() => {}} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button label="Click me" onClick={handleClick} />);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button label="Click me" onClick={() => {}} disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Type Testing
```typescript
// Use type assertions to test types
type AssertEqual<T, U> = T extends U ? (U extends T ? true : false) : false;

// Test that types match
const test1: AssertEqual<User, { id: string; name: string }> = true;

// Test that function returns correct type
const test2: AssertEqual<ReturnType<typeof getUser>, Promise<User>> = true;
```

---

## Code Organization

### File Structure
```
src/
├── components/          # Reusable UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   └── ...
├── features/           # Feature-based modules
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── index.ts
│   └── ...
├── hooks/             # Shared custom hooks
├── services/          # API and external services
├── store/             # State management
├── types/             # Shared type definitions
├── utils/             # Utility functions
└── App.tsx
```

### Barrel Exports
```typescript
// components/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';

// Usage
import { Button, Input, Modal } from '@/components';
```

---

## Common Pitfalls

### 1. Avoid Type Assertions
```typescript
// ❌ Bad - loses type safety
const user = data as User;

// ✅ Good - validate and narrow type
function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  );
}

if (isUser(data)) {
  // TypeScript knows data is User here
  console.log(data.name);
}
```

### 2. Avoid Non-Null Assertions
```typescript
// ❌ Bad - can cause runtime errors
const value = maybeNull!.property;

// ✅ Good - handle null case
const value = maybeNull?.property ?? defaultValue;
```

### 3. Avoid Enum (Use Union Types)
```typescript
// ❌ Avoid enums (they generate runtime code)
enum Status {
  Active = 'active',
  Inactive = 'inactive',
}

// ✅ Use const objects or union types
const Status = {
  Active: 'active',
  Inactive: 'inactive',
} as const;

type Status = typeof Status[keyof typeof Status];

// Or simply
type Status = 'active' | 'inactive';
```

### 4. Proper Async/Await Error Handling
```typescript
// ❌ Bad - unhandled promise rejection
async function fetchData() {
  const data = await api.get('/data');
  return data;
}

// ✅ Good - proper error handling
async function fetchData(): Promise<Data | null> {
  try {
    const data = await api.get<Data>('/data');
    return data;
  } catch (error) {
    console.error('Failed to fetch data:', error);
    return null;
  }
}
```

---

## Best Practices Checklist

- [ ] Enable strict mode in `tsconfig.json`
- [ ] Use explicit return types for public functions
- [ ] Prefer `interface` over `type` for object shapes
- [ ] Use `const` assertions for literal types
- [ ] Leverage utility types instead of manual transformations
- [ ] Write type guards for runtime type checking
- [ ] Use discriminated unions for complex state
- [ ] Avoid `any`, prefer `unknown` when type is uncertain
- [ ] Use generics for reusable, type-safe code
- [ ] Document complex types with JSDoc comments
- [ ] Keep components small and focused
- [ ] Use custom hooks to extract logic
- [ ] Implement proper error boundaries
- [ ] Write tests for critical paths
- [ ] Use code splitting for large bundles

---

## Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [Effective TypeScript](https://effectivetypescript.com/)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-17  
**Maintained by**: AI Assistant
