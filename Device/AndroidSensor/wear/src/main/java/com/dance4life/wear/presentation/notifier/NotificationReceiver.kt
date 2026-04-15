package com.dance4life.wear.presentation.notifier

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationManagerCompat
import com.dance4life.core.data.network.ApiService
import com.dance4life.core.utils.RejectManager

class NotificationReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {

        val inviteId = intent.getStringExtra("inviteId") ?: return

        when (intent.action) {

            "ACCEPT" -> {
                NotificationManagerCompat.from(context)
                    .cancel(inviteId.hashCode())

                ApiService.acceptInvite(inviteId)
            }

            "REJECT" -> {
                NotificationManagerCompat.from(context)
                    .cancel(inviteId.hashCode())

                RejectManager.registerReject(context)
            }
        }
    }
}