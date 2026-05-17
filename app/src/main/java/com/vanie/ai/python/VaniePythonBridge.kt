package com.vanie.ai.python

import android.content.Context
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.vanie.ai.nlp.ActionCommand
import com.vanie.ai.nlp.NlpResult

class VaniePythonBridge(private val context: Context) {

    private var vanieEnginePy: PyObject? = null
    private var isInitialized = false

    init {
        initPython()
    }

    private fun initPython() {
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(context))
            }
            val py = Python.getInstance()
            val module = py.getModule("VANIE_ENHANCED")
            vanieEnginePy = module.get("vanie_engine")
            isInitialized = true
        } catch (e: Exception) {
            e.printStackTrace()
            isInitialized = false
        }
    }

    fun processWithPython(input: String): NlpResult {
        if (!isInitialized || vanieEnginePy == null) {
            initPython()
        }

        return try {
            val pyResult = vanieEnginePy?.callMethod("generate_response", input)
            if (pyResult != null) {
                val responseText = pyResult.get("response")?.toString() ?: "I processed your request offline."
                val intentStr = pyResult.get("intent")?.toString() ?: "general"
                val sentimentStr = pyResult.get("sentiment")?.toString() ?: "neutral"
                val intentConf = pyResult.get("intent_confidence")?.toDegreeFloat() ?: 0.9f

                val actionCmd = mapIntentToAction(intentStr, input)
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
        } catch (e: Exception) {
            e.printStackTrace()
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

    private fun mapIntentToAction(intentStr: String, rawInput: String): ActionCommand {
        val lower = rawInput.lowercase()
        return when {
            intentStr == "torch_on" || lower.contains("torch on") || lower.contains("flashlight on") || lower.contains("लाइट चालू") -> ActionCommand.TORCH_ON
            intentStr == "torch_off" || lower.contains("torch off") || lower.contains("flashlight off") || lower.contains("लाइट बंद") -> ActionCommand.TORCH_OFF
            intentStr == "wifi_on" || lower.contains("wifi on") || lower.contains("turn on wifi") -> ActionCommand.WIFI_ON
            intentStr == "wifi_off" || lower.contains("wifi off") || lower.contains("turn off wifi") -> ActionCommand.WIFI_OFF
            intentStr == "bluetooth_on" || lower.contains("bluetooth on") -> ActionCommand.BLUETOOTH_ON
            intentStr == "bluetooth_off" || lower.contains("bluetooth off") -> ActionCommand.BLUETOOTH_OFF
            intentStr == "dnd_on" || lower.contains("dnd on") || lower.contains("do not disturb") -> ActionCommand.DND_ON
            intentStr == "dnd_off" || lower.contains("dnd off") -> ActionCommand.DND_OFF
            intentStr == "mode_silent" || lower.contains("silent mode") -> ActionCommand.MODE_SILENT
            intentStr == "mode_vibrate" || lower.contains("vibrate mode") -> ActionCommand.MODE_VIBRATE
            intentStr == "mode_ring" || lower.contains("ring mode") -> ActionCommand.MODE_RING
            intentStr == "make_call" || lower.contains("call ") || lower.contains("कॉल करो") -> ActionCommand.MAKE_CALL
            intentStr == "send_sms" || lower.contains("text ") || lower.contains("sms") -> ActionCommand.SEND_SMS
            intentStr == "send_whatsapp" || lower.contains("whatsapp") || lower.contains("व्हाट्सएप") -> ActionCommand.SEND_WHATSAPP
            intentStr == "answer_call" || lower.contains("pickup call") || lower.contains("receive call") -> ActionCommand.ANSWER_CALL
            intentStr == "reject_call" || lower.contains("cut call") || lower.contains("hangup") -> ActionCommand.REJECT_CALL
            lower.contains("brightness") || lower.contains("screen light") -> ActionCommand.BRIGHTNESS
            lower.contains("alarm") || lower.contains("timer") || lower.contains("remind") -> ActionCommand.ALARM
            lower.contains("battery") || lower.contains("charge") || lower.contains("power level") -> ActionCommand.BATTERY
            lower.contains("notification") || lower.contains("read messages") || lower.contains("unread") -> ActionCommand.NOTIFICATION_READ
            else -> ActionCommand.NONE
        }
    }

    private fun extractTargetName(input: String): String? {
        val parts = input.split(Regex("(?i)to|for|call|whatsapp|text|send"), 2)
        return if (parts.size > 1) parts[1].trim().split(" ")[0] else null
    }

    private fun extractMessageBody(input: String): String? {
        val parts = input.split(Regex("(?i)saying|message|that|text"), 2)
        return if (parts.size > 1) parts[1].trim() else null
    }

    private fun fallbackResult(input: String): NlpResult {
        return NlpResult(
            intent = "general",
            confidence = 0.5f,
            sentiment = "neutral",
            sentimentConfidence = 0.5f,
            responseText = "Processed offline: $input",
            actionCommand = ActionCommand.NONE
        )
    }
}
