package com.vanie.ai.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class VanieAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "VanieAccessibility"
        var pendingWhatsAppMessage: String? = null
        var isAutomationQueued = false
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || !isAutomationQueued) return

        if (event.packageName == "com.whatsapp") {
            val rootNode = rootInActiveWindow ?: return
            handleWhatsAppAutomation(rootNode)
        }
    }

    private fun handleWhatsAppAutomation(rootNode: AccessibilityNodeInfo) {
        val textToInsert = pendingWhatsAppMessage ?: return

        // 1. Find Chat Entry Field
        val inputNodes = rootNode.findAccessibilityNodeInfosByViewId("com.whatsapp:id/entry")
        if (!inputNodes.isNullOrEmpty()) {
            val inputField = inputNodes[0]
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, textToInsert)
            }
            inputField.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)

            // 2. Find and Click Send Button
            val sendNodes = rootNode.findAccessibilityNodeInfosByViewId("com.whatsapp:id/send")
            if (!sendNodes.isNullOrEmpty()) {
                sendNodes[0].performAction(AccessibilityNodeInfo.ACTION_CLICK)
                Log.d(TAG, "WhatsApp message sent automatically via VANIE Accessibility Service!")
                isAutomationQueued = false
                pendingWhatsAppMessage = null
            }
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "VanieAccessibilityService Interrupted")
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d(TAG, "VanieAccessibilityService Connected!")
    }
}
