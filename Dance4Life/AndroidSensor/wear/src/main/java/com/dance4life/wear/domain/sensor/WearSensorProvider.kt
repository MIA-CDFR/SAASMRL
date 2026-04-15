package com.dance4life.wear.domain.sensor

import android.content.Context
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.domain.sensor.SensorProvider

class WearSensorProvider(
    private val context: Context
) : SensorProvider {

    private var started = false
    private var helper: SensorHelper? = null
    private var listener: ((SensorData) -> Unit)? = null

    override fun setListener(listener: (SensorData) -> Unit) {
        this.listener = listener

        if (helper == null) {
            helper = SensorHelper(context) {
                this.listener?.invoke(it)
            }
        }
    }

    override fun start() {
        if (started) return
        started = true
        helper?.start()
    }

    override fun stop() {
        started = false
        helper?.stop()
    }
}