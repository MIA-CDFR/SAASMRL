package com.dance4life.plugins.rlinference

import android.content.Context

object RlCoachPolicyFactory {
    fun create(context: Context): RlCoachPolicy {
        return try {
            OnnxRlCoachPolicy(context = context)
        } catch (_: Throwable) {
            StubRlCoachPolicy()
        }
    }
}
