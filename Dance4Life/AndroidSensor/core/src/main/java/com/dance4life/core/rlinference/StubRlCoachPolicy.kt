package com.dance4life.core.rlinference

import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation

class StubRlCoachPolicy : RlCoachPolicy {
    override fun recommend(observation: MovementObservation): MovementRecommendation {
        val (actionId, title, duration, message) = if (observation.sedentaryMinutesToday > 180) {
            Quad(
                "medium_intensity",
                "Moderate coaching suggestion",
                5,
                "Great balance: this intensity supports healthy activity.",
            )
        } else {
            Quad(
                "low_intensity",
                "Low-intensity movement cue",
                2,
                "A gentle move keeps momentum without overload.",
            )
        }

        return MovementRecommendation(
            actionId = actionId,
            title = title,
            durationMinutes = duration,
            encouragementMessage = message,
        )
    }

    private data class Quad(
        val actionId: String,
        val title: String,
        val durationMinutes: Int,
        val encouragementMessage: String,
    )
}
