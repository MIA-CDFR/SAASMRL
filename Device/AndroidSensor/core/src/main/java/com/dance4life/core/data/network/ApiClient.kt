package com.dance4life.core.data.network

import okhttp3.OkHttpClient

object ApiClient {
    val client: OkHttpClient by lazy {
        OkHttpClient()
    }
}