package com.dance4life.core.data.repository

import android.util.Log
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.data.network.ApiService
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class DataRepository {

    fun sendDActivityData(
        userId: String,
        ritmo: Double,
        acc: Double,
        gyro: Double,
        hr: Double,
        lat: Double,
        lon: Double
    ) {
        Log.d("CLACULAR", "USERID: $userId")
        ApiService.sendData(userId, ritmo, acc, gyro, hr, lat, lon)
    }



    fun getUserMatch(userId: String, callback: (String?) -> Unit) {
        ApiService.getUserMatch(userId, callback)
    }

    fun getEnvironmentData(userId: String, latitude: Double, longitude: Double,city: String, callback: (String?) -> Unit) {
        ApiService.getEnvironmentData(userId, latitude, longitude, city, callback)
    }

    fun sendMovementRecommendation(
        userId: String,
        recommendation: MovementRecommendation
    ) {
        ApiService.sendMovementRecommendation(userId, recommendation)
    }


}