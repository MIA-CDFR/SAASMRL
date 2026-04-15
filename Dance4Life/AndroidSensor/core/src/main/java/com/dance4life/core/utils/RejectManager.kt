package com.dance4life.core.utils

import android.content.Context

object RejectManager {

    private const val PREF = "reject_prefs"
    private const val KEY = "reject_times"

    fun registerReject(context: Context) {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)

        val list = getRejects(context).toMutableList()
        list.add(System.currentTimeMillis())

        prefs.edit().putString(KEY, list.joinToString(",")).apply()
    }

    fun getRejectCount(context: Context, windowMillis: Long): Int {
        val now = System.currentTimeMillis()

        return getRejects(context).count {
            now - it <= windowMillis
        }
    }

    private fun getRejects(context: Context): List<Long> {
        val prefs = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        val raw = prefs.getString(KEY, "") ?: ""

        return if (raw.isEmpty()) emptyList()
        else raw.split(",").map { it.toLong() }
    }
}