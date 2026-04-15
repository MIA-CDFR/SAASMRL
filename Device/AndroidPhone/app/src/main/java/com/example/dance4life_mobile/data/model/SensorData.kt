package com.example.dance4life_mobile.data.model

data class SensorData(
    val accX: Float,
    val accY: Float,
    val accZ: Float,
    val gyroX: Float,
    val gyroY: Float,
    val gyroZ: Float,
    val heartRate: Int,
    val accMagnitude: Double,
    val gyroMagnitude: Double
)