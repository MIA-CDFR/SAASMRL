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
import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.rlinference.RlCoachPolicy

class DanceController(
    private val sensorProvider: SensorProvider,
    private val locationProvider: LocationProvider,
    private val repository: DataRepository,
    private val ritmoCalculator: RitmoCalculator,
    private val deviceProvider: DeviceProvider,
    private val rlCoachPolicy: RlCoachPolicy
) {


    private var onLocationUpdate: ((LocationData) -> Unit)? = null
    private var onMovementRecommendation: ((MovementRecommendation) -> Unit)? = null

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

    private val updatesHandler = Handler(Looper.getMainLooper())
    private lateinit var updatesRunnable: Runnable

    private var onInviteReceived: ((String, String) -> Unit)? = null

    private var started = false

    fun setSensorListener(listener: (SensorData) -> Unit) {
        onSensorUpdate = listener
    }

    fun setRitmoListener(listener: (Double) -> Unit) {
        onRitmoCalculated = listener
    }

    fun setMovementRecommendationListener(
        listener: (MovementRecommendation) -> Unit
    ) {
        onMovementRecommendation = listener
    }

    fun start() {

        if (started) return
        started = true

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

        // ENVIO DE 30 EM 30 SEGUNDOS
        runnable = object : Runnable {
            override fun run() {
                enviarDados()
                handler.postDelayed(this, SEND_ACTIVITY_DELAY)
            }
        }

        handler.postDelayed(runnable, SEND_ACTIVITY_DELAY)

        updatesRunnable = object : Runnable {
            override fun run() {

                val userId = deviceProvider.getUserId()

                repository.obterUpdates(userId) { body ->

                    if (!body.isNullOrEmpty()) {

                        val jsonArray = org.json.JSONArray(body)

                        for (i in 0 until jsonArray.length()) {
                            val obj = jsonArray.getJSONObject(i)

                            when (obj.getString("type")) {

                                "invite" -> {
                                    val id = obj.getString("id")
                                    val user = obj.getString("user")

                                    onInviteReceived?.invoke(id, user)
                                }

                                "match" -> {
                                    val user = obj.getString("user")
                                    val score = obj.getDouble("score")

                                    onMatchReceived?.invoke(user, score)
                                }
                            }
                        }
                    }
                }

                updatesHandler.postDelayed(this, 20000)
            }
        }

        updatesHandler.post(updatesRunnable)
    }

    private var onMatchReceived: ((String, Double) -> Unit)? = null

    fun setMatchListener(listener: (String, Double) -> Unit) {
        onMatchReceived = listener
    }

    fun stop() {
        started = false
        sensorProvider.stop()
        handler.removeCallbacks(runnable)
        updatesHandler.removeCallbacks(updatesRunnable)
    }

    // Calcula apenas (sem enviar)
    private fun calcularRitmoLocal() {
        //val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        //lastResult = result

        //onRitmoCalculated?.invoke(result.ritmo)



        val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        lastResult = result

        onRitmoCalculated?.invoke(result.ritmo)

        val observation = MovementObservation(
            stepsLastHour = estimateSteps(accData),
            sedentaryMinutesToday = estimateSedentaryMinutes(result.avgAcc),
            energyLevel = estimateEnergyLevel(result.avgHR),
            mobilityConfidence = estimateMobility(result.avgGyro)
        )

        val recommendation = rlCoachPolicy.recommend(observation)
        onMovementRecommendation?.invoke(recommendation)
    }

    private fun estimateSteps(accData: List<Float>): Int {
        return (accData.sum() * 8).toInt().coerceAtLeast(0)
    }

    private fun estimateSedentaryMinutes(avgAcc: Double): Int {
        return if (avgAcc < 1.2) 240 else 60
    }

    private fun estimateEnergyLevel(avgHr: Double): Int {
        return when {
            avgHr < 75 -> 3
            avgHr < 100 -> 6
            else -> 9
        }
    }

    private fun estimateMobility(avgGyro: Double): Int {
        return when {
            avgGyro < 0.5 -> 2
            avgGyro < 1.5 -> 5
            else -> 8
        }
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


    fun setInviteListener(listener: (inviteId: String, user: String) -> Unit) {
        onInviteReceived = listener
    }
}