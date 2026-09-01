package com.vanie.ai

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.*
import androidx.compose.ui.Alignment
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
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
import com.vanie.ai.ui.screens.PermissionsScreen
import com.vanie.ai.ui.theme.AccentCyan
import com.vanie.ai.ui.theme.AccentPurple
import com.vanie.ai.ui.theme.VANIETheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

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
            val systemDark = isSystemInDarkTheme()
            var isDarkTheme by remember { mutableStateOf(systemDark) }

            VANIETheme(darkTheme = isDarkTheme) {
                var isVoiceOverlayVisible by remember { mutableStateOf(false) }
                var isMenuExpanded by remember { mutableStateOf(false) }
                var isAboutDialogOpen by remember { mutableStateOf(false) }
                var isSettingsSheetOpen by remember { mutableStateOf(false) }
                var isThinking by remember { mutableStateOf(false) }
                var lastSpokenText by remember { mutableStateOf("") }
                var clearAnimationTrigger by remember { mutableIntStateOf(0) }

                val messages = remember {
                    mutableStateListOf(
                        ChatMessage(
                            sender = "vanie",
                            text = "Hello! I am VANIE (Virtual Agent of Neural Integrated Engine).\nYour offline AI Assistant with hardware control, calling & messaging!\nSay 'Hey VANIE' to activate!"
                        )
                    )
                }

                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.background)
                ) {
                    // ChatScreen fills full screen edge-to-edge
                    ChatScreen(
                        messages = messages,
                        isThinking = isThinking,
                        clearAnimationTrigger = clearAnimationTrigger,
                        onSendMessage = { text ->
                            messages.add(ChatMessage(sender = "user", text = text))
                            isThinking = true
                            lifecycleScope.launch(Dispatchers.IO) {
                                val pyResult = pythonBridge.processWithPython(text)
                                val responseText = pyResult.responseText
                                kotlinx.coroutines.delay(500)
                                withContext(Dispatchers.Main) {
                                    isThinking = false
                                    messages.add(ChatMessage(sender = "vanie", text = responseText))
                                    executeAction(pyResult.actionCommand, pyResult.targetName, pyResult.messageBody, messages)
                                }
                            }
                        },
                        onMicClick = {
                            isVoiceOverlayVisible = true
                        }
                    )

                    // Floating Liquid Glass Top App Bar
                    VanieTopAppBar(
                        modifier = Modifier
                            .align(Alignment.TopCenter)
                            .statusBarsPadding()
                            .padding(horizontal = 12.dp, vertical = 6.dp),
                        onSettingsClick = { isSettingsSheetOpen = true },
                        onMenuClick = { isMenuExpanded = true },
                        isMenuExpanded = isMenuExpanded,
                        onDismissMenu = { isMenuExpanded = false },
                        isDarkTheme = isDarkTheme,
                        onToggleTheme = { isDarkTheme = !isDarkTheme },
                        onClearChat = {
                            messages.clear()
                            messages.add(
                                ChatMessage(
                                    sender = "vanie",
                                    text = "Hello! I am VANIE (Virtual Agent of Neural Integrated Engine).\nYour offline AI Assistant with hardware control, calling & messaging!\nSay 'Hey VANIE' to activate!"
                                )
                            )
                            clearAnimationTrigger += 1
                            isMenuExpanded = false
                        },
                        onOpenAbout = {
                            isMenuExpanded = false
                            isAboutDialogOpen = true
                        }
                    )

                    // Masterpiece Live Voice Overlay Bottom Sheet
                    VanieVoiceOverlay(
                        isListening = isVoiceOverlayVisible,
                        spokenText = lastSpokenText,
                        isThinking = isThinking,
                        responseText = lastSpokenText,
                        onResultText = { voiceText ->
                            messages.add(ChatMessage(sender = "user", text = voiceText))
                            isThinking = true
                            lifecycleScope.launch(Dispatchers.IO) {
                                val pyResult = pythonBridge.processWithPython(voiceText)
                                val responseText = pyResult.responseText
                                kotlinx.coroutines.delay(500)
                                withContext(Dispatchers.Main) {
                                    isThinking = false
                                    lastSpokenText = responseText
                                    messages.add(ChatMessage(sender = "vanie", text = responseText))
                                    executeAction(pyResult.actionCommand, pyResult.targetName, pyResult.messageBody, messages)
                                }
                            }
                        },
                        onDismiss = {
                            isVoiceOverlayVisible = false
                            lastSpokenText = ""
                        }
                    )

                    // Settings Modal Sheet
                    if (isSettingsSheetOpen) {
                        SettingsModalSheet(
                            onDismiss = { isSettingsSheetOpen = false },
                            currentPersona = nlpEngine.activePersona,
                            onPersonaSelected = { nlpEngine.activePersona = it },
                            onRequestPermissions = { requestRequiredPermissions() }
                        )
                    }

                    // About Developer Dialog
                    if (isAboutDialogOpen) {
                        AboutDeveloperDialog(
                            onDismiss = { isAboutDialogOpen = false },
                            onOpenGithub = {
                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/AyushHarinkhede"))
                                startActivity(intent)
                            },
                            onSendEmail = {
                                val intent = Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:ayushharinkhere2005@gmail.com"))
                                startActivity(intent)
                            }
                        )
                    }
                }
            }
        }
    }

    private fun executeAction(
        action: ActionCommand,
        targetName: String?,
        messageBody: String?,
        messages: MutableList<ChatMessage>
    ) {
        when (action) {
            ActionCommand.TORCH_ON -> deviceController.setTorchMode(true)
            ActionCommand.TORCH_OFF -> deviceController.setTorchMode(false)
            ActionCommand.WIFI_ON, ActionCommand.WIFI_OFF -> deviceController.openWifiSettings()
            ActionCommand.BLUETOOTH_ON -> {
                val res = deviceController.setBluetoothMode(true)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.BLUETOOTH_OFF -> {
                val res = deviceController.setBluetoothMode(false)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.DND_ON -> deviceController.setDoNotDisturb(true)
            ActionCommand.DND_OFF -> deviceController.setDoNotDisturb(false)
            ActionCommand.MODE_SILENT -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_SILENT)
            ActionCommand.MODE_VIBRATE -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_VIBRATE)
            ActionCommand.MODE_RING -> deviceController.setRingerMode(android.media.AudioManager.RINGER_MODE_NORMAL)
            ActionCommand.LOCATION_INFO -> {
                deviceController.openLocationSettings()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Location & GPS settings..."))
            }
            ActionCommand.MAKE_CALL -> {
                val res = telephonyController.makeCall(targetName)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.SEND_WHATSAPP_CALL -> {
                val res = telephonyController.makeWhatsAppCall(targetName)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.SEND_SMS -> {
                telephonyController.sendSms(targetName, messageBody)
                messages.add(ChatMessage(sender = "vanie", text = "Sent SMS to ${targetName ?: "contact"}"))
            }
            ActionCommand.SEND_WHATSAPP -> {
                val res = telephonyController.prepareWhatsAppDraft(targetName, messageBody)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.CONFIRM_SEND_DRAFT -> {
                val res = telephonyController.confirmAndSendPendingDraft()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.ANSWER_CALL -> callReceiver.answerCall(this)
            ActionCommand.REJECT_CALL -> callReceiver.cutCall(this)
            ActionCommand.BRIGHTNESS -> {
                val percent = targetName?.toIntOrNull() ?: 75
                deviceController.setScreenBrightness(percent)
                messages.add(ChatMessage(sender = "vanie", text = "Screen brightness adjusted to ${percent}%"))
            }
            ActionCommand.ALARM, ActionCommand.SET_ALARM -> {
                val parts = targetName?.split(":")
                val hour = parts?.getOrNull(0)?.toIntOrNull() ?: 7
                val minute = parts?.getOrNull(1)?.toIntOrNull() ?: 0
                deviceController.setAlarm(hour, minute, "VANIE Alarm")
                messages.add(ChatMessage(sender = "vanie", text = "⏰ Alarm set for ${String.format("%02d:%02d", hour, minute)}!"))
            }
            ActionCommand.CONFIRM_ALARM_AM -> {
                val pendingHour = com.vanie.ai.control.VanieAlarmState.pendingHour
                val pendingMin = com.vanie.ai.control.VanieAlarmState.pendingMinute
                val hour = if (pendingHour == 12) 0 else pendingHour
                deviceController.setAlarm(hour, pendingMin, "VANIE Alarm")
                messages.add(ChatMessage(sender = "vanie", text = "⏰ Subah (AM) ka alarm set for ${String.format("%02d:%02d", hour, pendingMin)}!"))
                com.vanie.ai.control.VanieAlarmState.isWaitingForAmPm = false
            }
            ActionCommand.CONFIRM_ALARM_PM -> {
                val pendingHour = com.vanie.ai.control.VanieAlarmState.pendingHour
                val pendingMin = com.vanie.ai.control.VanieAlarmState.pendingMinute
                val hour = if (pendingHour == 12) 12 else (pendingHour % 12) + 12
                deviceController.setAlarm(hour, pendingMin, "VANIE Alarm")
                messages.add(ChatMessage(sender = "vanie", text = "⏰ Shaam/Raat (PM) ka alarm set for ${String.format("%02d:%02d", hour, pendingMin)}!"))
                com.vanie.ai.control.VanieAlarmState.isWaitingForAmPm = false
            }
            ActionCommand.SET_TIMER -> {
                val sec = targetName?.toIntOrNull() ?: 60
                deviceController.setTimer(sec, "VANIE Timer")
                messages.add(ChatMessage(sender = "vanie", text = "⏱️ Timer set for $sec seconds!"))
            }
            ActionCommand.START_STOPWATCH -> {
                val res = com.vanie.ai.control.VanieStopwatch.start()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.PAUSE_STOPWATCH -> {
                val res = com.vanie.ai.control.VanieStopwatch.pause()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.RESET_STOPWATCH -> {
                val res = com.vanie.ai.control.VanieStopwatch.reset()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.ADD_TASK -> {
                val res = com.vanie.ai.control.VanieTaskManager.addTask(targetName ?: "")
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.SHOW_TASKS -> {
                val res = com.vanie.ai.control.VanieTaskManager.getTasks()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.CLEAR_TASKS -> {
                val res = com.vanie.ai.control.VanieTaskManager.clearTasks()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.BATTERY, ActionCommand.GET_DETAILED_BATTERY -> {
                val status = deviceController.getDetailedBatteryInfo()
                messages.add(ChatMessage(sender = "vanie", text = status))
            }
            ActionCommand.GET_NETWORK_INFO -> {
                val info = deviceController.getNetworkAndPhoneInfo()
                messages.add(ChatMessage(sender = "vanie", text = info))
            }
            ActionCommand.NOTIFICATION_READ -> {
                val notifs = VanieNotificationService.getUnreadNotificationsSummary()
                messages.add(ChatMessage(sender = "vanie", text = "$notifs"))
            }
            ActionCommand.VOLUME_UP -> {
                val res = deviceController.adjustVolume(true)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.VOLUME_DOWN -> {
                val res = deviceController.adjustVolume(false)
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.VOLUME_MUTE -> {
                val res = deviceController.muteVolume()
                messages.add(ChatMessage(sender = "vanie", text = res))
            }
            ActionCommand.OPEN_CAMERA -> {
                deviceController.openCamera()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Camera..."))
            }
            ActionCommand.OPEN_GALLERY -> {
                deviceController.openGallery()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Gallery..."))
            }
            ActionCommand.OPEN_SETTINGS -> {
                deviceController.openSettings()
                messages.add(ChatMessage(sender = "vanie", text = "Opening System Settings..."))
            }
            ActionCommand.OPEN_MAPS -> {
                deviceController.openMaps()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Maps..."))
            }
            ActionCommand.OPEN_PLAYSTORE -> {
                deviceController.openPlayStore()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Play Store..."))
            }
            ActionCommand.OPEN_CALCULATOR -> {
                deviceController.openCalculator()
                messages.add(ChatMessage(sender = "vanie", text = "Opening Calculator..."))
            }
            ActionCommand.LAUNCH_APP -> {
                if (targetName != null) {
                    val launched = deviceController.launchApp(targetName)
                    val msg = if (launched) "Launched $targetName" else "Could not launch app '$targetName'"
                    messages.add(ChatMessage(sender = "vanie", text = msg))
                }
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VanieTopAppBar(
    modifier: Modifier = Modifier,
    onSettingsClick: () -> Unit,
    onMenuClick: () -> Unit,
    isMenuExpanded: Boolean,
    onDismissMenu: () -> Unit,
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
    onClearChat: () -> Unit,
    onOpenAbout: () -> Unit
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f),
        tonalElevation = 6.dp,
        shadowElevation = 6.dp,
        border = BorderStroke(
            1.dp,
            Brush.horizontalGradient(
                listOf(
                    AccentCyan.copy(alpha = 0.4f),
                    AccentPurple.copy(alpha = 0.4f)
                )
            )
        )
    ) {
        TopAppBar(
            title = {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(start = 4.dp)
                ) {
                    // VANIE Cutout Logo (Pure logo image without background box or circle)
                    Image(
                        painter = painterResource(id = R.drawable.vanie),
                        contentDescription = "VANIE Cutout Logo",
                        modifier = Modifier.size(46.dp)
                    )
                }
            },
            actions = {
                // 1. Settings Icon
                IconButton(onClick = onSettingsClick) {
                    Icon(Icons.Default.Settings, contentDescription = "Settings", tint = MaterialTheme.colorScheme.primary)
                }

                // 2. More Options Icon (⋮)
                Box {
                    IconButton(onClick = onMenuClick) {
                        Icon(Icons.Default.MoreVert, contentDescription = "More Options")
                    }
                    DropdownMenu(
                        expanded = isMenuExpanded,
                        onDismissRequest = onDismissMenu
                    ) {
                        DropdownMenuItem(
                            text = {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text("Dark Mode")
                                    Switch(
                                        checked = isDarkTheme,
                                        onCheckedChange = {
                                            onToggleTheme()
                                        }
                                    )
                                }
                            },
                            onClick = {
                                onToggleTheme()
                            },
                            leadingIcon = { Icon(Icons.Default.Brightness4, contentDescription = null) }
                        )
                        DropdownMenuItem(
                            text = { Text("Clear Chat History") },
                            onClick = onClearChat,
                            leadingIcon = { Icon(Icons.Default.DeleteSweep, contentDescription = null) }
                        )
                        DropdownMenuItem(
                            text = { Text("Privacy Policy & Terms") },
                            onClick = { onDismissMenu() },
                            leadingIcon = { Icon(Icons.Default.Security, contentDescription = null) }
                        )
                        HorizontalDivider()
                        DropdownMenuItem(
                            text = { Text("About Developer") },
                            onClick = onOpenAbout,
                            leadingIcon = { Icon(Icons.Default.Code, contentDescription = null) }
                        )
                    }
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Transparent,
                scrolledContainerColor = Color.Transparent
            )
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsModalSheet(
    onDismiss: () -> Unit,
    currentPersona: String,
    onPersonaSelected: (String) -> Unit,
    onRequestPermissions: () -> Unit
) {
    val context = LocalContext.current
    var isVoiceEnabled by remember { mutableStateOf(VanieVoiceService.isVoiceEnabled(context)) }
    var speechSpeed by remember { mutableFloatStateOf(1.0f) }
    var selectedPersona by remember { mutableStateOf(currentPersona) }
    var isSetupExpanded by remember { mutableStateOf(false) }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp),
        containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Settings",
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                color = AccentCyan
            )

            // Setup & Permissions Option
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                border = BorderStroke(1.dp, AccentCyan.copy(alpha = 0.3f)),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Shield, contentDescription = null, tint = AccentCyan)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = "Setup & Permissions", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                        }
                        IconButton(onClick = { isSetupExpanded = !isSetupExpanded }) {
                            Icon(
                                imageVector = if (isSetupExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                                contentDescription = "Toggle Setup"
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Manage system permissions for voice commands, calling, messaging, and hardware control.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(
                        onClick = { onRequestPermissions() },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp)
                    ) {
                        Text("Grant Required Permissions")
                    }

                    if (isSetupExpanded) {
                        Spacer(modifier = Modifier.height(12.dp))
                        PermissionsScreen(onRequestPermissions = onRequestPermissions)
                    }
                }
            }

            // AI Persona & Voice Settings Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                border = BorderStroke(1.dp, AccentPurple.copy(alpha = 0.3f)),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "AI Voice & Response Persona", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(
                            selected = selectedPersona == "default",
                            onClick = {
                                selectedPersona = "default"
                                onPersonaSelected("default")
                            },
                            label = { Text("Default") },
                            shape = CircleShape
                        )
                        FilterChip(
                            selected = selectedPersona == "cyberpunk",
                            onClick = {
                                selectedPersona = "cyberpunk"
                                onPersonaSelected("cyberpunk")
                            },
                            label = { Text("Cyberpunk") },
                            shape = CircleShape
                        )
                        FilterChip(
                            selected = selectedPersona == "hinglish",
                            onClick = {
                                selectedPersona = "hinglish"
                                onPersonaSelected("hinglish")
                            },
                            label = { Text("Hinglish") },
                            shape = CircleShape
                        )
                    }
                }
            }

            // Voice Listener Toggle Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                border = BorderStroke(1.dp, AccentCyan.copy(alpha = 0.3f)),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f))
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Voice Wake-Word Listener (\"Hey VANIE\")",
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = if (isVoiceEnabled) "Background wake-word detection is Active" else "Disabled to save battery",
                            fontSize = 12.sp,
                            color = AccentCyan
                        )
                    }

                    Switch(
                        checked = isVoiceEnabled,
                        onCheckedChange = { enabled ->
                            isVoiceEnabled = enabled
                            VanieVoiceService.setVoiceEnabled(context, enabled)
                        }
                    )
                }
            }

            // Speech Speed Slider
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                border = BorderStroke(1.dp, AccentPurple.copy(alpha = 0.3f)),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "TTS Speech Speed: ${String.format("%.1fx", speechSpeed)}", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Slider(
                        value = speechSpeed,
                        onValueChange = { speechSpeed = it },
                        valueRange = 0.5f..2.0f,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            Button(
                onClick = onDismiss,
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text("Save & Close Settings")
            }
        }
    }
}

@Composable
fun AboutDeveloperDialog(onDismiss: () -> Unit, onOpenGithub: () -> Unit, onSendEmail: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        shape = RoundedCornerShape(24.dp),
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // VANIE Cutout Logo (Pure logo image without background box or circle)
                Image(
                    painter = painterResource(id = R.drawable.vanie),
                    contentDescription = "VANIE Cutout Logo",
                    modifier = Modifier.size(36.dp)
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text("About Developer", fontWeight = FontWeight.Bold)
            }
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("VANIE - Virtual Agent of Neural Integrated Engine", fontWeight = FontWeight.Bold, color = AccentCyan)
                Text("Created by Ayush Harinkhede", fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(4.dp))
                Text("Email: ayushharinkhere2005@gmail.com", fontSize = 13.sp, fontFamily = FontFamily.Monospace)
                Text("GitHub: AyushHarinkhede", fontSize = 13.sp, fontFamily = FontFamily.Monospace)
            }
        },
        confirmButton = {
            Button(onClick = onOpenGithub, shape = CircleShape) {
                Icon(Icons.Default.Code, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("GitHub")
            }
        },
        dismissButton = {
            OutlinedButton(onClick = onSendEmail, shape = CircleShape) {
                Icon(Icons.Default.Email, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Email")
            }
        }
    )
}

