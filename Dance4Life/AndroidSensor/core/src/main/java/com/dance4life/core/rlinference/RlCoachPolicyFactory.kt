package com.dance4life.core.rlinference

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
