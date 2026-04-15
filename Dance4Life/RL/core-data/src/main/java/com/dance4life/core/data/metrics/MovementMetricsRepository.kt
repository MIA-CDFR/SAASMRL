package com.dance4life.core.data.metrics

import com.dance4life.core.domain.model.MovementObservation
import kotlinx.coroutines.flow.StateFlow

interface MovementMetricsRepository {
    val observation: StateFlow<MovementObservation>

    fun recordSteps(stepsInLastHour: Int)

    fun recordSedentaryMinutes(totalSedentaryMinutesToday: Int)

    fun recordEnergyLevel(level0to10: Int)

    fun recordMobilityConfidence(level0to10: Int)

    fun recordRecommendationFeedback(
        actionId: String,
        accepted: Boolean,
        completed: Boolean,
    )
}
