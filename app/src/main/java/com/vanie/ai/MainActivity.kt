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
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
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
                var isPermissionsSheetOpen by remember { mutableStateOf(false) }
                var isSettingsSheetOpen by remember { mutableStateOf(false) }
                var isThinking by remember { mutableStateOf(false) }
                var lastSpokenText by remember { mutableStateOf("") }

                val messages = remember {
                    mutableStateListOf(
                        ChatMessage(
                            sender = "vanie",
                            text = "Hello! I am VANIE 🤖 (Virtual Agent of Neural Integrated Engine).\nYour offline AI Assistant with hardware control, calling & messaging!\nSay 'Hey VANIE' to activate!"
                        )
                    )
                }

                Scaffold(
                    topBar = {
                        VanieTopAppBar(
                            onPermissionsClick = { isPermissionsSheetOpen = true },
                            onSettingsClick = { isSettingsSheetOpen = true },
                            onMenuClick = { isMenuExpanded = true },
                            isMenuExpanded = isMenuExpanded,
                            onDismissMenu = { isMenuExpanded = false },
                            isDarkTheme = isDarkTheme,
                            onToggleTheme = { isDarkTheme = !isDarkTheme },
                            onOpenAbout = {
                                isMenuExpanded = false
                                isAboutDialogOpen = true
                            }
                        )
                    }
                ) { innerPadding ->
                    Box(modifier = Modifier.padding(innerPadding)) {
                        // Single Unified Chat Home Screen
                        ChatScreen(
                            messages = messages,
                            isThinking = isThinking,
                            onSendMessage = { text ->
                                messages.add(ChatMessage(sender = "user", text = text))
                                isThinking = true
                                lifecycleScope.launch(Dispatchers.IO) {
                                    val pyResult = pythonBridge.processWithPython(text)
                                    val responseText = pyResult.responseText
                                    withContext(Dispatchers.Main) {
                                        isThinking = false
                                        messages.add(ChatMessage(sender = "vanie", text = responseText))
                                        executeAction(pyResult.actionCommand, pyResult.targetName, pyResult.messageBody)
                                    }
                                }
                            },
                            onMicClick = {
                                isVoiceOverlayVisible = true
                            }
                        )

                        // Voice Overlay Bottom Sheet with Pulsing Vanie.png Visualizer
                        VanieVoiceOverlay(
                            isListening = isVoiceOverlayVisible,
                            spokenText = lastSpokenText,
                            onDismiss = { isVoiceOverlayVisible = false }
                        )

                        // Animated Hover Permissions Sheet
                        if (isPermissionsSheetOpen) {
                            PermissionsModalSheet(
                                onDismiss = { isPermissionsSheetOpen = false },
                                onRequestPermissions = { requestRequiredPermissions() }
                            )
                        }

                        // Animated Hover Settings Sheet with Voice Trigger Toggle
                        if (isSettingsSheetOpen) {
                            SettingsModalSheet(
                                onDismiss = { isSettingsSheetOpen = false }
                            )
                        }

                        // About Developer Dialog (Ayush Harinkhede)
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
                Toast.makeText(this, status, Toast.LENGTH_LONG).show()
            }
            ActionCommand.NOTIFICATION_READ -> {
                val notifs = VanieNotificationService.getUnreadNotificationsSummary()
                Toast.makeText(this, notifs, Toast.LENGTH_LONG).show()
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VanieTopAppBar(
    onPermissionsClick: () -> Unit,
    onSettingsClick: () -> Unit,
    onMenuClick: () -> Unit,
    isMenuExpanded: Boolean,
    onDismissMenu: () -> Unit,
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit,
    onOpenAbout: () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "headerLogo")
    val logoScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = 1.15f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "logoScale"
    )

    TopAppBar(
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(40.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(38.dp * logoScale)
                            .clip(CircleShape)
                            .background(AccentCyan.copy(alpha = 0.2f))
                    )
                    Image(
                        painter = painterResource(id = R.drawable.vanie),
                        contentDescription = "VANIE Logo",
                        modifier = Modifier
                            .size(34.dp)
                            .clip(CircleShape)
                    )
                }
                Spacer(modifier = Modifier.width(10.dp))
                Column {
                    Text(
                        text = "VANIE AI",
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "Virtual Agent of Neural Integrated Engine",
                        style = MaterialTheme.typography.labelSmall,
                        color = AccentCyan,
                        fontSize = 10.sp
                    )
                }
            }
        },
        actions = {
            // 1. Setup / Permissions Icon
            IconButton(onClick = onPermissionsClick) {
                Icon(Icons.Default.Shield, contentDescription = "Setup Permissions", tint = AccentCyan)
            }

            // 2. Settings Icon
            IconButton(onClick = onSettingsClick) {
                Icon(Icons.Default.Settings, contentDescription = "Settings", tint = AccentPurple)
            }

            // 3. More Options Icon (⋮)
            Box {
                IconButton(onClick = onMenuClick) {
                    Icon(Icons.Default.MoreVert, contentDescription = "More Options")
                }
                DropdownMenu(
                    expanded = isMenuExpanded,
                    onDismissRequest = onDismissMenu
                ) {
                    DropdownMenuItem(
                        text = { Text("Theme: ${if (isDarkTheme) "Dark 🌙" else "Light ☀️"}") },
                        onClick = {
                            onToggleTheme()
                            onDismissMenu()
                        },
                        leadingIcon = { Icon(Icons.Default.Brightness4, contentDescription = null) }
                    )
                    DropdownMenuItem(
                        text = { Text("Privacy Policy & Terms") },
                        onClick = { onDismissMenu() },
                        leadingIcon = { Icon(Icons.Default.Security, contentDescription = null) }
                    )
                    Divider()
                    DropdownMenuItem(
                        text = { Text("About Developer") },
                        onClick = onOpenAbout,
                        leadingIcon = { Icon(Icons.Default.Code, contentDescription = null) }
                    )
                }
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.surface)
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionsModalSheet(onDismiss: () -> Unit, onRequestPermissions: () -> Unit) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)
    ) {
        PermissionsScreen(onRequestPermissions = onRequestPermissions)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsModalSheet(onDismiss: () -> Unit) {
    val context = LocalContext.current
    var isVoiceEnabled by remember { mutableStateOf(VanieVoiceService.isVoiceEnabled(context)) }
    var speechSpeed by remember { mutableFloatStateOf(1.0f) }
    var speechPitch by remember { mutableFloatStateOf(1.0f) }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp)
        ) {
            Text(
                text = "VANIE System Settings",
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                color = AccentCyan
            )

            // Voice Listener Toggle Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
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
                            text = if (isVoiceEnabled) "Background wake-word detection is ACTIVE" else "DISABLED to save battery & privacy",
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
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
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

            // Speech Pitch Slider
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "TTS Voice Pitch: ${String.format("%.1fx", speechPitch)}", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Slider(
                        value = speechPitch,
                        onValueChange = { speechPitch = it },
                        valueRange = 0.5f..1.5f,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            Button(
                onClick = onDismiss,
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(14.dp)
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
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Image(
                    painter = painterResource(id = R.drawable.vanie),
                    contentDescription = null,
                    modifier = Modifier.size(32.dp).clip(CircleShape)
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text("About Developer", fontWeight = FontWeight.Bold)
            }
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("VANIE - Virtual Agent of Neural Integrated Engine", fontWeight = FontWeight.Bold, color = AccentCyan)
                Text("Created with ❤️ by Ayush Harinkhede", fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(4.dp))
                Text("📧 Email: ayushharinkhere2005@gmail.com", fontSize = 13.sp, fontFamily = FontFamily.Monospace)
                Text("💻 GitHub: AyushHarinkhede", fontSize = 13.sp, fontFamily = FontFamily.Monospace)
            }
        },
        confirmButton = {
            Button(onClick = onOpenGithub) {
                Icon(Icons.Default.Code, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("GitHub")
            }
        },
        dismissButton = {
            OutlinedButton(onClick = onSendEmail) {
                Icon(Icons.Default.Email, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("Email")
            }
        }
    )
}
