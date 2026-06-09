# ADR-013: Mobile App Architecture (Android)

## Status

Proposed

## Context

We need to initialize the Android application for the Ticket Analyzer project. The app's primary responsibilities are receipt capture (camera), offline storage of draft receipts, and synchronization with the backend API.

## Decision

We will use a modern Android architecture based on **Jetpack Compose** and the **MVVM (Model-View-ViewModel)** pattern.

### Tech Stack

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Asynchronous Work**: Kotlin Coroutines & Flow
- **Local Persistence**: Room (SQLite wrapper)
- **Networking**: Retrofit + OkHttp
- **Dependency Injection**: Manual DI or Hilt (Manual DI initially for simplicity in MVP)
- **Background Tasks**: WorkManager (for sync)

### Layered Architecture

1.  **UI Layer (Compose)**: Activities and Composable functions. They observe state from ViewModels.
2.  **Domain Layer**: Pure Kotlin models and Use Cases (interactors). Defines the business logic of what a "Receipt Draft" is.
3.  **Data Layer**: Repositories that decide between local (Room) or remote (Retrofit) data sources.

### Offline-First Strategy

- All captured receipts are first saved to the local Room database as `DraftReceipt`.
- A background worker (WorkManager) periodically attempts to upload pending drafts to the backend.
- Once successfully uploaded, the draft is marked as `SYNCED` or moved to a `SyncedReceipt` table.

## Consequences

- **Pros**: Native performance, excellent camera integration, robust offline support.
- **Cons**: Higher initial setup complexity compared to cross-platform (Flutter/RN), but better for the long-term goal of "Consumption Intelligence" which may require on-device processing.
