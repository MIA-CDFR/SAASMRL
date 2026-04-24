package com.dance4life.core.domain.controller

import android.os.Handler
import android.os.Looper
import android.util.Log
import com.dance4life.core.data.model.EnvironmentData
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
import kotlin.math.log

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

    private var currentCity: String? = null

    private var lastActionId: String? = null
    private var onSensorUpdate: ((SensorData) -> Unit)? = null
    private var onRitmoCalculated: ((Double) -> Unit)? = null

    // 🔥 Guarda o último resultado calculado
    private var lastResult: RitmoResult? = null

    // Rolling buffer of (timestampMs, ritmo) for 1-min average
    private val ritmoBuffer = mutableListOf<Pair<Long, Double>>()
    private val RITMO_WINDOW_MS = 1 * 60 * 1000L

    // ⏱️ Timer para envio
    private val handler = Handler(Looper.getMainLooper())
    private lateinit var runnable: Runnable

    private val updatesHandler = Handler(Looper.getMainLooper())
    private lateinit var updatesRunnable: Runnable

    private var onInviteReceived: ((String, String) -> Unit)? = null

    private var onEnvironmentUpdate: ((EnvironmentData) -> Unit)? = null

    private var started = false
    private var sessionStartMs: Long = 0L

    // 1 real second = SIM_MINUTES_PER_SECOND simulated minutes (increase to simulate faster)
    private val SIM_MINUTES_PER_SECOND = 0.5f

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
        sessionStartMs = System.currentTimeMillis()

        //Localização
        locationProvider.start { location ->
            currentLat = location.latitude
            currentLon = location.longitude
            currentCity = location.city

            onLocationUpdate?.invoke(location)

            repository.getEnvironmentData(
                userId = deviceProvider.getUserId(),
                latitude = currentLat,
                longitude = currentLon,
                city = currentCity ?: ""
            ) { body ->

                if (!body.isNullOrEmpty()) {

                    val obj = org.json.JSONObject(body)

                    onEnvironmentUpdate?.invoke(
                        EnvironmentData(
                            temperature = obj.getDouble("temperatura"),
                            humidity = obj.getDouble("humidade")
                        )
                    )
                }
            }
        }

        //Sensores (tempo real)
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

            //CALCULA SEMPRE
            if (accData.isNotEmpty()) {
                calcularRitmoLocal()
            }
        }

        sensorProvider.start()

        // ENVIO DE 30 EM 30 SEGUNDOS
        runnable = object : Runnable {
            override fun run() {
                sendDActivityData()
                handler.postDelayed(this, SEND_ACTIVITY_DELAY)
            }
        }

        handler.postDelayed(runnable, SEND_ACTIVITY_DELAY)

        updatesRunnable = object : Runnable {
            override fun run() {

                val userId = deviceProvider.getUserId()

                repository.getUserMatch(userId) { body ->

                    if (!body.isNullOrEmpty()) {
                        Log.d("MatchData:", body)
                        val jsonArray = org.json.JSONArray(body)

                        for (i in 0 until jsonArray.length()) {
                            val obj = jsonArray.getJSONObject(i)

                            when (obj.getString("type")) {

                                "invite" -> {

                                    val id = obj.getString("id")
                                    val cluster = obj.getString("cluster")

                                    onInviteReceived?.invoke(id, cluster)
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

                if (currentLat != 0.0 && currentLon != 0.0) {
                    repository.getEnvironmentData(
                        userId = userId,
                        latitude = currentLat,
                        longitude = currentLon,
                        city = currentCity ?: ""
                    ) { body ->

                        if (!body.isNullOrEmpty()) {

                            val obj = org.json.JSONObject(body)

                            onEnvironmentUpdate?.invoke(
                                EnvironmentData(
                                    temperature = obj.getDouble("temperatura"),
                                    humidity = obj.getDouble("humidade")
                                )
                            )


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

        val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        lastResult = result

        onRitmoCalculated?.invoke(result.ritmo)

        // Update rolling 1-min ritmo buffer
        val now = System.currentTimeMillis()
        ritmoBuffer.add(Pair(now, result.ritmo))
        ritmoBuffer.removeAll { now - it.first > RITMO_WINDOW_MS }
        val avgRitmo = if (ritmoBuffer.isNotEmpty()) ritmoBuffer.map { it.second }.average() else result.ritmo

        val sedentaryMinutesToday = estimateSedentaryMinutes(result.avgAcc)
        val energyLevel = estimateEnergyLevel(result.avgHR)
        val elapsedSimMinutes = ((System.currentTimeMillis() - sessionStartMs) / 1000f * SIM_MINUTES_PER_SECOND).toInt()
        val mobilityConfidence = estimateMobility(result.avgGyro)

        // Grow irritation only if ritmo stays above threshold long enough.
        tickIrritationGrowthByRitmo(result.ritmo)

        val activityLevel = (avgRitmo / RITMO_ACTIVITY_SCALE).toFloat().coerceIn(0f, 10f)
        val simSedentary = (sedentaryMinutesToday + elapsedSimMinutes).coerceIn(0, 480)
        val baselinePhysicalFatigue =
            ((simSedentary / 480f) * 5f +
                    ((10 - energyLevel.coerceIn(0, 10)) / 10f) * 5f)
                .coerceIn(0f, 10f)
        val irritationMetric = getIrritationLevel().toFloat().coerceIn(0f, 10f)
        val physicalFatigue = maxOf(baselinePhysicalFatigue, irritationMetric)

        val observation = MovementObservation(
           /* stepsLastHour = estimateSteps(accData),
            sedentaryMinutesToday = estimateSedentaryMinutes(result.avgAcc),
            energyLevel = estimateEnergyLevel(result.avgHR),
            mobilityConfidence = estimateMobility(result.avgGyro)*/
            //irritationLevel = getIrritationLevel()
            activityLevel = activityLevel,
            physicalFatigue = physicalFatigue,
            irritationLevel = irritationMetric,
        )



        val recommendation = rlCoachPolicy.recommend(observation)
        onMovementRecommendation?.invoke(recommendation)


        Log.d("RECOMMENDATION", recommendation.actionId)
        Log.d("IRRITATION_LEVEL_0", physicalFatigue.toString())

        if(lastActionId != recommendation.actionId) {

            lastActionId = recommendation.actionId
            sendMovementRecommendation(
                userId = deviceProvider.getUserId(),
                recommendation = recommendation
            )
        }
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
    private fun sendDActivityData() {

        val result = lastResult ?: return

        repository.sendDActivityData(
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

    fun sendMovementRecommendation(
        userId: String,
        recommendation: MovementRecommendation
    ) {
        repository.sendMovementRecommendation(userId, recommendation)
    }

    fun setLocationListener(listener: (LocationData) -> Unit) {
        onLocationUpdate = listener
    }


    fun setInviteListener(listener: (inviteId: String, user: String) -> Unit) {
        onInviteReceived = listener
    }

    fun setEnvironmentListener(listener: (EnvironmentData) -> Unit) {
        onEnvironmentUpdate = listener
    }

    companion object {
        private const val RITMO_ACTIVITY_SCALE = 2.0
        private var irritationLevel: Int = 0
        private var lastIrritationLevel: Long = System.currentTimeMillis()
        private var highRitmoStartMs: Long = 0L
        private var lastRitmoGrowthTick: Long = System.currentTimeMillis()
        private var lastRitmoForGrowth: Double? = null

        private const val IRRITATION_MAX = 10
        private const val STRESS_START = 1
        private const val RELIEF_BUMP = 3
        private const val RITMO_STRESS_THRESHOLD = 20.0
        private const val RITMO_STRESS_HOLD_MS = 3_000L
        private const val RITMO_GROWTH_STEP = 2
        private const val RITMO_GROWTH_INTERVAL_MS = 500L

        fun increaseIrritationLevel() {
            Log.d("IRRITATION_LEVEL_3", irritationLevel.toString())
            verifyIrritationLevel()
            irritationLevel = if (irritationLevel <= 0) STRESS_START else (irritationLevel + 1).coerceAtMost(IRRITATION_MAX)
            Log.d("IRRITATION_LEVEL_3", irritationLevel.toString())
        }

        fun decreaseIrritationLevel() {
            verifyIrritationLevel()
            if (irritationLevel > 0) {
                irritationLevel = (irritationLevel - RELIEF_BUMP).coerceAtLeast(0)
            }
        }

        fun tickIrritationGrowthByRitmo(currentRitmo: Double) {
            verifyIrritationLevel()

            val now = System.currentTimeMillis()
            val previousRitmo = lastRitmoForGrowth
            val isRitmoGrowing = previousRitmo != null && currentRitmo > (previousRitmo + 0.1)
            lastRitmoForGrowth = currentRitmo

            if (currentRitmo <= RITMO_STRESS_THRESHOLD) {
                highRitmoStartMs = 0L
                lastRitmoGrowthTick = now
                return
            }

            // Only grow irritation when ritmo is actually trending up.
            if (!isRitmoGrowing) {
                return
            }

            if (highRitmoStartMs == 0L) {
                highRitmoStartMs = now
                lastRitmoGrowthTick = now
                return
            }

            val sustainedMs = now - highRitmoStartMs
            if (sustainedMs < RITMO_STRESS_HOLD_MS || irritationLevel >= IRRITATION_MAX) {
                return
            }

            if (irritationLevel <= 0) {
                irritationLevel = STRESS_START
                lastRitmoGrowthTick = now
                return
            }

            val elapsedGrowthMs = now - lastRitmoGrowthTick
            if (elapsedGrowthMs < RITMO_GROWTH_INTERVAL_MS) {
                return
            }

            val steps = (elapsedGrowthMs / RITMO_GROWTH_INTERVAL_MS).toInt().coerceAtLeast(1)
            irritationLevel = (irritationLevel + steps * RITMO_GROWTH_STEP).coerceAtMost(IRRITATION_MAX)
            lastRitmoGrowthTick += steps * RITMO_GROWTH_INTERVAL_MS
        }

        fun verifyIrritationLevel() {
            val nowTime = System.currentTimeMillis()
            val resetInterval = 5 * 60 * 1000L // 5 minutos

            if (nowTime - lastIrritationLevel >= resetInterval) {
                irritationLevel = 0
                highRitmoStartMs = 0L
                lastIrritationLevel = System.currentTimeMillis()
                lastRitmoGrowthTick = lastIrritationLevel
                lastRitmoForGrowth = null
            }
            Log.d("IRRITATION_LEVEL_2", irritationLevel.toString())
        }

        fun getIrritationLevel(): Int {
            return irritationLevel
        }
    }
}