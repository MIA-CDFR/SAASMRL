package com.dance4life.core.data.metrics

import android.content.Context
import com.dance4life.core.domain.model.MovementObservation
import com.dance4life.core.data.telemetry.RlEvent
import com.dance4life.core.data.telemetry.RlOutcome
import com.dance4life.core.data.telemetry.Dance4LifeDatabase
import com.dance4life.core.data.telemetry.RlTelemetrySyncWorker
import com.dance4life.core.data.telemetry.RlTelemetryFirebaseService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class InMemoryMovementMetricsRepository(
    private val context: Context,
    initialObservation: MovementObservation = MovementObservation(
        stepsLastHour = 120,
        sedentaryMinutesToday = 180,
        energyLevel = 5,
        mobilityConfidence = 6,
    ),
) : MovementMetricsRepository {

    private val _observation = MutableStateFlow(initialObservation)
    override val observation: StateFlow<MovementObservation> = _observation.asStateFlow()

    private val db = Dance4LifeDatabase.getInstance(context)
    private val ioScope = CoroutineScope(Dispatchers.IO)

    init {
        RlTelemetrySyncWorker.schedulePeriodicSync(context)
    }

    override fun recordSteps(stepsInLastHour: Int) {
        _observation.value = _observation.value.copy(
            stepsLastHour = stepsInLastHour.coerceIn(0, 2000),
        )
    }

    override fun recordSedentaryMinutes(totalSedentaryMinutesToday: Int) {
        _observation.value = _observation.value.copy(
            sedentaryMinutesToday = totalSedentaryMinutesToday.coerceIn(0, 480),
        )
    }

    override fun recordEnergyLevel(level0to10: Int) {
        _observation.value = _observation.value.copy(
            energyLevel = level0to10.coerceIn(0, 10),
        )
    }

    override fun recordMobilityConfidence(level0to10: Int) {
        _observation.value = _observation.value.copy(
            mobilityConfidence = level0to10.coerceIn(0, 10),
        )
    }

    override fun recordRecommendationFeedback(
        actionId: String,
        accepted: Boolean,
        completed: Boolean,
    ) {
        val current = _observation.value

        val confidenceBoost = when {
            completed -> 2
            accepted -> 1
            else -> -1
        }

        val energyDelta = when {
            completed -> 1
            accepted -> 0
            else -> -1
        }

        val sedDelta = when {
            completed -> -20
            accepted -> -10
            else -> 10
        }

        val rewardProxy = when {
            completed -> 1.0
            accepted -> 0.3
            else -> -0.3
        }

        _observation.value = current.copy(
            sedentaryMinutesToday = (current.sedentaryMinutesToday + sedDelta).coerceIn(0, 480),
            energyLevel = (current.energyLevel + energyDelta).coerceIn(0, 10),
            mobilityConfidence = (current.mobilityConfidence + confidenceBoost).coerceIn(0, 10),
        )

        ioScope.launch {
            val outcome = RlOutcome(
                eventId = "",
                tsClientMs = System.currentTimeMillis(),
                accepted = accepted,
                completed = completed,
                rewardProxy = rewardProxy,
            )
            db.rlOutcomeDao().insert(outcome.toEntity())
        }
    }

    fun recordObservationAndAction(
        actionId: String,
        actionIndex: Int,
    ) {
        val current = _observation.value
        ioScope.launch {
            val event = RlEvent(
                deviceIdHash = RlTelemetryFirebaseService.hashDeviceId(context),
                modelVersion = "dance4life_coach_v1",
                appVersion = "0.1.0",
                stepsLastHour = current.stepsLastHour,
                sedentaryMinutesToday = current.sedentaryMinutesToday,
                energyLevel = current.energyLevel,
                mobilityConfidence = current.mobilityConfidence,
                actionId = actionId,
                actionIndex = actionIndex,
            )
            db.rlEventDao().insert(event.toEntity())
        }
    }
}
