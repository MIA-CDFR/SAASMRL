package com.dance4life.core.domain.controller

import android.os.Handler
import android.os.Looper
import com.dance4life.core.data.model.LocationData
import com.dance4life.core.data.model.RitmoResult
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.device.DeviceProvider
import com.dance4life.core.domain.location.LocationProvider
import com.dance4life.core.domain.sensor.SensorProvider
import com.dance4life.core.utils.Constants.SEND_ACTIVITY_DELAY
import com.dance4life.core.utils.RitmoCalculator

class DanceController(
    private val sensorProvider: SensorProvider,
    private val locationProvider: LocationProvider,
    private val repository: DataRepository,
    private val ritmoCalculator: RitmoCalculator,
    private val deviceProvider: DeviceProvider
) {

    private var onLocationUpdate: ((LocationData) -> Unit)? = null

    private val accData = mutableListOf<Float>()
    private val gyroData = mutableListOf<Float>()
    private val hrData = mutableListOf<Int>()

    private var currentLat: Double = 0.0
    private var currentLon: Double = 0.0

    private var onSensorUpdate: ((SensorData) -> Unit)? = null
    private var onRitmoCalculated: ((Double) -> Unit)? = null

    // 🔥 Guarda o último resultado calculado
    private var lastResult: RitmoResult? = null

    // ⏱️ Timer para envio
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var runnable: Runnable

    fun setSensorListener(listener: (SensorData) -> Unit) {
        onSensorUpdate = listener
    }

    fun setRitmoListener(listener: (Double) -> Unit) {
        onRitmoCalculated = listener
    }

    fun start() {

        // 📍 Localização
        locationProvider.start { location ->
            currentLat = location.latitude
            currentLon = location.longitude

            onLocationUpdate?.invoke(location)
        }

        // 📡 Sensores (tempo real)
        sensorProvider.setListener { data ->

            accData.add(data.accMagnitude.toFloat())
            gyroData.add(data.gyroMagnitude.toFloat())
            hrData.add(data.heartRate)

            onSensorUpdate?.invoke(data)

            if (accData.size > 50) {
                accData.removeAt(0)
                gyroData.removeAt(0)
                hrData.removeAt(0)
            }

            // 🔥 CALCULA SEMPRE
            if (accData.isNotEmpty()) {
                calcularRitmoLocal()
            }
        }

        sensorProvider.start()

        // ⏱️ ENVIO DE 30 EM 30 SEGUNDOS
        runnable = object : Runnable {
            override fun run() {
                enviarDados()
                handler.postDelayed(this, SEND_ACTIVITY_DELAY)
            }
        }

        handler.postDelayed(runnable, SEND_ACTIVITY_DELAY)
    }

    fun stop() {
        sensorProvider.stop()
        handler.removeCallbacks(runnable)
    }

    // Calcula apenas (sem enviar)
    private fun calcularRitmoLocal() {
        val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        lastResult = result

        onRitmoCalculated?.invoke(result.ritmo)
    }

    // Envia apenas (usa último cálculo)
    private fun enviarDados() {

        val result = lastResult ?: return

        repository.enviarDados(
            deviceProvider.getUserId(),
            result.ritmo,
            result.avgAcc,
            result.avgGyro,
            result.avgHR,
            currentLat,
            currentLon
        )

        // limpa buffers após envio
        accData.clear()
        gyroData.clear()
        hrData.clear()
    }

    fun setLocationListener(listener: (LocationData) -> Unit) {
        onLocationUpdate = listener
    }
}