package com.dance4life.core.data.telemetry

import java.util.UUID

data class RlEvent(
    val eventId: String = UUID.randomUUID().toString(),
    val tsClientMs: Long = System.currentTimeMillis(),
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
) {
    fun toEntity(): RlEventEntity = RlEventEntity(
        eventId = eventId,
        tsClientMs = tsClientMs,
        deviceIdHash = deviceIdHash,
        modelVersion = modelVersion,
        appVersion = appVersion,
        stepsLastHour = stepsLastHour,
        sedentaryMinutesToday = sedentaryMinutesToday,
        energyLevel = energyLevel,
        mobilityConfidence = mobilityConfidence,
        actionId = actionId,
        actionIndex = actionIndex,
        policySource = policySource,
    )
}

data class RlOutcome(
    val outcomeId: String = UUID.randomUUID().toString(),
    val eventId: String,
    val tsClientMs: Long = System.currentTimeMillis(),
    val accepted: Boolean,
    val completed: Boolean,
    val completionMinutes: Int? = null,
    val rewardProxy: Double = 0.0,
) {
    fun toEntity(): RlOutcomeEntity = RlOutcomeEntity(
        outcomeId = outcomeId,
        eventId = eventId,
        tsClientMs = tsClientMs,
        accepted = accepted,
        completed = completed,
        completionMinutes = completionMinutes,
        rewardProxy = rewardProxy,
    )
}
