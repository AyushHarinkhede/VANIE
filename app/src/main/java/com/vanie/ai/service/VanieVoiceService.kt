package com.vanie.ai.service

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.VanieNlpEngine
import com.vanie.ai.receiver.VanieCallReceiver
import com.vanie.ai.telephony.VanieTelephonyController
import com.vanie.ai.util.VanieTtsUtils
import java.util.Locale

class VanieVoiceService : Service(), RecognitionListener, TextToSpeech.OnInitListener {

    companion object {
        private const val TAG = "VanieVoiceService"
        private const val CHANNEL_ID = "VANIE_VOICE_SERVICE_CHANNEL"
        private const val NOTIFICATION_ID = 1001
        private const val PREFS_NAME = "VANIE_SETTINGS"
        private const val KEY_VOICE_ENABLED = "voice_wake_word_enabled"

        fun setVoiceEnabled(context: Context, enabled: Boolean) {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().putBoolean(KEY_VOICE_ENABLED, enabled).apply()
            val intent = Intent(context, VanieVoiceService::class.java)
            if (enabled) {
                val hasAudioPermission = ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.RECORD_AUDIO
                ) == PackageManager.PERMISSION_GRANTED

                if (hasAudioPermission) {
                    try {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            context.startForegroundService(intent)
                        } else {
                            context.startService(intent)
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error starting voice service: ${e.message}", e)
                    }
                }
            } else {
                try {
                    context.stopService(intent)
                } catch (e: Exception) {
                    Log.e(TAG, "Error stopping voice service: ${e.message}", e)
                }
            }
        }

        fun isVoiceEnabled(context: Context): Boolean {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            return prefs.getBoolean(KEY_VOICE_ENABLED, true)
        }
    }

    private var speechRecognizer: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null
    private lateinit var nlpEngine: VanieNlpEngine
    private lateinit var deviceController: VanieDeviceController
    private lateinit var telephonyController: VanieTelephonyController
    private val callReceiver = VanieCallReceiver()

    override fun onCreate() {
        super.onCreate()
        try {
            val hasAudioPermission = ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED

            createNotificationChannel()

            val notification = buildForegroundNotification()
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                if (hasAudioPermission) {
                    ServiceCompat.startForeground(
                        this,
                        NOTIFICATION_ID,
                        notification,
                        ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
                    )
                } else {
                    Log.w(TAG, "RECORD_AUDIO permission missing; cannot start microphone foreground service.")
                    stopSelf()
                    return
                }
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }

            nlpEngine = VanieNlpEngine(this)
            deviceController = VanieDeviceController(this)
            telephonyController = VanieTelephonyController(this)

            try {
                tts = TextToSpeech(this, this)
            } catch (e: Exception) {
                Log.e(TAG, "TTS init error: ${e.message}", e)
            }

            if (hasAudioPermission && isVoiceEnabled(this)) {
                startListening()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Exception in VanieVoiceService.onCreate: ${e.message}", e)
            stopSelf()
        }
    }

    private fun startListening() {
        if (!isVoiceEnabled(this)) return

        val hasAudioPermission = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED

        if (!hasAudioPermission) {
            Log.w(TAG, "Cannot start listening: RECORD_AUDIO permission not granted")
            return
        }

        try {
            if (SpeechRecognizer.isRecognitionAvailable(this)) {
                speechRecognizer?.destroy()
                speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
                speechRecognizer?.setRecognitionListener(this)

                val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                    putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                    putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
                    putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
                    putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
                }

                speechRecognizer?.startListening(intent)
            }
        } catch (e: Exception) {
            Log.e(TAG, "SpeechRecognizer startListening failed: ${e.message}", e)
        }
    }

    override fun onResults(results: Bundle?) {
        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (!matches.isNullOrEmpty()) {
            val spokenText = matches[0]
            Log.d(TAG, "Spoken text: $spokenText")
            handleSpokenCommand(spokenText)
        }
        if (isVoiceEnabled(this)) {
            startListening()
        }
    }

    private fun handleSpokenCommand(input: String) {
        val lower = input.lowercase()
        if (lower.contains("hey vanie") || lower.contains("hello vanie") || lower.contains("vanie")) {
            val cleanCommand = lower.replace("hey vanie", "").replace("hello vanie", "").replace("vanie", "").trim()
            if (cleanCommand.isEmpty()) {
                speakOut("Yes, I am listening!")
                return
            }

            val result = nlpEngine.processMessage(cleanCommand)
            executeAction(result.actionCommand, result.targetName, result.messageBody)
            speakOut(result.responseText)
        }
    }

    private fun executeAction(action: ActionCommand, targetName: String?, messageBody: String?) {
        try {
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
                ActionCommand.SEND_WHATSAPP -> telephonyController.sendWhatsAppMessage(targetName, messageBody)
                ActionCommand.ANSWER_CALL -> callReceiver.answerCall(this)
                ActionCommand.REJECT_CALL -> callReceiver.cutCall(this)
                else -> {}
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error executing action $action: ${e.message}", e)
        }
    }

    private fun speakOut(text: String) {
        VanieTtsUtils.speakExpressive(tts, text, "VANIE_SPEECH")
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            try {
                tts?.language = Locale.US
            } catch (e: Exception) {
                Log.e(TAG, "TTS setLanguage error: ${e.message}", e)
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "VANIE Voice Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private fun buildForegroundNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("VANIE Voice Assistant")
            .setContentText("Listening offline for Hey VANIE...")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onError(error: Int) {
        if (isVoiceEnabled(this)) {
            startListening()
        }
    }

    override fun onReadyForSpeech(params: Bundle?) {}
    override fun onBeginningOfSpeech() {}
    override fun onRmsChanged(rmsdB: Float) {}
    override fun onBufferReceived(buffer: ByteArray?) {}
    override fun onEndOfSpeech() {}
    override fun onPartialResults(partialResults: Bundle?) {}
    override fun onEvent(eventType: Int, params: Bundle?) {}

    override fun onDestroy() {
        try {
            speechRecognizer?.destroy()
        } catch (e: Exception) {
            Log.e(TAG, "Error destroying speechRecognizer: ${e.message}", e)
        }
        try {
            tts?.stop()
            tts?.shutdown()
        } catch (e: Exception) {
            Log.e(TAG, "Error shutting down TTS: ${e.message}", e)
        }
        super.onDestroy()
    }
}
