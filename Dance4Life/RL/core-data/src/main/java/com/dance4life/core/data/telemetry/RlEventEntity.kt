package com.dance4life.core.data.telemetry

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "rl_events")
data class RlEventEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val eventId: String,
    val tsClientMs: Long,
    val deviceIdHash: String,
    val modelVersion: String,
    val appVersion: String,
    val stepsLastHour: Int,
    val sedentaryMinutesToday: Int,
    val energyLevel: Int,
    val mobilityConfidence: Int,
    val actionId: String,
    val actionIndex: Int,
    val policySource: String = "onnx",
    val synced: Boolean = false,
    val syncedAtMs: Long? = null,
)
