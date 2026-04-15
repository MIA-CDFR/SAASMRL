package com.example.dance4life_phone.ui.notifier

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.core.app.NotificationManagerCompat
import com.dance4life.core.data.network.ApiService
import com.dance4life.core.utils.RejectManager

class NotificationReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {

        val inviteId = intent.getStringExtra("inviteId") ?: return
        Log.d("Convite", "Recebeu $inviteId")

        when (intent.action) {


            "ACCEPT" -> {
                // 1. remover imediatamente
                NotificationManagerCompat.from(context)
                    .cancel(inviteId.hashCode())
                Log.d("INVITE", "Aceitou $inviteId")

                // 2. chamar API (já é async internamente)
                ApiService.acceptInvite(inviteId)
            }

            "REJECT" -> {
                // remover imediatamente
                NotificationManagerCompat.from(context)
                    .cancel(inviteId.hashCode())

                RejectManager.registerReject(context)
            }
        }
    }
}