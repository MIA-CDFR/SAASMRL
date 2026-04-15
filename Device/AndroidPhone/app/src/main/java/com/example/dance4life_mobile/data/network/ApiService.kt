package com.example.dance4life_mobile.data.network

import com.example.dance4life_mobile.utils.Constants
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

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
            put("ritmo", ritmo)
            put("acc", acc)
            put("gyro", gyro)
            put("hr", hr)
            put("latitude", lat)
            put("longitude", lon)
            put("timestamp", System.currentTimeMillis())
        }

        val body = json.toString()
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(Constants.BASE_URL + Constants.COLLECT_DATA)
            .post(body)
            .build()

        Thread {
            try {
                val response = ApiClient.client.newCall(request).execute()
                println(response.body?.string())
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    fun getUpdates(userId: String, callback: (String?) -> Unit) {

        val request = Request.Builder()
            .url("${Constants.BASE_URL}${Constants.GET_UPDATES}/$userId")
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
}