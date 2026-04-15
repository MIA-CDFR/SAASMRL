package com.dance4life.plugins.rlinference

import com.dance4life.core.domain.model.MovementObservation
import com.dance4life.core.domain.model.MovementRecommendation

interface RlCoachPolicy {
    fun recommend(observation: MovementObservation): MovementRecommendation
}
