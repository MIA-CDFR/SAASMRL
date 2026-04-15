package com.dance4life.wear.domain.device

import android.annotation.SuppressLint
import android.content.Context
import android.provider.Settings
import androidx.core.content.edit
import java.util.UUID

object DeviceHelper {

    @SuppressLint("HardwareIds")
    fun getAndroidID(context: Context): String {
        return Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
    }


    private const val PREF_NAME = "app_prefs"
    private const val KEY_ID = "unique_id"

    fun getUniqueId(context: Context): String {
        val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)

        var id = prefs.getString(KEY_ID, null)

        if (id == null) {
            id = UUID.randomUUID().toString()
            prefs.edit { putString(KEY_ID, id) }
        }

        return id
    }
}