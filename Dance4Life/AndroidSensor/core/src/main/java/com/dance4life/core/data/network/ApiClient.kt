package com.dance4life.core.data.network

import okhttp3.Dns
import okhttp3.OkHttpClient
import java.net.Inet4Address
import java.net.InetAddress

object ApiClient {
    val client: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .dns(object : Dns {
                override fun lookup(hostname: String): List<InetAddress> =
                    Dns.SYSTEM.lookup(hostname).filter { it is Inet4Address }
            })
            .build()
    }
}