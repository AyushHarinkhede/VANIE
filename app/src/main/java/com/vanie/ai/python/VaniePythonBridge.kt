package com.vanie.ai.python

import android.content.Context
import android.util.Log
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.NlpResult
import com.vanie.ai.nlp.VanieNlpEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class VaniePythonBridge(private val context: Context) {

    private var vanieEnginePy: PyObject? = null
    private val nlpFallbackEngine = VanieNlpEngine(context)
    @Volatile
    private var isInitialized = false

    private suspend fun initPython() = withContext(Dispatchers.IO) {
        if (!isInitialized) {
            try {
                if (!Python.isStarted()) {
                    Python.start(AndroidPlatform(context.applicationContext))
                }
                val py = Python.getInstance()
                val module = py.getModule("VANIE_ENHANCED")
                vanieEnginePy = module.get("vanie_engine")
                isInitialized = true
                Log.d("VaniePythonBridge", "Python engine and VANIE_ENHANCED module initialized successfully.")
            } catch (e: Throwable) {
                Log.e("VaniePythonBridge", "Python Bridge init failed: ${e.message}", e)
                isInitialized = false
            }
        }
    }

    suspend fun processWithPython(input: String): NlpResult = withContext(Dispatchers.IO) {
        if (!isInitialized || vanieEnginePy == null) {
            initPython()
        }

        try {
            val pyResult = vanieEnginePy?.callAttr("generate_response", input)
            if (pyResult != null) {
                val responseText = pyResult.callAttr("get", "response")?.toString() ?: "I processed your request offline."
                val intentStr = pyResult.callAttr("get", "intent")?.toString() ?: "general"
                val actionTag = pyResult.callAttr("get", "action")?.toString() ?: ""
                val sentimentStr = pyResult.callAttr("get", "sentiment")?.toString() ?: "neutral"
                val intentConf = pyResult.callAttr("get", "intent_confidence")?.toDegreeFloat() ?: 0.9f

                val actionCmd = mapActionTagToEnum(actionTag, intentStr, input)
                val targetName = extractTargetName(input)
                val messageBody = extractMessageBody(input)

                NlpResult(
                    intent = intentStr,
                    confidence = intentConf,
                    sentiment = sentimentStr,
                    sentimentConfidence = 0.9f,
                    responseText = responseText,
                    actionCommand = actionCmd,
                    targetName = targetName,
                    messageBody = messageBody
                )
            } else {
                fallbackResult(input)
            }
        } catch (e: Throwable) {
            Log.e("VaniePythonBridge", "Error executing python processWithPython: ${e.message}", e)
            fallbackResult(input)
        }
    }

    private fun PyObject.toDegreeFloat(): Float {
        return try {
            this.toFloat()
        } catch (e: Exception) {
            0.9f
        }
    }

    private fun mapActionTagToEnum(actionTag: String, intentStr: String, rawInput: String): ActionCommand {
        val lower = rawInput.lowercase()

        when (actionTag) {
            "GET_NETWORK_INFO" -> return ActionCommand.GET_NETWORK_INFO
            "GET_DETAILED_BATTERY" -> return ActionCommand.GET_DETAILED_BATTERY
            "SEND_WHATSAPP_CALL" -> return ActionCommand.SEND_WHATSAPP_CALL
            "CONFIRM_SEND_DRAFT" -> return ActionCommand.CONFIRM_SEND_DRAFT
            "LOCATION_INFO" -> return ActionCommand.LOCATION_INFO
            "TORCH_ON" -> return ActionCommand.TORCH_ON
            "TORCH_OFF" -> return ActionCommand.TORCH_OFF
            "WIFI_ON" -> return ActionCommand.WIFI_ON
            "WIFI_OFF" -> return ActionCommand.WIFI_OFF
            "BLUETOOTH_ON" -> return ActionCommand.BLUETOOTH_ON
            "BLUETOOTH_OFF" -> return ActionCommand.BLUETOOTH_OFF
            "DND_ON" -> return ActionCommand.DND_ON
            "DND_OFF" -> return ActionCommand.DND_OFF
            "MODE_SILENT" -> return ActionCommand.MODE_SILENT
            "MODE_VIBRATE" -> return ActionCommand.MODE_VIBRATE
            "MODE_RING" -> return ActionCommand.MODE_RING
            "MAKE_CALL", "CALL_CONTACT" -> return ActionCommand.MAKE_CALL
            "SEND_SMS" -> return ActionCommand.SEND_SMS
            "SEND_WHATSAPP" -> return ActionCommand.SEND_WHATSAPP
            "ANSWER_CALL" -> return ActionCommand.ANSWER_CALL
            "REJECT_CALL" -> return ActionCommand.REJECT_CALL
            "BRIGHTNESS", "SET_BRIGHTNESS" -> return ActionCommand.BRIGHTNESS
            "ALARM", "SET_ALARM" -> return ActionCommand.SET_ALARM
            "TIMER", "SET_TIMER" -> return ActionCommand.SET_TIMER
            "BATTERY" -> return ActionCommand.BATTERY
            "NOTIFICATION_READ" -> return ActionCommand.NOTIFICATION_READ
            "LAUNCH_APP" -> return ActionCommand.LAUNCH_APP
        }

        return when {
            lower == "send it" || lower == "bhej do" || lower == "confirm send" || lower == "yes send" || lower == "ha bhej do" -> ActionCommand.CONFIRM_SEND_DRAFT
            lower.contains("torch on") || lower.contains("flashlight on") || lower.contains("flash on") || lower.contains("turn on flashlight") || lower.contains("लाइट चालू") || lower.contains("टॉर्च चालू") || intentStr == "torch_on" -> ActionCommand.TORCH_ON
            lower.contains("torch off") || lower.contains("flashlight off") || lower.contains("flash off") || lower.contains("turn off flashlight") || lower.contains("लाइट बंद") || lower.contains("टॉर्च बंद") || intentStr == "torch_off" -> ActionCommand.TORCH_OFF
            lower.contains("wifi on") || lower.contains("turn on wifi") || lower.contains("enable wifi") || lower.contains("वाईफाई चालू") -> ActionCommand.WIFI_ON
            lower.contains("wifi off") || lower.contains("turn off wifi") || lower.contains("disable wifi") || lower.contains("वाईफाई बंद") -> ActionCommand.WIFI_OFF
            lower.contains("bluetooth on") || lower.contains("turn on bluetooth") || lower.contains("ब्लूटूथ चालू") -> ActionCommand.BLUETOOTH_ON
            lower.contains("bluetooth off") || lower.contains("turn off bluetooth") || lower.contains("ब्लूटूथ बंद") -> ActionCommand.BLUETOOTH_OFF
            lower.contains("dnd on") || lower.contains("do not disturb on") || lower.contains("डीएनडी चालू") -> ActionCommand.DND_ON
            lower.contains("dnd off") || lower.contains("do not disturb off") || lower.contains("डीएनडी बंद") -> ActionCommand.DND_OFF
            lower.contains("silent mode") || lower.contains("phone silent") || lower.contains("साइलेंट करो") -> ActionCommand.MODE_SILENT
            lower.contains("vibrate mode") || lower.contains("phone vibrate") || lower.contains("वाइब्रेट करो") -> ActionCommand.MODE_VIBRATE
            lower.contains("ring mode") || lower.contains("normal mode") || lower.contains("रिंगर ऑन") -> ActionCommand.MODE_RING
            lower.contains("network type") || lower.contains("sim info") || lower.contains("operator") -> ActionCommand.GET_NETWORK_INFO
            lower.contains("battery percentage") || lower.contains("kitni charge") || lower.contains("power status") -> ActionCommand.GET_DETAILED_BATTERY
            lower.contains("whatsapp call") || lower.contains("call on whatsapp") || lower.contains("whatsapp se call") -> ActionCommand.SEND_WHATSAPP_CALL
            lower.contains("open youtube") || lower.contains("open whatsapp") || lower.contains("open chrome") || lower.contains("open camera") || lower.startsWith("open ") || lower.contains("खोलो") -> ActionCommand.LAUNCH_APP
            lower.contains("call ") || lower.contains("dial ") || lower.contains("कॉल करो") || lower.contains("फोन करो") || intentStr == "make_call" -> ActionCommand.MAKE_CALL
            lower.contains("text ") || lower.contains("sms ") || lower.contains("send text") || lower.contains("मैसेज करो") || intentStr == "send_sms" -> ActionCommand.SEND_SMS
            lower.contains("whatsapp ") || lower.contains("send whatsapp") || lower.contains("व्हाट्सएप करो") || intentStr == "send_whatsapp" -> ActionCommand.SEND_WHATSAPP
            lower.contains("pickup call") || lower.contains("answer call") || lower.contains("कॉल उठाओ") || intentStr == "answer_call" -> ActionCommand.ANSWER_CALL
            lower.contains("cut call") || lower.contains("hangup") || lower.contains("reject call") || lower.contains("कॉल काटो") || intentStr == "reject_call" -> ActionCommand.REJECT_CALL
            lower.contains("brightness") || lower.contains("screen light") || lower.contains("ब्राइटनेस") -> ActionCommand.BRIGHTNESS
            lower.contains("alarm") || lower.contains("timer") || lower.contains("अलार्म") -> ActionCommand.ALARM
            lower.contains("battery") || lower.contains("charge") || lower.contains("बैटरी") -> ActionCommand.BATTERY
            lower.contains("notification") || lower.contains("read messages") || lower.contains("unread") -> ActionCommand.NOTIFICATION_READ
            else -> ActionCommand.NONE
        }
    }

    private fun extractTargetName(input: String): String? {
        val lower = input.lowercase()
        if (lower.startsWith("open ")) {
            return lower.replace("open ", "").trim()
        }
        val parts = input.split(Regex("(?i)\\b(to|for|call|dial|whatsapp call|whatsapp|text|send|open|on whatsapp|in whatsapp)\\b"), 2)
        if (parts.size > 1) {
            val candidate = parts[1].split(Regex("(?i)\\b(saying|message|that|text|ko)\\b"), 2)[0].trim()
            if (candidate.isNotBlank()) return candidate
        }
        return null
    }

    private fun extractMessageBody(input: String): String? {
        val parts = input.split(Regex("(?i)\\b(saying|message|that|text)\\b"), 2)
        return if (parts.size > 1 && parts[1].isNotBlank()) parts[1].trim() else null
    }

    private fun fallbackResult(input: String): NlpResult {
        return nlpFallbackEngine.processMessage(input)
    }
}
