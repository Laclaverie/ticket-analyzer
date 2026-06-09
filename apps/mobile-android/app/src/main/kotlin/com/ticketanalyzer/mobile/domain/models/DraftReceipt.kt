package com.ticketanalyzer.mobile.domain.models

import java.util.UUID
import java.util.Date

enum class SyncStatus {
    DRAFT,
    SYNCING,
    SYNCED,
    FAILED
}

data class DraftReceipt(
    val id: UUID = UUID.randomUUID(),
    val localImagePath: String,
    val capturedAt: Date = Date(),
    val status: SyncStatus = SyncStatus.DRAFT,
    val retryCount: Int = 0,
    val lastError: String? = null
)
