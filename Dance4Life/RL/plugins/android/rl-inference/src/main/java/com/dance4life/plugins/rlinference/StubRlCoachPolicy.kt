package com.dance4life.plugins.rlinference

import com.dance4life.core.domain.model.MovementObservation
import com.dance4life.core.domain.model.MovementRecommendation

class StubRlCoachPolicy : RlCoachPolicy {
    override fun recommend(observation: MovementObservation): MovementRecommendation {
        val title = if (observation.sedentaryMinutesToday > 180) {
            "Gentle 5-minute walk"
        } else {
            "2-minute stretch break"
        }

        val duration = if (title.contains("5-minute")) 5 else 2

        return MovementRecommendation(
            actionId = "move_break",
            title = title,
            durationMinutes = duration,
            encouragementMessage = "Great job taking care of your health. Small movements matter.",
        )
    }
}
