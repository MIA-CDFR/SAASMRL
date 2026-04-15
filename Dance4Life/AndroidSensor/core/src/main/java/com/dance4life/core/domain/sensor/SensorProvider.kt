package com.dance4life.core.domain.sensor

import com.dance4life.core.data.model.SensorData

interface SensorProvider {
    fun start()
    fun stop()
    fun setListener(listener: (SensorData) -> Unit)
}