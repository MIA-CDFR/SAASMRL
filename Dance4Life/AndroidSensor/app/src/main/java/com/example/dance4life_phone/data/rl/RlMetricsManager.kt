package com.example.dance4life_phone.data.rl

import android.content.Context
import android.util.Log
import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import org.json.JSONArray
import org.json.JSONObject

class RlMetricsManager(
    context: Context,
    private val repository: DataRepository,
    private val userIdProvider: () -> String,
) {

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private var isFlushing: Boolean = false

    fun recordInference(
        observation: MovementObservation,
        recommendation: MovementRecommendation,
        sensor: SensorData,
        policyName: String,
    ) {
        val userId = userIdProvider()

        val payload = JSONObject().apply {
            put("eventType", "rl_metric")
            put("timestamp", System.currentTimeMillis())
            put("userId", userId)

            put("policy", policyName)
            put("recommendationActionId", recommendation.actionId)
            put("recommendationDurationMinutes", recommendation.durationMinutes)

            put(
                "observation",
                JSONObject().apply {
                    put("activityLevel", observation.activityLevel)
                    put("physicalFatigue", observation.physicalFatigue)
                    put("irritationLevel", observation.irritationLevel)
                    //put("mobilityConfidence", observation.mobilityConfidence)

                }
            )

            put(
                "sensorSnapshot",
                JSONObject().apply {
                    put("heartRate", sensor.heartRate)
                    put("accMagnitude", sensor.accMagnitude)
                    put("gyroMagnitude", sensor.gyroMagnitude)
                    put("accX", sensor.accX)
                    put("accY", sensor.accY)
                    put("accZ", sensor.accZ)
                    put("gyroX", sensor.gyroX)
                    put("gyroY", sensor.gyroY)
                    put("gyroZ", sensor.gyroZ)
                }
            )
        }

        enqueue(payload)
        flushPending()
    }

    fun flushPending() {
        synchronized(this) {
            if (isFlushing) return
            if (queueSize() == 0) return
            isFlushing = true
        }
        flushNext()
    }

    private fun flushNext() {
        val next = synchronized(this) {
            if (queueSize() == 0) {
                isFlushing = false
                null
            } else {
                queue().optJSONObject(0)
            }
        }

        if (next == null) return

        /*repository.enviarMetricaRl(next) { success ->
            if (success) {
                synchronized(this) {
                    dequeueFirst()
                }
                flushNext()
            } else {
                synchronized(this) {
                    isFlushing = false
                }
                Log.w(TAG, "RL metrics flush failed. Keeping data in local queue.")
            }
        }*/
    }

    private fun enqueue(item: JSONObject) {
        synchronized(this) {
            val current = queue()
            current.put(item)

            // Bound queue to avoid uncontrolled growth.
            while (current.length() > MAX_QUEUE_SIZE) {
                val trimmed = JSONArray()
                for (i in 1 until current.length()) {
                    trimmed.put(current.get(i))
                }
                saveQueue(trimmed)
                return
            }

            saveQueue(current)
        }
    }

    private fun dequeueFirst() {
        val current = queue()
        if (current.length() == 0) return

        val next = JSONArray()
        for (i in 1 until current.length()) {
            next.put(current.get(i))
        }
        saveQueue(next)
    }

    private fun queue(): JSONArray {
        val raw = prefs.getString(KEY_QUEUE, null)
        return if (raw.isNullOrBlank()) JSONArray() else JSONArray(raw)
    }

    private fun queueSize(): Int = queue().length()

    private fun saveQueue(array: JSONArray) {
        prefs.edit().putString(KEY_QUEUE, array.toString()).apply()
    }

    companion object {
        private const val TAG = "RlMetricsManager"
        private const val PREFS_NAME = "rl_metrics_store"
        private const val KEY_QUEUE = "pending_rl_metrics"
        private const val MAX_QUEUE_SIZE = 2000
    }
}