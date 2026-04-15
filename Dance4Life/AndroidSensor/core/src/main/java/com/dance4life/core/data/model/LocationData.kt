package com.dance4life.core.data.model

data class LocationData(
    val latitude: Double,
    val longitude: Double,
    val country: String?,
    val city: String?,
    val street: String?
)