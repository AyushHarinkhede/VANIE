package com.vanie.ai.ui.screens

import android.media.AudioManager
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.telephony.VanieTelephonyController
import com.vanie.ai.ui.theme.AccentCyan

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    deviceController: VanieDeviceController,
    telephonyController: VanieTelephonyController
) {
    var torchState by remember { mutableStateOf(false) }
    var dndState by remember { mutableStateOf(false) }
    var brightnessValue by remember { mutableFloatStateOf(0.75f) }
    var batteryText by remember { mutableStateOf("Tap to check battery level") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Hardware Control Center",
            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
            color = MaterialTheme.colorScheme.onBackground
        )
        Text(
            text = "Instant 0-delay offline system controls powered by VANIE NPU Engine",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        // Grid Row 1: Torch & DND
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ControlCard(
                title = "Flashlight",
                subtitle = if (torchState) "ACTIVE" else "OFF",
                icon = Icons.Default.FlashOn,
                isActive = torchState,
                onClick = {
                    torchState = !torchState
                    deviceController.setTorchMode(torchState)
                },
                modifier = Modifier.weight(1f)
            )

            ControlCard(
                title = "Do Not Disturb",
                subtitle = if (dndState) "ACTIVE" else "OFF",
                icon = Icons.Default.DoNotDisturbOn,
                isActive = dndState,
                onClick = {
                    dndState = !dndState
                    deviceController.setDoNotDisturb(dndState)
                },
                modifier = Modifier.weight(1f)
            )
        }

        // Grid Row 2: Wi-Fi & Bluetooth
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ControlCard(
                title = "Wi-Fi Control",
                subtitle = "Tap to manage",
                icon = Icons.Default.Wifi,
                isActive = false,
                onClick = { deviceController.openWifiSettings() },
                modifier = Modifier.weight(1f)
            )

            ControlCard(
                title = "Bluetooth",
                subtitle = "Tap to manage",
                icon = Icons.Default.Bluetooth,
                isActive = false,
                onClick = { deviceController.openBluetoothSettings() },
                modifier = Modifier.weight(1f)
            )
        }

        // Screen Brightness Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Brightness6, contentDescription = null, tint = AccentCyan)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Screen Brightness: ${(brightnessValue * 100).toInt()}%",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                Slider(
                    value = brightnessValue,
                    onValueChange = {
                        brightnessValue = it
                        deviceController.setScreenBrightness((it * 100).toInt())
                    },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        // Audio Profile Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Sound Profiles",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    ElevatedButton(onClick = { deviceController.setRingerMode(AudioManager.RINGER_MODE_NORMAL) }) {
                        Icon(Icons.Default.VolumeUp, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Ring")
                    }
                    ElevatedButton(onClick = { deviceController.setRingerMode(AudioManager.RINGER_MODE_VIBRATE) }) {
                        Icon(Icons.Default.Vibration, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Vibrate")
                    }
                    ElevatedButton(onClick = { deviceController.setRingerMode(AudioManager.RINGER_MODE_SILENT) }) {
                        Icon(Icons.Default.VolumeOff, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Silent")
                    }
                }
            }
        }

        // Battery Status Card
        Card(
            onClick = { batteryText = deviceController.getBatteryStatus() },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.BatteryChargingFull, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(32.dp))
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(text = "Battery Status", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Text(text = batteryText, fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f))
                }
            }
        }

        // Telephony Actions Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Telephony & Messaging Shortcuts",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    OutlinedButton(onClick = { telephonyController.makeCall(null) }) {
                        Icon(Icons.Default.Call, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Direct Call")
                    }
                    OutlinedButton(onClick = { telephonyController.sendSms(null, null) }) {
                        Icon(Icons.Default.Message, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Send SMS")
                    }
                }
            }
        }
    }
}

@Composable
fun ControlCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    isActive: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier.height(115.dp),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isActive) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = if (isActive) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(28.dp)
            )
            Column {
                Text(
                    text = title,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = if (isActive) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = subtitle,
                    fontSize = 12.sp,
                    color = if (isActive) MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f) else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                )
            }
        }
    }
}
