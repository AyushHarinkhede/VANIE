package com.vanie.ai.control

import android.app.NotificationManager
import android.bluetooth.BluetoothAdapter
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.hardware.camera2.CameraManager
import android.media.AudioManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.provider.AlarmClock
import android.provider.Settings
import android.telephony.TelephonyManager
import android.widget.Toast
import kotlin.math.roundToInt

class VanieDeviceController(private val context: Context) {

    private val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

    fun setTorchMode(enabled: Boolean): Boolean {
        return try {
            val cameraId = cameraManager.cameraIdList.firstOrNull { id ->
                cameraManager.getCameraCharacteristics(id)
                    .get(android.hardware.camera2.CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
            }
            if (cameraId != null) {
                cameraManager.setTorchMode(cameraId, enabled)
                Toast.makeText(context, if (enabled) "Torch Turned ON" else "Torch Turned OFF", Toast.LENGTH_SHORT).show()
                true
            } else {
                Toast.makeText(context, "No Camera Flash Available", Toast.LENGTH_SHORT).show()
                false
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "Torch Error: ${e.message}", Toast.LENGTH_SHORT).show()
            false
        }
    }

    fun setBluetoothMode(enable: Boolean): String {
        return try {
            val adapter = BluetoothAdapter.getDefaultAdapter()
            if (adapter == null) {
                return "Bluetooth is not supported on this device."
            }
            if (enable) {
                if (!adapter.isEnabled) {
                    @Suppress("DEPRECATION")
                    adapter.enable()
                    "Bluetooth turned ON directly."
                } else {
                    "Bluetooth is already ON."
                }
            } else {
                if (adapter.isEnabled) {
                    @Suppress("DEPRECATION")
                    adapter.disable()
                    "Bluetooth turned OFF directly."
                } else {
                    "Bluetooth is already OFF."
                }
            }
        } catch (e: Exception) {
            openBluetoothSettings()
            "Opening Bluetooth settings..."
        }
    }

    fun openWifiSettings() {
        try {
            val intent = Intent(Settings.ACTION_WIFI_SETTINGS).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Could not open Wi-Fi settings", Toast.LENGTH_SHORT).show()
        }
    }

    fun openBluetoothSettings() {
        try {
            val intent = Intent(Settings.ACTION_BLUETOOTH_SETTINGS).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Could not open Bluetooth settings", Toast.LENGTH_SHORT).show()
        }
    }

    fun openLocationSettings() {
        try {
            val intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Could not open Location settings", Toast.LENGTH_SHORT).show()
        }
    }

    fun setRingerMode(mode: Int): Boolean {
        return try {
            audioManager.ringerMode = mode
            val modeName = when (mode) {
                AudioManager.RINGER_MODE_SILENT -> "Silent Mode"
                AudioManager.RINGER_MODE_VIBRATE -> "Vibrate Mode"
                else -> "Normal Ringing Mode"
            }
            Toast.makeText(context, "Audio set to $modeName", Toast.LENGTH_SHORT).show()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "Audio Permission required", Toast.LENGTH_SHORT).show()
            false
        }
    }

    fun setDoNotDisturb(enable: Boolean): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!notificationManager.isNotificationPolicyAccessGranted) {
                val intent = Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                context.startActivity(intent)
                Toast.makeText(context, "Grant DND Policy access to VANIE", Toast.LENGTH_LONG).show()
                return false
            }

            return try {
                val filter = if (enable) {
                    NotificationManager.INTERRUPTION_FILTER_NONE
                } else {
                    NotificationManager.INTERRUPTION_FILTER_ALL
                }
                notificationManager.setInterruptionFilter(filter)
                Toast.makeText(context, if (enable) "DND Activated" else "DND Disabled", Toast.LENGTH_SHORT).show()
                true
            } catch (e: Exception) {
                e.printStackTrace()
                false
            }
        }
        return false
    }

    fun setScreenBrightness(percent: Int): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.System.canWrite(context)) {
                val intent = Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                context.startActivity(intent)
                Toast.makeText(context, "Grant Write Settings permission to change brightness", Toast.LENGTH_LONG).show()
                return false
            }
        }

        return try {
            val brightnessVal = ((percent.coerceIn(0, 100) / 100f) * 255).roundToInt()
            Settings.System.putInt(context.contentResolver, Settings.System.SCREEN_BRIGHTNESS, brightnessVal)
            Toast.makeText(context, "Brightness set to $percent%", Toast.LENGTH_SHORT).show()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun launchApp(appNameQuery: String): Boolean {
        val pm = context.packageManager
        val cleanQuery = appNameQuery.lowercase().trim()

        val directPackage = when {
            cleanQuery.contains("youtube") -> "com.google.android.youtube"
            cleanQuery.contains("whatsapp") -> "com.whatsapp"
            cleanQuery.contains("chrome") -> "com.android.chrome"
            cleanQuery.contains("camera") -> "com.google.android.GoogleCamera"
            cleanQuery.contains("photo") || cleanQuery.contains("gallery") -> "com.google.android.apps.photos"
            cleanQuery.contains("map") -> "com.google.android.apps.maps"
            cleanQuery.contains("gmail") || cleanQuery.contains("email") -> "com.google.android.gm"
            cleanQuery.contains("setting") -> "com.android.settings"
            cleanQuery.contains("store") || cleanQuery.contains("play") -> "com.android.vending"
            cleanQuery.contains("clock") || cleanQuery.contains("timer") -> "com.google.android.deskclock"
            else -> null
        }

        if (directPackage != null) {
            val launchIntent = pm.getLaunchIntentForPackage(directPackage)
            if (launchIntent != null) {
                launchIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(launchIntent)
                return true
            }
        }

        val packages = pm.getInstalledPackages(0)
        val matchedPkg = packages.firstOrNull {
            it.packageName.contains(cleanQuery, ignoreCase = true) ||
            pm.getApplicationLabel(it.applicationInfo).toString().contains(cleanQuery, ignoreCase = true)
        }?.packageName

        if (matchedPkg != null) {
            val launchIntent = pm.getLaunchIntentForPackage(matchedPkg)
            if (launchIntent != null) {
                launchIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(launchIntent)
                return true
            }
        }
        Toast.makeText(context, "Could not find app '$appNameQuery'", Toast.LENGTH_SHORT).show()
        return false
    }

    fun setAlarm(hour: Int = 7, minute: Int = 0, message: String = "VANIE Alarm"): Boolean {
        return try {
            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minute)
                putExtra(AlarmClock.EXTRA_MESSAGE, message)
                putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            Toast.makeText(context, "⏰ Alarm set for ${String.format("%02d:%02d", hour, minute)}", Toast.LENGTH_SHORT).show()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun setTimer(seconds: Int, message: String = "VANIE Timer"): Boolean {
        return try {
            val intent = Intent(AlarmClock.ACTION_SET_TIMER).apply {
                putExtra(AlarmClock.EXTRA_LENGTH, seconds)
                putExtra(AlarmClock.EXTRA_MESSAGE, message)
                putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            Toast.makeText(context, "⏱️ Timer set for $seconds seconds", Toast.LENGTH_SHORT).show()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun getDetailedBatteryInfo(): String {
        val iFilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus = context.registerReceiver(null, iFilter)
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct = if (level != -1 && scale != -1) (level * 100 / scale.toFloat()).roundToInt() else 50
        val isCharging = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) == BatteryManager.BATTERY_STATUS_CHARGING
        val tempTenths = batteryStatus?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0
        val tempCelsius = tempTenths / 10f
        val tech = batteryStatus?.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY) ?: "Li-ion"

        val healthStr = when (batteryStatus?.getIntExtra(BatteryManager.EXTRA_HEALTH, BatteryManager.BATTERY_HEALTH_UNKNOWN)) {
            BatteryManager.BATTERY_HEALTH_GOOD -> "Good"
            BatteryManager.BATTERY_HEALTH_OVERHEAT -> "Overheated"
            BatteryManager.BATTERY_HEALTH_DEAD -> "Dead"
            BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> "Over Voltage"
            else -> "Healthy"
        }

        return "Battery Level: ${batteryPct}%\nStatus: ${if (isCharging) "Charging ⚡" else "Discharging"}\nHealth: $healthStr\nTemperature: ${String.format("%.1f", tempCelsius)}°C ($tech)"
    }

    fun getNetworkAndPhoneInfo(): String {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager

        val activeNetwork = cm.activeNetwork
        val caps = cm.getNetworkCapabilities(activeNetwork)

        val connectionType = when {
            caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true -> "Wi-Fi Network"
            caps?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true -> "Cellular Mobile Data"
            else -> "No Active Internet"
        }

        val operatorName = tm.networkOperatorName.ifBlank { "Mobile Operator" }
        val simState = if (tm.simState == TelephonyManager.SIM_STATE_READY) "Active SIM" else "No SIM / Disabled"

        return "Connection: $connectionType\nOperator: $operatorName\nSIM Status: $simState"
    }

    fun getBatteryStatus(): String = getDetailedBatteryInfo()

    fun adjustVolume(increase: Boolean): String {
        return try {
            val direction = if (increase) AudioManager.ADJUST_RAISE else AudioManager.ADJUST_LOWER
            audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, direction, AudioManager.FLAG_SHOW_UI)
            val currentVol = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC)
            val maxVol = audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
            val percent = (currentVol * 100) / maxVol
            "Media volume adjusted to $percent%"
        } catch (e: Exception) {
            "Could not adjust volume"
        }
    }

    fun muteVolume(): String {
        return try {
            audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_MUTE, AudioManager.FLAG_SHOW_UI)
            "Media muted"
        } catch (e: Exception) {
            "Could not mute volume"
        }
    }

    fun openCamera(): Boolean = launchApp("camera")
    fun openGallery(): Boolean = launchApp("photos")
    fun openSettings(): Boolean {
        return try {
            val intent = Intent(Settings.ACTION_SETTINGS).apply { flags = Intent.FLAG_ACTIVITY_NEW_TASK }
            context.startActivity(intent)
            true
        } catch (e: Exception) {
            false
        }
    }
    fun openMaps(): Boolean = launchApp("maps")
    fun openPlayStore(): Boolean = launchApp("store")
    fun openCalculator(): Boolean = launchApp("calculator")
}

object VanieAlarmState {
    var pendingHour: Int = -1
    var pendingMinute: Int = 0
    var pendingLabel: String = "VANIE Alarm"
    var isWaitingForAmPm: Boolean = false
}

object VanieStopwatch {
    private var startTime = 0L
    private var isRunning = false
    private var elapsedTime = 0L

    fun start(): String {
        return if (!isRunning) {
            startTime = System.currentTimeMillis() - elapsedTime
            isRunning = true
            "⏱️ Stopwatch Started! 🚀"
        } else {
            "⏱️ Stopwatch is already running! Elapsed: ${getFormattedTime()}"
        }
    }

    fun pause(): String {
        return if (isRunning) {
            elapsedTime = System.currentTimeMillis() - startTime
            isRunning = false
            "⏸️ Stopwatch Paused at ${getFormattedTime()}"
        } else {
            "⏱️ Stopwatch is currently paused at ${getFormattedTime()}"
        }
    }

    fun reset(): String {
        startTime = 0L
        elapsedTime = 0L
        isRunning = false
        return "🔄 Stopwatch Reset to 00:00!"
    }

    fun getFormattedTime(): String {
        val total = if (isRunning) System.currentTimeMillis() - startTime else elapsedTime
        val seconds = (total / 1000) % 60
        val minutes = (total / (1000 * 60)) % 60
        val hours = total / (1000 * 3600)
        return if (hours > 0) {
            String.format("%02d:%02d:%02d", hours, minutes, seconds)
        } else {
            String.format("%02d:%02d", minutes, seconds)
        }
    }
}

object VanieTaskManager {
    private val taskList = mutableListOf<String>()

    fun addTask(task: String): String {
        val cleanTask = task.trim()
        if (cleanTask.isNotEmpty()) {
            taskList.add(cleanTask)
            return "✅ Task Added: '$cleanTask' (Total Tasks: ${taskList.size})"
        }
        return "⚠️ Kripya task ka details batayein!"
    }

    fun getTasks(): String {
        if (taskList.isEmpty()) {
            return "📋 Aapke paas abhi koi pending task nahi hai!"
        }
        val sb = StringBuilder("📋 **Aapki Task List:**\n")
        taskList.forEachIndexed { i, t ->
            sb.append("${i + 1}. $t\n")
        }
        return sb.toString().trim()
    }

    fun clearTasks(): String {
        val count = taskList.size
        taskList.clear()
        return "🗑️ Sabhi $count tasks clear kar diye gaye hain!"
    }
}

