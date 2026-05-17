package com.vanie.ai.notification

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log

class VanieNotificationService : NotificationListenerService() {

    companion object {
        private const val TAG = "VanieNotificationService"
        private var instance: VanieNotificationService? = null

        fun getUnreadNotificationsSummary(): String {
            val service = instance ?: return "Notification listener permission is not enabled."
            val notifications = service.activeNotifications
            if (notifications.isNullOrEmpty()) {
                return "You have no unread notifications right now."
            }

            val summaryList = mutableListOf<String>()
            for (sbn in notifications.take(5)) {
                val extras = sbn.notification.extras
                val title = extras.getString("android.title") ?: "System"
                val text = extras.getCharSequence("android.text")?.toString() ?: ""
                val appName = sbn.packageName.substringAfterLast(".")
                if (text.isNotBlank()) {
                    summaryList.add("$appName from $title: $text")
                }
            }

            return if (summaryList.isNotEmpty()) {
                "Here are your recent notifications: " + summaryList.joinToString(". ")
            } else {
                "No new unread notification text."
            }
        }
    }

    override fun onListenerConnected() {
        super.onListenerConnected()
        instance = this
        Log.d(TAG, "Notification Listener Connected!")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        Log.d(TAG, "Notification posted from: ${sbn?.packageName}")
    }

    override fun onListenerDisconnected() {
        super.onListenerDisconnected()
        instance = null
    }
}
