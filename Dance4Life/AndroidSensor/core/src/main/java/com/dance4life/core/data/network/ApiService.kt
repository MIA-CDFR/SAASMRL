package com.dance4life.core.data.network

import android.util.Log
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.utils.Constants
import com.dance4life.core.utils.Constants.SET_INVITE_STATUS
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import kotlin.code

object ApiService {

    fun sendData(
        userId: String,
        ritmo: Double,
        acc: Double,
        gyro: Double,
        hr: Double,
        lat: Double,
        lon: Double
    ) {
        val json = JSONObject().apply {
            put("userId", userId)
            put("utilizador_id", userId)
            put("ritmo", ritmo)
            put("acc", acc)
            put("gyro", gyro)
            put("hr", hr)
            put("latitude", lat)
            put("longitude", lon)
            put("timestamp", System.currentTimeMillis())
            put("eventType", "activity")
        }

        postJson(
            url = Constants.BASE_URL + Constants.COLLECT_DATA,
            json = json,
            callback = null,
        )
    }

    fun sendRlMetric(payload: JSONObject, callback: (Boolean) -> Unit) {
        val json = JSONObject(payload.toString()).apply {
            if (!has("timestamp")) {
                put("timestamp", System.currentTimeMillis())
            }
            if (!has("eventType")) {
                put("eventType", "rl_metric")
            }
        }

        postJson(
            url = Constants.BASE_URL + Constants.COLLECT_DATA,
            json = json,
            callback = callback,
        )
    }

    fun getUserMatch(userId: String, callback: (String?) -> Unit) {

        val request = Request.Builder()
            .url("${Constants.BASE_URL}${Constants.GET_USER_MATCH}/$userId")
            .get()
            .build()

        Thread {
            try {
                val response = ApiClient.client.newCall(request).execute()
                callback(response.body?.string())
            } catch (e: Exception) {
                e.printStackTrace()
                callback(null)
            }
        }.start()
    }

    fun getEnvironmentData(userId: String, latitude: Double, longitude: Double, city: String, callback: (String?) -> Unit) {

        val request = Request.Builder()
            .url("${Constants.BASE_URL}${Constants.GET_ENVIRONMENT_DATA}/$userId/$latitude/$longitude/$city")
            .get()
            .build()

        Thread {
            try {
                val response = ApiClient.client.newCall(request).execute()
                callback(response.body?.string())
            } catch (e: Exception) {
                e.printStackTrace()
                callback(null)
            }
        }.start()
    }

    fun acceptInvite(inviteId: String, inviteStatus: Boolean) {

        val json = JSONObject().apply {
            put("inviteId", inviteId)
        }

        Log.d("INVITE", "Aceitou $inviteId")

        val body = json.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(Constants.BASE_URL + "/" + SET_INVITE_STATUS + "/" + inviteId+ "/" + inviteStatus)
            .post(body)
            .build()

        Thread {
            try {
                val response = ApiClient.client.newCall(request).execute()
                Log.d("API", "ACCEPT Code: ${response.code}")
                Log.d("API", "ACCEPT Response: ${response.body?.string()}")
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()


    }

    fun sendMovementRecommendation(
        userId: String,
        recommendation: MovementRecommendation
    ) {
        val json = JSONObject().apply {
            put("userId", userId)
            put("actionId", recommendation.actionId)
            put("title", recommendation.title)
            put("durationMinutes", recommendation.durationMinutes)
            put("encouragementMessage", recommendation.encouragementMessage)
            put("timestamp", System.currentTimeMillis())
        }

        val body = json.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(Constants.BASE_URL + Constants.SET_MOVEMENT_RECOMMENDATION)
            .post(body)
            .build()

        Thread {
            try {
                val response = ApiClient.client.newCall(request).execute()
                Log.d("API", "Recommendation Code: ${response.code}")
                Log.d("API", "Recommendation Response: ${response.body?.string()}")
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }
}