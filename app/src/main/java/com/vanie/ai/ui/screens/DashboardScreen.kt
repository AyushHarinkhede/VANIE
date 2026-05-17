package com.vanie.ai.ui.screens

import android.media.AudioManager
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.telephony.VanieTelephonyController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    deviceController: VanieDeviceController,
    telephonyController: VanieTelephonyController
) {
    var torchState by remember { mutableStateOf(false) }
    var dndState by remember { mutableStateOf(false) }

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
            text = "Instant 0-delay offline system controls powered by VANIE",
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
                subtitle = if (torchState) "ON" else "OFF",
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
                subtitle = if (dndState) "Active" else "Off",
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
                subtitle = "Tap to open",
                icon = Icons.Default.Wifi,
                isActive = false,
                onClick = { deviceController.openWifiSettings() },
                modifier = Modifier.weight(1f)
            )

            ControlCard(
                title = "Bluetooth",
                subtitle = "Tap to open",
                icon = Icons.Default.Bluetooth,
                isActive = false,
                onClick = { deviceController.openBluetoothSettings() },
                modifier = Modifier.weight(1f)
            )
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
        modifier = modifier.height(110.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isActive) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(14.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = if (isActive) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
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
