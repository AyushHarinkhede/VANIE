package com.vanie.ai.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import androidx.core.app.NotificationCompat
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.VanieNlpEngine
import com.vanie.ai.receiver.VanieCallReceiver
import com.vanie.ai.telephony.VanieTelephonyController
import java.util.Locale

class VanieVoiceService : Service(), RecognitionListener, TextToSpeech.OnInitListener {

    companion object {
        private const val TAG = "VanieVoiceService"
        private const val CHANNEL_ID = "VANIE_VOICE_SERVICE_CHANNEL"
        private const val NOTIFICATION_ID = 1001
    }

    private var speechRecognizer: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null
    private lateinit var nlpEngine: VanieNlpEngine
    private lateinit var deviceController: VanieDeviceController
    private lateinit var telephonyController: VanieTelephonyController
    private val callReceiver = VanieCallReceiver()

    override fun onCreate() {
        super.onCreate()
        nlpEngine = VanieNlpEngine(this)
        deviceController = VanieDeviceController(this)
        telephonyController = VanieTelephonyController(this)

        tts = TextToSpeech(this, this)
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, buildForegroundNotification())

        startListening()
    }

    private fun startListening() {
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
    }

    override fun onResults(results: Bundle?) {
        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (!matches.isNullOrEmpty()) {
            val spokenText = matches[0]
            Log.d(TAG, "Spoken text: $spokenText")
            handleSpokenCommand(spokenText)
        }
        // Restart listener for continuous offline hotword detection
        startListening()
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
    }

    private fun speakOut(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "VANIE_SPEECH")
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts?.language = Locale.US
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
            manager.createNotificationChannel(channel)
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
        startListening()
    }

    override fun onReadyForSpeech(params: Bundle?) {}
    override fun onBeginningOfSpeech() {}
    override fun onRmsChanged(rmsdB: Float) {}
    override fun onBufferReceived(buffer: ByteArray?) {}
    override fun onEndOfSpeech() {}
    override fun onPartialResults(partialResults: Bundle?) {}
    override fun onEvent(eventType: Int, params: Bundle?) {}

    override fun onDestroy() {
        speechRecognizer?.destroy()
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}
