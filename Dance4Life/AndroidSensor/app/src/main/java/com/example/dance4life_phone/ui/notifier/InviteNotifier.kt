package com.example.dance4life_phone.ui.notifier

import android.Manifest
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat

object InviteNotifier {

    fun show(context: Context, inviteId: String, user: String) {

        val acceptIntent = Intent(context, NotificationReceiver::class.java).apply {
            action = "ACCEPT"
            putExtra("inviteId", inviteId)
            setPackage(context.packageName) // 🔥 FIX IMPORTANTE
        }

        val rejectIntent = Intent(context, NotificationReceiver::class.java).apply {
            action = "REJECT"
            putExtra("inviteId", inviteId)
            setPackage(context.packageName) // 🔥 FIX IMPORTANTE
        }

        val acceptPending = PendingIntent.getBroadcast(
            context,
            inviteId.hashCode(),
            acceptIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val rejectPending = PendingIntent.getBroadcast(
            context,
            inviteId.hashCode() + 1,
            rejectIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, "invite_channel")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Novo convite!")
            .setContentText("Convite de $user")
            .addAction(0, "Aceitar", acceptPending)
            .addAction(0, "Rejeitar", rejectPending)
            .setAutoCancel(true) // 🔥 UX melhor
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        // ✅ Android 13+ permission
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (ActivityCompat.checkSelfPermission(
                    context,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                return
            }
        }

        NotificationManagerCompat.from(context)
            .notify(inviteId.hashCode(), notification)
    }
}