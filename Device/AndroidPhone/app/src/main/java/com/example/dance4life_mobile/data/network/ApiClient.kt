package com.example.dance4life_mobile.data.network

import okhttp3.OkHttpClient

object ApiClient {
    val client: OkHttpClient by lazy {
        OkHttpClient()
    }
}