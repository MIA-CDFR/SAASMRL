package com.dance4life.wear.domain.device

import android.content.Context
import android.provider.Settings
import com.dance4life.core.domain.device.DeviceProvider

class WearDeviceProvider(
    private val context: Context
) : DeviceProvider {

    override fun getUserId(): String {
        return Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
    }
}