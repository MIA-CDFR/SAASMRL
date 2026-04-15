package com.example.dance4life_mobile.utils

import com.example.dance4life_mobile.data.model.RitmoResult

class RitmoCalculator {

    fun calcular(
        accData: List<Float>,
        gyroData: List<Float>,
        hrData: List<Int>
    ): RitmoResult {

        val avgAcc = if (accData.isNotEmpty()) accData.average() else 0.0
        val avgGyro = if (gyroData.isNotEmpty()) gyroData.average() else 0.0
        val avgHR = if (hrData.isNotEmpty()) hrData.average() else 70.0

        val ritmo = avgAcc + avgGyro + (avgHR / 10)

        return RitmoResult(
            ritmo = ritmo,
            avgAcc = avgAcc,
            avgGyro = avgGyro,
            avgHR = avgHR
        )
    }
}