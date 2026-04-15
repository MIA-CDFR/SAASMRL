package com.dance4life.core.rlinference

import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation

interface RlCoachPolicy {
    fun recommend(observation: MovementObservation): MovementRecommendation
}
