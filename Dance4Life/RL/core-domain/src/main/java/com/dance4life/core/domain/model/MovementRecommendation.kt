package com.dance4life.core.domain.model

data class MovementObservation(
    val stepsLastHour: Int,
    val sedentaryMinutesToday: Int,
    val energyLevel: Int,
    val mobilityConfidence: Int,
)

data class MovementRecommendation(
    val actionId: String,
    val title: String,
    val durationMinutes: Int,
    val encouragementMessage: String,
)
