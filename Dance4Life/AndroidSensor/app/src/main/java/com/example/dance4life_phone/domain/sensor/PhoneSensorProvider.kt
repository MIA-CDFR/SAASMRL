package com.example.dance4life_phone.domain.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.domain.sensor.SensorProvider
import kotlin.math.sqrt

class PhoneSensorProvider(
    private val context: Context
) : SensorProvider {

    private lateinit var helper: SensorHelper

    override fun setListener(listener: (SensorData) -> Unit) {
        helper = SensorHelper(context, listener)
    }

    override fun start() {
        helper.start()
    }

    override fun stop() {
        helper.stop()
    }
}