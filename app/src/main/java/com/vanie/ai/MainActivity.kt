package com.vanie.ai

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.vanie.ai.accessibility.VanieAccessibilityService
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.VanieNlpEngine
import com.vanie.ai.notification.VanieNotificationService
import com.vanie.ai.python.VaniePythonBridge
import com.vanie.ai.receiver.VanieCallReceiver
import com.vanie.ai.service.VanieVoiceService
import com.vanie.ai.telephony.VanieTelephonyController
import com.vanie.ai.ui.components.VanieVoiceOverlay
import com.vanie.ai.ui.screens.ChatMessage
import com.vanie.ai.ui.screens.ChatScreen
import com.vanie.ai.ui.screens.DashboardScreen
import com.vanie.ai.ui.screens.PermissionsScreen
import com.vanie.ai.ui.theme.VANIETheme

class MainActivity : ComponentActivity() {

    private lateinit var nlpEngine: VanieNlpEngine
    private lateinit var pythonBridge: VaniePythonBridge
    private lateinit var deviceController: VanieDeviceController
    private lateinit var telephonyController: VanieTelephonyController
    private val callReceiver = VanieCallReceiver()

    private val requiredPermissions = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.CAMERA,
        Manifest.permission.CALL_PHONE,
        Manifest.permission.READ_CONTACTS,
        Manifest.permission.SEND_SMS,
        Manifest.permission.READ_PHONE_STATE
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        nlpEngine = VanieNlpEngine(this)
        pythonBridge = VaniePythonBridge(this)
        deviceController = VanieDeviceController(this)
        telephonyController = VanieTelephonyController(this)

        requestRequiredPermissions()
        startVoiceService()

        setContent {
            VANIETheme {
                var selectedTab by remember { mutableIntStateOf(0) }
                var isVoiceOverlayVisible by remember { mutableStateOf(false) }
                var lastSpokenText by remember { mutableStateOf("") }

                val messages = remember {
                    mutableStateListOf(
                        ChatMessage("vanie", "Hello! I am VANIE 🤖 (Virtual Agent of Neural Integrated Engine).\nPowered by Python & Kotlin on-device NPU/TPU hardware execution!\nSay 'Hey VANIE' to activate!")
                    )
                }

                Scaffold(
                    bottomBar = {
                        NavigationBar {
                            NavigationBarItem(
                                selected = selectedTab == 0,
                                onClick = { selectedTab = 0 },
                                icon = { Icon(Icons.Default.Chat, contentDescription = "Chat") },
                                label = { Text("VANIE Chat") }
                            )
                            NavigationBarItem(
                                selected = selectedTab == 1,
                                onClick = { selectedTab = 1 },
                                icon = { Icon(Icons.Default.Dashboard, contentDescription = "Controls") },
                                label = { Text("Controls") }
                            )
                            NavigationBarItem(
                                selected = selectedTab == 2,
                                onClick = { selectedTab = 2 },
                                icon = { Icon(Icons.Default.Shield, contentDescription = "Permissions") },
                                label = { Text("Setup") }
                            )
                        }
                    }
                ) { innerPadding ->
                    Surface(modifier = Modifier.padding(innerPadding)) {
                        when (selectedTab) {
                            0 -> ChatScreen(
                                messages = messages,
                                onSendMessage = { text ->
                                    messages.add(ChatMessage("user", text))
                                    // Process via Chaquopy Python Bridge
                                    val pyResult = pythonBridge.processWithPython(text)
                                    val responseText = pyResult.responseText
                                    messages.add(ChatMessage("vanie", responseText))
                                    executeAction(pyResult.actionCommand, pyResult.targetName, pyResult.messageBody)
                                },
                                onMicClick = {
                                    isVoiceOverlayVisible = true
                                }
                            )
                            1 -> DashboardScreen(
                                deviceController = deviceController,
                                telephonyController = telephonyController
                            )
                            2 -> PermissionsScreen(
                                onRequestPermissions = { requestRequiredPermissions() }
                            )
                        }

                        // Voice Overlay Bottom Sheet with Pulsing Vanie.png Visualizer
                        VanieVoiceOverlay(
                            isListening = isVoiceOverlayVisible,
                            spokenText = lastSpokenText,
                            onDismiss = { isVoiceOverlayVisible = false }
                        )
                    }
                }
            }
        }
    }

    private fun executeAction(action: ActionCommand, targetName: String?, messageBody: String?) {
        when (action) {
            ActionCommand.TORCH_ON -> deviceController.setTorchMode(true)
            ActionCommand.TORCH_OFF -> deviceController.setTorchMode(false)
            ActionCommand.WIFI_ON, ActionCommand.WIFI_OFF -> deviceController.openWifiSettings()
            ActionCommand.BLUETOOTH_ON, ActionCommand.BLUETOOTH_OFF -> deviceController.openBluetoothSettings()
            ActionCommand.DND_ON -> deviceController.setDoNotDisturb(true)
            ActionCommand.DND_OFF -> deviceController.setDoNotDisturb(false)
            ActionCommand.MODE_SILENT -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_SILENT)
            ActionCommand.MODE_VIBRATE -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_VIBRATE)
            ActionCommand.MODE_RING -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_NORMAL)
            ActionCommand.MAKE_CALL -> telephonyController.makeCall(targetName)
            ActionCommand.SEND_SMS -> telephonyController.sendSms(targetName, messageBody)
            ActionCommand.SEND_WHATSAPP -> {
                VanieAccessibilityService.pendingWhatsAppMessage = messageBody
                VanieAccessibilityService.isAutomationQueued = true
                telephonyController.sendWhatsAppMessage(targetName, messageBody)
            }
            ActionCommand.ANSWER_CALL -> callReceiver.answerCall(this)
            ActionCommand.REJECT_CALL -> callReceiver.cutCall(this)
            ActionCommand.BRIGHTNESS -> deviceController.setScreenBrightness(75)
            ActionCommand.ALARM -> deviceController.setAlarm(7, 0, "VANIE Voice Alarm")
            ActionCommand.BATTERY -> {
                val status = deviceController.getBatteryStatus()
                deviceController.setTorchMode(false)
            }
            ActionCommand.NOTIFICATION_READ -> {
                val notifs = VanieNotificationService.getUnreadNotificationsSummary()
            }
            ActionCommand.LAUNCH_APP -> {
                if (targetName != null) deviceController.launchApp(targetName)
            }
            else -> {}
        }
    }

    private fun requestRequiredPermissions() {
        val missingPermissions = requiredPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missingPermissions.toTypedArray(), 101)
        }
    }

    private fun startVoiceService() {
        try {
            val serviceIntent = Intent(this, VanieVoiceService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent)
            } else {
                startService(serviceIntent)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
