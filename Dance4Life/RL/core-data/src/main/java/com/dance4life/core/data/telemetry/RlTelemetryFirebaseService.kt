package com.dance4life.core.data.telemetry

import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.tasks.await
import java.security.MessageDigest

class RlTelemetryFirebaseService(private val firestore: FirebaseFirestore) {

    suspend fun uploadEvent(event: RlEvent, anonUserId: String): Result<String> = runCatching {
        val doc = mapOf(
            "ts_client_ms" to event.tsClientMs,
            "ts_server" to com.google.firebase.firestore.FieldValue.serverTimestamp(),
            "device_id_hash" to event.deviceIdHash,
            "model_version" to event.modelVersion,
            "app_version" to event.appVersion,
            "state" to mapOf(
                "steps_last_hour" to event.stepsLastHour,
                "sedentary_minutes_today" to event.sedentaryMinutesToday,
                "energy_level" to event.energyLevel,
                "mobility_confidence" to event.mobilityConfidence,
            ),
            "action" to mapOf(
                "action_id" to event.actionId,
                "action_index" to event.actionIndex,
            ),
            "policy" to mapOf(
                "source" to event.policySource,
                "epsilon" to 0.0,
            ),
        )

        firestore
            .collection("users")
            .document(anonUserId)
            .collection("events")
            .add(doc)
            .await()
            .id
    }

    suspend fun uploadOutcome(outcome: RlOutcome, anonUserId: String): Result<String> = runCatching {
        val doc = mapOf(
            "event_id" to outcome.eventId,
            "ts_client_ms" to outcome.tsClientMs,
            "ts_server" to com.google.firebase.firestore.FieldValue.serverTimestamp(),
            "accepted" to outcome.accepted,
            "completed" to outcome.completed,
            "completion_minutes" to outcome.completionMinutes,
            "reward_proxy" to outcome.rewardProxy,
        )

        firestore
            .collection("users")
            .document(anonUserId)
            .collection("outcomes")
            .add(doc)
            .await()
            .id
    }

    companion object {
        fun getOrCreateAnonId(context: android.content.Context): String {
            val pref = context.getSharedPreferences("dance4life_telemetry", android.content.Context.MODE_PRIVATE)
            return pref.getString("anon_user_id", null) ?: run {
                val newId = java.util.UUID.randomUUID().toString()
                pref.edit().putString("anon_user_id", newId).apply()
                newId
            }
        }

        fun hashDeviceId(context: android.content.Context): String {
            val androidId = android.provider.Settings.Secure.getString(
                context.contentResolver,
                android.provider.Settings.Secure.ANDROID_ID
            )
            val digest = MessageDigest.getInstance("SHA-256")
            return digest.digest(androidId.toByteArray()).joinToString("") { "%02x".format(it) }
        }
    }
}
