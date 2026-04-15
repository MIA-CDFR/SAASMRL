package com.example.dance4life_phone.domain.location

import android.content.Context
import com.dance4life.core.data.model.LocationData
import com.dance4life.core.domain.location.LocationProvider


class PhoneLocationProvider(
    private val context: Context
) : LocationProvider {

    private val helper = LocationHelper(context)

    override fun start(onLocation: (LocationData) -> Unit) {
        helper.startLocationUpdates(onLocation)
    }
}