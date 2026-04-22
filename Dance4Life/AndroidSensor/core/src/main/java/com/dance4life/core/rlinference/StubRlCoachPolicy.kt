package com.dance4life.core.rlinference

import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation

class StubRlCoachPolicy : RlCoachPolicy {
    override fun recommend(observation: MovementObservation): MovementRecommendation {
        //val (actionId, title, duration, message) = if (observation.sedentaryMinutesToday > 180) {
        val (actionId, title, duration, message) = if (observation.physicalFatigue > 8.0f) {
            Quad(
                "low_intensity",
                "Ritmo Baixo",
                2,
                "Um ritmo mais leve será benéfico para o seu bem-estar.",

            )
        } else if (observation.physicalFatigue > 6.0f){
            Quad(
                "medium_intensity",
                "Ritmo Saudável",
                5,
                "Este nível de atividade é ideal para o seu bem-estar.",
            )
        }else{
            Quad(
                "high_intensity",
                "Ritmo Elevado",
                2,
                "Aumentar o nível de atividade será benéfico para o seu bem-estar.",
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
