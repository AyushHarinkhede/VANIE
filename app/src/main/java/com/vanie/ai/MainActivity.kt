package com.vanie.ai

import android.Manifest
import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ContentResolver
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.graphics.Color
import android.media.AudioManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.VibrationEffect
import android.os.Vibrator
import android.provider.MediaStore
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Base64
import android.view.HapticFeedbackConstants
import android.view.View
import android.view.Window
import android.view.WindowManager
import android.webkit.GeolocationPermissions
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.lifecycleScope
import com.google.gson.Gson
import com.google.gson.JsonObject
import com.vanie.ai.control.VanieDeviceController
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.VanieNlpEngine
import com.vanie.ai.python.VaniePythonBridge
import com.vanie.ai.receiver.VanieCallReceiver
import com.vanie.ai.service.VanieVoiceService
import com.vanie.ai.telephony.VanieTelephonyController
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.OutputStream
import java.nio.charset.StandardCharsets
import java.util.Locale

class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {

    private lateinit var webView: WebView
    private var uploadMessage: ValueCallback<Array<Uri>>? = null
    private val FILECHOOSER_RESULTCODE = 1
    private val PERMISSION_REQUEST_CODE = 100
    private var isIncognitoActive = false

    private lateinit var nlpEngine: VanieNlpEngine
    private lateinit var pythonBridge: VaniePythonBridge
    private lateinit var deviceController: VanieDeviceController
    private lateinit var telephonyController: VanieTelephonyController
    private val callReceiver = VanieCallReceiver()

    private var textToSpeech: TextToSpeech? = null
    private var speechRecognizer: SpeechRecognizer? = null
    private var isTtsReady = false

    private fun getRequiredPermissions(): Array<String> {
        val list = mutableListOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.CAMERA,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_PHONE_STATE,
            Manifest.permission.VIBRATE
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            list.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        return list.toTypedArray()
    }

    @SuppressLint("SetJavaScriptEnabled", "AddJavascriptInterface")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Hardware Acceleration for maximum 120Hz-165Hz performance
        window.setFlags(
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
            WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED
        )

        setContentView(R.layout.activity_main)

        // Enable edge-to-edge transparent status bar and navigation bar
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            val win: Window = window
            win.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS or WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION)
            win.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
            val uiOptions = (View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION)
            win.decorView.systemUiVisibility = uiOptions
            win.statusBarColor = Color.TRANSPARENT
            win.navigationBarColor = Color.TRANSPARENT
        }

        enableHighRefreshRate()

        nlpEngine = VanieNlpEngine(this)
        pythonBridge = VaniePythonBridge(this)
        deviceController = VanieDeviceController(this)
        telephonyController = VanieTelephonyController(this)
        textToSpeech = TextToSpeech(this, this)

        requestRequiredPermissions()
        startVoiceService()

        webView = findViewById(R.id.webView)
        webView.isSoundEffectsEnabled = false
        webView.isHapticFeedbackEnabled = false

        // Enable Hardware Accelerated GPU rendering layer
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
        webView.scrollBarStyle = View.SCROLLBARS_INSIDE_OVERLAY
        webView.overScrollMode = View.OVER_SCROLL_NEVER

        // Optimized WebSettings for high FPS JS rendering & data persistence
        val webSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.databaseEnabled = true
        webSettings.allowFileAccess = true
        webSettings.allowContentAccess = true
        webSettings.allowFileAccessFromFileURLs = true
        webSettings.allowUniversalAccessFromFileURLs = true
        try {
            val dbPath = applicationContext.getDir("databases", Context.MODE_PRIVATE).path
            webSettings.databasePath = dbPath
        } catch (ignored: Exception) {}
        webSettings.loadWithOverviewMode = true
        webSettings.useWideViewPort = true
        webSettings.cacheMode = WebSettings.LOAD_DEFAULT

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            webSettings.offscreenPreRaster = true
        }

        // Handle external URLs
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                if (url != null && (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("mailto:") || url.startsWith("tel:"))) {
                    try {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                        startActivity(intent)
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                    return true
                }
                view?.loadUrl(url ?: "")
                return true
            }
        }

        // Handle FileChooser & Permissions
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                uploadMessage?.onReceiveValue(null)
                uploadMessage = filePathCallback

                val intent = fileChooserParams?.createIntent()
                try {
                    if (intent != null) {
                        startActivityForResult(intent, FILECHOOSER_RESULTCODE)
                    }
                } catch (e: ActivityNotFoundException) {
                    uploadMessage = null
                    return false
                }
                return true
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
                if (isIncognitoActive) {
                    runOnUiThread {
                        try {
                            request?.deny()
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                    return
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    super.onPermissionRequest(request)
                }
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String?,
                callback: GeolocationPermissions.Callback?
            ) {
                if (isIncognitoActive) {
                    callback?.invoke(origin, false, false)
                    return
                }
                super.onGeolocationPermissionsShowPrompt(origin, callback)
            }
        }

        // Register custom JavaScript interface for VANIE AI & Mr.NodeMan UI
        webView.addJavascriptInterface(AndroidInterface(), "AndroidApp")

        // Load the local HTML file from assets
        webView.loadUrl("file:///android_asset/index.html")
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = textToSpeech?.setLanguage(Locale.US)
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                textToSpeech?.setLanguage(Locale.getDefault())
            }
            textToSpeech?.setPitch(1.0f)
            textToSpeech?.setSpeechRate(1.0f)
            isTtsReady = true
        }
    }

    private fun enableHighRefreshRate() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                val window = window
                val display = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    display
                } else {
                    @Suppress("DEPRECATION")
                    windowManager.defaultDisplay
                }
                if (display != null) {
                    val supportedModes = display.supportedModes
                    var maxMode = display.mode
                    var maxRate = maxMode.refreshRate
                    for (mode in supportedModes) {
                        if (mode.refreshRate > maxRate) {
                            maxRate = mode.refreshRate
                            maxMode = mode
                        }
                    }
                    val params = window.attributes
                    params.preferredDisplayModeId = maxMode.modeId
                    window.attributes = params
                }
            } catch (ignored: Exception) {}
        }
    }

    private fun requestRequiredPermissions() {
        val permissionsToRequest = getRequiredPermissions().filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissionsToRequest.toTypedArray(), PERMISSION_REQUEST_CODE)
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val audioIndex = permissions.indexOf(Manifest.permission.RECORD_AUDIO)
            if (audioIndex != -1 && grantResults.getOrNull(audioIndex) == PackageManager.PERMISSION_GRANTED) {
                if (VanieVoiceService.isVoiceEnabled(this)) {
                    startVoiceService()
                }
            }
        }
    }

    private fun startVoiceService() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            return
        }
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

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILECHOOSER_RESULTCODE) {
            if (uploadMessage == null) return
            var results: Array<Uri>? = null
            if (resultCode == RESULT_OK && data != null) {
                val dataString = data.dataString
                val clipData = data.clipData
                if (clipData != null) {
                    results = Array(clipData.itemCount) { i -> clipData.getItemAt(i).uri }
                }
                if (dataString != null) {
                    results = arrayOf(Uri.parse(dataString))
                }
            }
            uploadMessage?.onReceiveValue(results)
            uploadMessage = null
        } else {
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    override fun onBackPressed() {
        if (::webView.isInitialized) {
            webView.evaluateJavascript("if(window.handleSystemBack) { window.handleSystemBack(); } else { history.back(); }", null)
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        if (textToSpeech != null) {
            textToSpeech?.stop()
            textToSpeech?.shutdown()
        }
        if (speechRecognizer != null) {
            speechRecognizer?.destroy()
        }
        super.onDestroy()
    }

    // Native Interface exposing operations to JavaScript
    inner class AndroidInterface {

        // â”€â”€ Ultra-crisp Native Haptic Feedback â”€â”€
        @JavascriptInterface
        fun performHaptic(type: String?) {
            runOnUiThread {
                try {
                    val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
                    if (vibrator == null || !vibrator.hasVibrator()) return@runOnUiThread

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        var effectId = -1
                        when (type?.lowercase()) {
                            "light", "tap", "selection" -> effectId = VibrationEffect.EFFECT_CLICK
                            "medium", "impact", "navigation" -> effectId = VibrationEffect.EFFECT_DOUBLE_CLICK
                            "heavy", "modal", "button" -> effectId = VibrationEffect.EFFECT_HEAVY_CLICK
                            "tick", "clock", "countdown" -> effectId = VibrationEffect.EFFECT_TICK
                        }

                        if (effectId != -1) {
                            try {
                                vibrator.vibrate(VibrationEffect.createPredefined(effectId))
                                return@runOnUiThread
                            } catch (ignored: Exception) {}
                        }
                    }

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        when (type?.lowercase()) {
                            "success" -> vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 15, 35, 20), intArrayOf(0, 200, 0, 255), -1))
                            "error", "delete", "danger" -> vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 25, 35, 25, 35, 40), intArrayOf(0, 220, 0, 220, 0, 255), -1))
                            "heavy", "modal", "button" -> vibrator.vibrate(VibrationEffect.createOneShot(26, VibrationEffect.DEFAULT_AMPLITUDE))
                            "medium", "impact", "navigation" -> vibrator.vibrate(VibrationEffect.createOneShot(16, 200))
                            "tick", "clock" -> vibrator.vibrate(VibrationEffect.createOneShot(8, 140))
                            else -> vibrator.vibrate(VibrationEffect.createOneShot(12, 180))
                        }
                    } else {
                        @Suppress("DEPRECATION")
                        when (type?.lowercase()) {
                            "success" -> vibrator.vibrate(longArrayOf(0, 15, 35, 20), -1)
                            "error", "delete" -> vibrator.vibrate(longArrayOf(0, 25, 35, 25, 35, 40), -1)
                            "heavy", "modal" -> vibrator.vibrate(25)
                            "medium", "navigation" -> vibrator.vibrate(16)
                            "tick" -> vibrator.vibrate(8)
                            else -> vibrator.vibrate(12)
                        }
                    }
                } catch (e: Exception) {
                    try {
                        webView.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP, HapticFeedbackConstants.FLAG_IGNORE_GLOBAL_SETTING)
                    } catch (ignored: Exception) {}
                }
            }
        }

        // ── VANIE Neural AI Processing Bridge ──
        @JavascriptInterface
        fun processAI(query: String) {
            lifecycleScope.launch(Dispatchers.IO) {
                try {
                    val pyResult = pythonBridge.processWithPython(query)
                    val responseText = pyResult.responseText

                    // Execute corresponding hardware or telephony actions
                    withContext(Dispatchers.Main) {
                        try {
                            executeAction(pyResult.actionCommand, pyResult.targetName, pyResult.messageBody)
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                        
                        // Speak out loud via TTS
                        if (isTtsReady) {
                            try {
                                textToSpeech?.speak(responseText, TextToSpeech.QUEUE_FLUSH, null, "VanieResponse")
                            } catch (e: Exception) {
                                e.printStackTrace()
                            }
                        }

                        // Dispatch JSON back to WebView
                        val json = JsonObject()
                        json.addProperty("responseText", responseText)
                        json.addProperty("intent", pyResult.intent)
                        json.addProperty("confidence", pyResult.confidence)
                        json.addProperty("actionCommand", pyResult.actionCommand.name)

                        val gson = Gson()
                        val jsonString = gson.toJson(json)
                        webView.evaluateJavascript("window.onVanieAIResponse($jsonString);", null)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    withContext(Dispatchers.Main) {
                        val fallback = "I processed your command offline with zero latency."
                        val json = JsonObject()
                        json.addProperty("responseText", fallback)
                        val gson = Gson()
                        val jsonString = gson.toJson(json)
                        webView.evaluateJavascript("window.onVanieAIResponse($jsonString);", null)
                    }
                }
            }
        }

        @JavascriptInterface
        fun speakText(text: String?) {
            if (!text.isNullOrBlank() && isTtsReady) {
                runOnUiThread {
                    try {
                        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "VanieManualSpeak")
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
        }

        @JavascriptInterface
        fun stopSpeaking() {
            runOnUiThread {
                try {
                    textToSpeech?.stop()
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }

        @JavascriptInterface
        fun startVoiceListening() {
            runOnUiThread {
                if (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this@MainActivity, "Microphone permission required for voice input", Toast.LENGTH_SHORT).show()
                    requestRequiredPermissions()
                    return@runOnUiThread
                }
                try {
                    if (SpeechRecognizer.isRecognitionAvailable(this@MainActivity)) {
                        speechRecognizer?.destroy()
                        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this@MainActivity)
                        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
                            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
                        }
                        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                            override fun onReadyForSpeech(params: Bundle?) {}
                            override fun onBeginningOfSpeech() {}
                            override fun onRmsChanged(rmsdB: Float) {}
                            override fun onBufferReceived(buffer: ByteArray?) {}
                            override fun onEndOfSpeech() {}
                            override fun onError(error: Int) {
                                runOnUiThread {
                                    Toast.makeText(this@MainActivity, "Voice timeout, please try again", Toast.LENGTH_SHORT).show()
                                }
                            }
                            override fun onResults(results: Bundle?) {
                                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                                if (!matches.isNullOrEmpty()) {
                                    val recognized = matches[0]
                                    runOnUiThread {
                                        val jsonEscaped = Gson().toJson(recognized)
                                        webView.evaluateJavascript("window.handleVoiceResult($jsonEscaped);", null)
                                    }
                                }
                            }
                            override fun onPartialResults(partialResults: Bundle?) {}
                            override fun onEvent(eventType: Int, params: Bundle?) {}
                        })
                        speechRecognizer?.startListening(intent)
                    } else {
                        Toast.makeText(this@MainActivity, "Speech recognition not available on this device", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                    Toast.makeText(this@MainActivity, "Speech recognition error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }

        // â”€â”€ Hardware Controls â”€â”€
        @JavascriptInterface
        fun toggleTorch(enable: Boolean): Boolean {
            return deviceController.setTorchMode(enable)
        }

        @JavascriptInterface
        fun setBrightness(percent: Int): Boolean {
            return deviceController.setScreenBrightness(percent)
        }

        @JavascriptInterface
        fun getBatteryLevel(): String {
            return deviceController.getDetailedBatteryInfo()
        }

        @JavascriptInterface
        fun setAudioMode(mode: String): Boolean {
            return when (mode.lowercase()) {
                "silent" -> deviceController.setRingerMode(AudioManager.RINGER_MODE_SILENT)
                "vibrate" -> deviceController.setRingerMode(AudioManager.RINGER_MODE_VIBRATE)
                "dnd" -> deviceController.setDoNotDisturb(true)
                else -> {
                    deviceController.setDoNotDisturb(false)
                    deviceController.setRingerMode(AudioManager.RINGER_MODE_NORMAL)
                }
            }
        }

        @JavascriptInterface
        fun openWifiSettings() {
            deviceController.openWifiSettings()
        }

        @JavascriptInterface
        fun openBluetoothSettings() {
            deviceController.openBluetoothSettings()
        }

        @JavascriptInterface
        fun launchApp(appName: String): Boolean {
            return deviceController.launchApp(appName)
        }

        @JavascriptInterface
        fun setAlarm(hour: Int, min: Int, label: String?): Boolean {
            return deviceController.setAlarm(hour, min, label ?: "VANIE Alarm")
        }

        @JavascriptInterface
        fun setTimer(seconds: Int, label: String?): Boolean {
            return deviceController.setTimer(seconds, label ?: "VANIE Timer")
        }

        @JavascriptInterface
        fun makePhoneCall(contactOrNumber: String?): String {
            return telephonyController.makeCall(contactOrNumber)
        }

        @JavascriptInterface
        fun sendSms(number: String, message: String): String {
            telephonyController.sendSms(number, message)
            return "SMS queued for $number"
        }

        @JavascriptInterface
        fun sendWhatsAppMessage(contact: String, message: String): String {
            return telephonyController.prepareWhatsAppDraft(contact, message)
        }

        // â”€â”€ Native Persistent Flash Disk Key-Value Storage â”€â”€
        @JavascriptInterface
        fun saveData(key: String?, value: String?): Boolean {
            if (key == null) return false
            return try {
                val prefs: SharedPreferences = getSharedPreferences("vanie_native_store", Context.MODE_PRIVATE)
                val committed = prefs.edit().putString(key, value).commit()
                try {
                    val storeDir = File(filesDir, "vanie_data")
                    if (!storeDir.exists()) storeDir.mkdirs()
                    val file = File(storeDir, "store_" + Math.abs(key.hashCode()) + ".dat")
                    FileOutputStream(file).use { fos ->
                        if (value != null) {
                            fos.write(value.toByteArray(StandardCharsets.UTF_8))
                        } else {
                            file.delete()
                        }
                    }
                } catch (ignored: Exception) {}
                committed
            } catch (e: Exception) {
                false
            }
        }

        @JavascriptInterface
        fun loadData(key: String?): String? {
            if (key == null) return null
            return try {
                val prefs: SharedPreferences = getSharedPreferences("vanie_native_store", Context.MODE_PRIVATE)
                val value = prefs.getString(key, null)
                if (value != null) return value

                val storeDir = File(filesDir, "vanie_data")
                val file = File(storeDir, "store_" + Math.abs(key.hashCode()) + ".dat")
                if (file.exists()) {
                    FileInputStream(file).use { fis ->
                        val bytes = ByteArray(file.length().toInt())
                        fis.read(bytes)
                        return String(bytes, StandardCharsets.UTF_8)
                    }
                }
                null
            } catch (e: Exception) {
                null
            }
        }

        // â”€â”€ Direct File Exporter â”€â”€
        @JavascriptInterface
        fun exportFile(filename: String, base64Data: String, mimeType: String) {
            runOnUiThread {
                try {
                    val bytes = Base64.decode(base64Data, Base64.DEFAULT)
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        val values = ContentValues().apply {
                            put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
                            put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
                            put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                        }
                        val resolver: ContentResolver = contentResolver
                        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                        if (uri != null) {
                            resolver.openOutputStream(uri)?.use { os ->
                                os.write(bytes)
                                Toast.makeText(this@MainActivity, "File saved to Downloads: $filename", Toast.LENGTH_LONG).show()
                                return@runOnUiThread
                            }
                        }
                    } else {
                        val dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                        if (!dir.exists()) dir.mkdirs()
                        val file = File(dir, filename)
                        FileOutputStream(file).use { fos ->
                            fos.write(bytes)
                            Toast.makeText(this@MainActivity, "File saved to Downloads: $filename", Toast.LENGTH_LONG).show()
                            return@runOnUiThread
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }

                // Fallback share intent
                triggerShareIntent(filename, base64Data, mimeType)
            }
        }

        @JavascriptInterface
        fun openExternalUrl(url: String) {
            runOnUiThread {
                try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                    startActivity(intent)
                } catch (e: Exception) {
                    e.printStackTrace()
                    Toast.makeText(this@MainActivity, "Could not open link: $url", Toast.LENGTH_SHORT).show()
                }
            }
        }

        @JavascriptInterface
        fun setScreenCaptureProtection(enable: Boolean) {
            runOnUiThread {
                try {
                    isIncognitoActive = enable
                    if (enable) {
                        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
                    } else {
                        window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }

        @JavascriptInterface
        fun isScreenCaptureProtected(): Boolean {
            return try {
                (window.attributes.flags and WindowManager.LayoutParams.FLAG_SECURE) != 0
            } catch (e: Exception) {
                false
            }
        }

        @JavascriptInterface
        fun exitApp() {
            runOnUiThread {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    finishAndRemoveTask()
                } else {
                    finish()
                }
            }
        }
    }

    private fun triggerShareIntent(filename: String, base64Data: String, mimeType: String) {
        try {
            val bytes = Base64.decode(base64Data, Base64.DEFAULT)
            val tempDir = File(cacheDir, "shared_exports")
            if (!tempDir.exists()) tempDir.mkdirs()
            val tempFile = File(tempDir, filename)
            FileOutputStream(tempFile).use { it.write(bytes) }

            val contentUri = FileProvider.getUriForFile(this, "$packageName.provider", tempFile)
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = mimeType
                putExtra(Intent.EXTRA_STREAM, contentUri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(shareIntent, "Save or share $filename"))
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Export ready: $filename", Toast.LENGTH_SHORT).show()
        }
    }

    private fun executeAction(
        action: ActionCommand,
        targetName: String?,
        messageBody: String?
    ) {
        try {
            when (action) {
                ActionCommand.TORCH_ON -> deviceController.setTorchMode(true)
                ActionCommand.TORCH_OFF -> deviceController.setTorchMode(false)
                ActionCommand.WIFI_ON, ActionCommand.WIFI_OFF -> deviceController.openWifiSettings()
                ActionCommand.BLUETOOTH_ON -> deviceController.setBluetoothMode(true)
                ActionCommand.BLUETOOTH_OFF -> deviceController.setBluetoothMode(false)
                ActionCommand.DND_ON -> deviceController.setDoNotDisturb(true)
                ActionCommand.DND_OFF -> deviceController.setDoNotDisturb(false)
                ActionCommand.MODE_SILENT -> deviceController.setRingerMode(AudioManager.RINGER_MODE_SILENT)
                ActionCommand.MODE_VIBRATE -> deviceController.setRingerMode(AudioManager.RINGER_MODE_VIBRATE)
                ActionCommand.MODE_RING -> deviceController.setRingerMode(AudioManager.RINGER_MODE_NORMAL)
                ActionCommand.LAUNCH_APP -> if (targetName != null) deviceController.launchApp(targetName)
                ActionCommand.SET_ALARM -> deviceController.setAlarm(7, 0, "VANIE Alarm")
                ActionCommand.SET_TIMER -> deviceController.setTimer(300, "VANIE Timer")
                ActionCommand.GET_DETAILED_BATTERY -> {
                    val info = deviceController.getDetailedBatteryInfo()
                    Toast.makeText(this, info, Toast.LENGTH_LONG).show()
                }
                ActionCommand.GET_NETWORK_INFO -> {
                    val info = deviceController.getNetworkAndPhoneInfo()
                    Toast.makeText(this, info, Toast.LENGTH_LONG).show()
                }
                ActionCommand.MAKE_CALL -> if (targetName != null) telephonyController.makeCall(targetName)
                ActionCommand.SEND_SMS -> if (targetName != null) telephonyController.sendSms(targetName, messageBody)
                ActionCommand.SEND_WHATSAPP -> if (targetName != null) telephonyController.sendWhatsAppMessage(targetName, messageBody)
                ActionCommand.SEND_WHATSAPP_CALL -> if (targetName != null) telephonyController.makeWhatsAppCall(targetName)
                ActionCommand.CONFIRM_SEND_DRAFT -> telephonyController.confirmAndSendPendingDraft()
                ActionCommand.LOCATION_INFO -> deviceController.openLocationSettings()
                ActionCommand.VOLUME_UP -> deviceController.adjustVolume(true)
                ActionCommand.VOLUME_DOWN -> deviceController.adjustVolume(false)
                ActionCommand.VOLUME_MUTE -> deviceController.muteVolume()
                ActionCommand.OPEN_CAMERA -> deviceController.openCamera()
                ActionCommand.OPEN_GALLERY -> deviceController.openGallery()
                ActionCommand.OPEN_SETTINGS -> deviceController.openSettings()
                ActionCommand.OPEN_MAPS -> deviceController.openMaps()
                ActionCommand.OPEN_PLAYSTORE -> deviceController.openPlayStore()
                ActionCommand.OPEN_CALCULATOR -> deviceController.openCalculator()
                else -> {}
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}