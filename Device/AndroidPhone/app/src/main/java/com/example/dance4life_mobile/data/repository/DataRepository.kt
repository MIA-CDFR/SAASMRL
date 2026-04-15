package com.example.dance4life_mobile.data.repository

import com.example.dance4life_mobile.data.network.ApiService

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
        ApiService.sendData(userId, ritmo, acc, gyro, hr, lat, lon)
    }

    fun obterUpdates(userId: String, callback: (String?) -> Unit) {
        ApiService.getUpdates(userId, callback)
    }
}