package com.dance4life.core.data.repository

import android.util.Log
import com.dance4life.core.data.network.ApiService
import org.json.JSONObject

class DataRepository {

    fun enviarDados(
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

    fun obterUpdates(userId: String, callback: (String?) -> Unit) {
        ApiService.getUpdates(userId, callback)
    }

    fun enviarMetricaRl(payload: JSONObject, callback: (Boolean) -> Unit) {
        ApiService.sendRlMetric(payload, callback)
    }
}