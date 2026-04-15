package com.dance4life.core.data.telemetry

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.flow.first
import java.util.concurrent.TimeUnit

class RlTelemetrySyncWorker(
    appContext: Context,
    params: androidx.work.WorkerParameters,
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            val context = applicationContext
            val db = Dance4LifeDatabase.getInstance(context)
            val firestore = FirebaseFirestore.getInstance()
            val telemetryService = RlTelemetryFirebaseService(firestore)

            val anonUserId = RlTelemetryFirebaseService.getOrCreateAnonId(context)

            val unsyncedEvents = db.rlEventDao().getUnsynced()
            val unsyncedOutcomes = db.rlOutcomeDao().getUnsynced()

            var successCount = 0
            var failureCount = 0

            for (event in unsyncedEvents) {
                val result = telemetryService.uploadEvent(
                    RlEvent(
                        eventId = event.eventId,
                        tsClientMs = event.tsClientMs,
                        deviceIdHash = event.deviceIdHash,
                        modelVersion = event.modelVersion,
                        appVersion = event.appVersion,
                        stepsLastHour = event.stepsLastHour,
                        sedentaryMinutesToday = event.sedentaryMinutesToday,
                        energyLevel = event.energyLevel,
                        mobilityConfidence = event.mobilityConfidence,
                        actionId = event.actionId,
                        actionIndex = event.actionIndex,
                        policySource = event.policySource,
                    ),
                    anonUserId,
                )
                if (result.isSuccess) successCount++ else failureCount++
            }

            for (outcome in unsyncedOutcomes) {
                val result = telemetryService.uploadOutcome(
                    RlOutcome(
                        outcomeId = outcome.outcomeId,
                        eventId = outcome.eventId,
                        tsClientMs = outcome.tsClientMs,
                        accepted = outcome.accepted,
                        completed = outcome.completed,
                        completionMinutes = outcome.completionMinutes,
                        rewardProxy = outcome.rewardProxy,
                    ),
                    anonUserId,
                )
                if (result.isSuccess) successCount++ else failureCount++
            }

            if (failureCount == 0 && successCount > 0) {
                db.rlEventDao().markSynced(unsyncedEvents.map { it.id }, System.currentTimeMillis())
                db.rlOutcomeDao().markSynced(unsyncedOutcomes.map { it.id }, System.currentTimeMillis())
                Result.success()
            } else if (failureCount > 0) {
                Result.retry()
            } else {
                Result.success()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }

    companion object {
        const val WORK_NAME = "rl_telemetry_sync"

        fun schedulePeriodicSync(context: Context) {
            val syncRequest = PeriodicWorkRequestBuilder<RlTelemetrySyncWorker>(
                15,
                TimeUnit.MINUTES,
            ).build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                androidx.work.ExistingPeriodicWorkPolicy.KEEP,
                syncRequest,
            )
        }
    }
}
