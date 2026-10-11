<!-- mermaid-ai-skills:start -->
## Mermaid Diagrams

When the user asks to create, edit, or visualize a diagram, follow the
instructions in `.github/instructions/mermaid.instructions.md`.
<!-- mermaid-ai-skills:end -->

# React + TypeScript Engineering Constitution

These rules apply to all code generated, modified, refactored, or reviewed by GitHub Copilot in this repository.

The goal is not merely to make code work.

The goal is to produce code that is:

* maintainable
* testable
* reusable
* predictable
* readable
* loosely coupled
* strongly typed
* architecturally consistent
* easy for another engineer to understand

---

# 1. Core Engineering Principles

Follow these principles by default:

1. SOLID
2. Separation of concerns
3. Single responsibility
4. Composition over inheritance
5. Dependency inversion where appropriate
6. DRY without premature abstraction
7. KISS
8. Explicit dependencies
9. Strong typing
10. Testability
11. Minimal coupling
12. High cohesion

Do not apply design patterns mechanically.

Prefer the simplest design that satisfies the requirements and preserves maintainability.

A SOLID principle may be intentionally violated when following it would create unnecessary complexity. When doing so, explain the reason.

---

# 2. EXISTING CODE FIRST

Before creating anything new, inspect the existing repository.

Always look for:

* existing components
* existing hooks
* existing utilities
* existing API clients
* existing fetch functions
* existing types
* existing validation utilities
* existing state-management patterns
* existing error-handling patterns
* existing UI components
* existing design-system components
* existing shadcn/ui components
* existing libraries already installed in package.json

NEVER create a new utility, component, hook, API client, or library abstraction before checking whether an existing solution can be reused.

Prefer:

existing solution > extending existing solution > small new abstraction > new dependency

Do not introduce a new dependency if the existing project already has a suitable solution.

---

# 3. UI LIBRARY RULE

If the project uses shadcn/ui:

ALWAYS prefer the existing shadcn/ui components.

Before creating a custom component, check whether shadcn/ui already provides the required functionality.

Examples:

* Button → use existing Button
* Dialog → use existing Dialog
* Dropdown → use existing DropdownMenu
* Select → use existing Select
* Input → use existing Input
* Form → use existing form infrastructure
* Tabs → use existing Tabs
* Tooltip → use existing Tooltip

Do not recreate these components unless there is a documented project-specific reason.

Follow the existing project's customization and styling conventions.

---

# 4. SEPARATION OF LOGIC FROM TSX

TSX files should primarily describe the UI.

Avoid putting substantial business logic directly inside JSX/TSX.

Separate:

* business logic
* data fetching
* transformations
* validation
* complex state management
* side effects
* calculations
* API communication

from presentation.

Prefer structures such as:

components/
hooks/
services/
lib/
utils/
types/
features/

The exact structure must follow the existing project's architecture.

Do not create files merely to satisfy this rule. Extraction should improve separation of concerns.

---

# 5. TSX RESPONSIBILITY

A React component should primarily be responsible for:

* receiving props
* composing UI
* rendering UI
* handling simple UI interactions
* delegating complex behavior

Avoid large components containing:

* API calls
* business rules
* complex calculations
* data transformation pipelines
* large conditional business logic
* duplicated logic
* complicated asynchronous workflows

If a component becomes difficult to understand, consider extracting:

* custom hooks
* presentational components
* domain functions
* services
* utilities

---

# 6. DECLARATIVE REACT

Prefer declarative React patterns.

Describe WHAT the UI should represent rather than HOW to manipulate the UI.

Prefer:

```tsx
{isLoading && <Loading />}
{error && <ErrorMessage error={error} />}
{data && <DataView data={data} />}
```

over imperative DOM manipulation.

Avoid:

* direct DOM manipulation
* document.querySelector
* manual DOM updates
* unnecessary refs for state
* imperative UI synchronization

Use React state, props, composition, and derived values.

---

# 7. REUSABLE COMPONENTS

Reusable components must follow a declarative API.

Prefer:

```tsx
<Card>
  <CardHeader>
    <CardTitle>Users</CardTitle>
  </CardHeader>

  <CardContent>
    <UserList users={users} />
  </CardContent>
</Card>
```

over components with excessive configuration flags such as:

```tsx
<Card
  showHeader
  showFooter
  showIcon
  compact
  bordered
  ...
/>
```

Prefer composition over boolean-prop explosion.

A reusable component should expose a clear, predictable interface.

Avoid making components reusable before there is a real reuse requirement.

---

# 8. BUSINESS LOGIC

Business logic must not depend unnecessarily on React.

Prefer:

```text
UI
 ↓
Hook / Controller
 ↓
Domain logic
 ↓
Service
 ↓
Infrastructure
```

rather than putting all logic into the component.

Domain logic should be testable independently when practical.

---

# 9. DATA FETCHING

Before creating a fetch function, API client, or data-access abstraction:

1. Search the repository.
2. Identify existing fetch utilities.
3. Identify existing API clients.
4. Identify existing hooks.
5. Identify existing query/data-fetching libraries.

Reuse existing infrastructure.

For example, if the project already has:

```ts
apiClient.get(...)
```

do not create:

```ts
fetch(...)
axios(...)
newApiClient(...)
```

unless there is a documented architectural reason.

Follow the project's established data-fetching pattern.

---

# 10. HOOKS

Custom hooks should encapsulate reusable React behavior.

A hook should not become a dumping ground for unrelated business logic.

Prefer focused hooks:

```ts
useUser()
useAuth()
useDebounce()
useUsersQuery()
```

over giant hooks containing unrelated application behavior.

Do not create a custom hook simply because code can technically be placed inside one.

---

# 11. UTILITIES

Before creating a utility:

1. Search `lib/`
2. Search `utils/`
3. Search existing feature modules.
4. Check installed libraries.
5. Check whether an equivalent function already exists.

Reuse existing utilities whenever appropriate.

Do not create duplicate helpers with slightly different names.

---

# 12. TYPESCRIPT

Prefer strong typing.

Avoid:

```ts
any
```

unless there is a justified reason.

Prefer:

```ts
unknown
```

when the type is genuinely unknown.

Avoid unnecessary type assertions:

```ts
foo as SomeType
```

Prefer proper type narrowing.

Keep domain types explicit and meaningful.

Do not duplicate types when an existing canonical type can be reused.

---

# 13. STATE MANAGEMENT

Use the simplest appropriate state mechanism.

Prefer:

1. derived values
2. local component state
3. custom hooks
4. existing project state-management solution

Do not introduce global state for local concerns.

Do not duplicate server state into client state unnecessarily.

Follow the existing project's state-management architecture.

---

# 14. ERROR HANDLING

Follow existing project conventions for:

* API errors
* validation errors
* loading states
* empty states
* retry behavior
* user-facing errors

Do not silently swallow errors.

Avoid:

```ts
catch {
}
```

unless intentionally justified.

---

# 15. FILE SIZE AND RESPONSIBILITY

Do not split files purely because they are long.

Split when there is a meaningful separation of responsibility.

A file should have a clear purpose.

Avoid:

```text
helpers.ts
utils.ts
common.ts
misc.ts
```

becoming dumping grounds for unrelated functionality.

Prefer domain-oriented organization.

---

# 16. DEPENDENCY DIRECTION

Respect the project's architectural boundaries.

High-level business/domain logic should not unnecessarily depend on:

* UI
* database
* HTTP framework
* browser APIs
* infrastructure implementation details

Dependencies should point toward stable abstractions where appropriate.

Do not introduce abstraction layers without a real architectural benefit.

---

# 17. REFACTORING

When implementing a feature:

DO NOT refactor unrelated code.

If existing code is directly related to the feature and must be improved, keep the refactor focused.

Avoid large opportunistic rewrites.

Prefer small, reviewable changes.

---

# 18. NEW DEPENDENCIES

Before installing a dependency:

1. Check package.json.
2. Check whether an existing dependency solves the problem.
3. Check whether the functionality can reasonably be implemented using existing project infrastructure.
4. Consider bundle size and maintenance cost.

Do not add dependencies casually.

---

# 19. ARCHITECTURE MAP

The repository contains:

```text
docs/architecture/source-map.md
```

This file contains Mermaid diagrams describing the source-code architecture.

Before making significant architectural changes:

1. Read the relevant architecture map.
2. Understand the existing dependency relationships.
3. Update the architecture map if the change alters architecture.

Keep the architecture map understandable.

Do not turn it into an exhaustive representation of every file.

Represent meaningful relationships such as:

* feature boundaries
* domain boundaries
* UI → hooks
* hooks → services
* services → API/infrastructure
* shared components
* important dependencies

---

# 20. BEFORE IMPLEMENTATION

For non-trivial tasks:

DO NOT immediately generate code.

First:

1. Understand the requirement.
2. Inspect the existing implementation.
3. Find reusable code.
4. Identify affected modules.
5. Identify architectural boundaries.
6. Determine whether existing utilities/components can be reused.
7. Propose the smallest appropriate design.

For small changes, this analysis may be brief.

---

# 21. IMPLEMENTATION

When implementing:

* make the smallest appropriate change
* reuse existing infrastructure
* preserve existing conventions
* avoid unrelated modifications
* keep types strong
* keep components focused
* keep business logic separated from presentation
* prefer composition
* prefer declarative APIs
* follow existing UI patterns

---

# 22. MANDATORY SELF-REVIEW

After implementation, review the changes as if reviewing another engineer's pull request.

Check:

### Architecture

* Are dependencies flowing correctly?
* Did I violate an existing architectural boundary?
* Did I introduce unnecessary coupling?

### SOLID

* SRP
* OCP
* LSP
* ISP
* DIP

### React

* Is the component declarative?
* Is business logic separated from TSX?
* Is state located at the correct level?
* Is there unnecessary prop drilling?
* Is there unnecessary useEffect?
* Is there unnecessary useRef?
* Is there unnecessary state?

### Reuse

* Did I reuse existing components?
* Did I reuse existing shadcn components?
* Did I reuse existing utilities?
* Did I reuse existing API/fetch infrastructure?
* Did I accidentally duplicate functionality?

### TypeScript

* Any unnecessary `any`?
* Any unnecessary assertions?
* Are types reusable and canonical?

### Maintainability

* Is the code easy to understand?
* Is it over-engineered?
* Is there unnecessary abstraction?
* Is there duplicated logic?

If problems are found, fix them before considering the task complete.

---

# 23. FINAL RESPONSE FORMAT

When completing a coding task, briefly report:

1. What changed.
2. Which existing components/utilities were reused.
3. Any new abstractions introduced.
4. Any architectural decisions.
5. Tests/checks performed.
6. Any intentional rule violations and why.

Do not claim tests passed unless they were actually run.

---

# 24. GOLDEN RULE

Before creating something new, ask:

> "Does this repository already have a way to do this?"

Prefer the existing way unless there is a concrete reason to change it.

Consistency with the existing codebase is more important than introducing a theoretically "better" pattern.

The objective is not maximum abstraction.

The objective is a codebase that remains easy to change.
