package com.dance4life.core.data.telemetry

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "rl_outcomes")
data class RlOutcomeEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val outcomeId: String,
    val eventId: String,
    val tsClientMs: Long,
    val accepted: Boolean,
    val completed: Boolean,
    val completionMinutes: Int? = null,
    val rewardProxy: Double = 0.0,
    val synced: Boolean = false,
    val syncedAtMs: Long? = null,
)
