# Source Architecture Map

This document describes the high-level architecture and important source-code relationships of this application.

Update this document when significant architectural changes are introduced.

---

## High-Level Architecture

```mermaid
flowchart TD

    UI[React UI / TSX]

    Components[Reusable Components]
    Features[Feature Modules]

    Hooks[Custom Hooks]
    Domain[Domain / Business Logic]

    Services[Services / API Layer]
    Utils[Utilities]
    Types[Shared Types]

    External[External APIs / Infrastructure]

    UI --> Components
    UI --> Features

    Features --> Hooks
    Features --> Domain
    Features --> Components

    Hooks --> Domain
    Hooks --> Services

    Domain --> Utils
    Domain --> Types

    Services --> External
    Services --> Types

    Components --> Types
```

---

## Architectural Rules

```mermaid
flowchart LR

    Presentation[Presentation]
    Application[Application Logic]
    Domain[Domain Logic]
    Infrastructure[Infrastructure]

    Presentation --> Application
    Application --> Domain
    Application --> Infrastructure

    Domain --> Shared[Shared Types / Pure Utilities]

    Infrastructure --> External[External Systems]
```

The dependency direction should generally follow:

```text
Presentation
      ↓
Application
      ↓
Domain
      ↓
Shared
```

Infrastructure should remain at the boundary.

---

## Feature Structure

Use the project's existing structure.

When a feature is sufficiently complex, prefer a domain-oriented structure such as:

```text
features/
└── users/
    ├── components/
    ├── hooks/
    ├── services/
    ├── utils/
    ├── types.ts
    └── index.ts
```

Do not create this structure for every small feature automatically.

---

## Component Relationship

```mermaid
flowchart TD

    Page[Page]

    Feature[Feature Container]

    Hook[Feature Hook]

    Logic[Business / Domain Logic]

    UI[Presentational Components]

    Shared[Shared Components]

    Page --> Feature
    Feature --> Hook
    Feature --> UI
    Hook --> Logic
    UI --> Shared
```

---

## Data Flow

```mermaid
sequenceDiagram

    participant User
    participant UI as React UI
    participant Hook as Custom Hook
    participant Service as Service/API
    participant API as External API

    User->>UI: Interaction
    UI->>Hook: Invoke action
    Hook->>Service: Request data
    Service->>API: HTTP request
    API-->>Service: Response
    Service-->>Hook: Parsed data
    Hook-->>UI: State / data
    UI-->>User: Render result
```

---

## Reuse Hierarchy

When implementing functionality, prefer:

```mermaid
flowchart TD

    Requirement[New Requirement]

    ExistingFeature[Existing Feature]
    ExistingComponent[Existing Component]
    Shadcn[Existing shadcn/ui Component]
    ExistingHook[Existing Hook]
    ExistingUtility[Existing Utility]
    ExistingService[Existing API / Fetch Service]
    ExistingLibrary[Existing Library]

    NewImplementation[New Implementation]

    Requirement --> ExistingFeature
    Requirement --> ExistingComponent
    Requirement --> Shadcn
    Requirement --> ExistingHook
    Requirement --> ExistingUtility
    Requirement --> ExistingService
    Requirement --> ExistingLibrary

    ExistingFeature --> NewImplementation
    ExistingComponent --> NewImplementation
    Shadcn --> NewImplementation
    ExistingHook --> NewImplementation
    ExistingUtility --> NewImplementation
    ExistingService --> NewImplementation
    ExistingLibrary --> NewImplementation
```

The goal is:

```text
Reuse
  >
Extend
  >
Compose
  >
Create
```

---

## Important Architectural Decisions

Record significant decisions here.

Example:

```text
ADR-001
Decision: Use the project's existing fetch abstraction for all API calls.
Reason: Centralizes authentication, error handling, and request configuration.
```

---

## Updating This Map

Update this document when:

* a new major feature is introduced
* a new architectural layer is introduced
* dependency direction changes
* a major shared component system changes
* API/data-access architecture changes
* state-management architecture changes

Do not update it for every small component or file.

The map should remain useful to engineers and AI agents trying to understand the system.
