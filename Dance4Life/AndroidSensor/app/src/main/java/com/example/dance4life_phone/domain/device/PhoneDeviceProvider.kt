package com.example.dance4life_phone.domain.device

import android.content.Context
import com.dance4life.core.domain.device.DeviceProvider

class PhoneDeviceProvider(
    private val context: Context
) : DeviceProvider {

    override fun getUserId(): String {
        return DeviceHelper.getAndroidID(context)
    }
}