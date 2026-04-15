package com.dance4life.core.domain.location

import com.dance4life.core.data.model.LocationData

interface LocationProvider {
    fun start(onLocation: (LocationData) -> Unit)
}