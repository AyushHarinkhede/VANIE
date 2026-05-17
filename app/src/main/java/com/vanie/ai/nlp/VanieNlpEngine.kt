package com.vanie.ai.nlp

import android.content.Context
import com.google.gson.Gson
import com.google.gson.JsonObject
import java.io.InputStreamReader
import java.util.regex.Pattern
import kotlin.math.min
import kotlin.random.Random

data class NlpResult(
    val intent: String,
    val confidence: Float,
    val sentiment: String,
    val sentimentConfidence: Float,
    val responseText: String,
    val actionCommand: ActionCommand = ActionCommand.NONE,
    val targetName: String? = null,
    val messageBody: String? = null
)

enum class ActionCommand {
    NONE,
    TORCH_ON,
    TORCH_OFF,
    WIFI_ON,
    WIFI_OFF,
    BLUETOOTH_ON,
    BLUETOOTH_OFF,
    DND_ON,
    DND_OFF,
    MODE_SILENT,
    MODE_VIBRATE,
    MODE_RING,
    MAKE_CALL,
    SEND_SMS,
    SEND_WHATSAPP,
    ANSWER_CALL,
    REJECT_CALL,
    BRIGHTNESS,
    ALARM,
    BATTERY,
    NOTIFICATION_READ,
    LAUNCH_APP
}

class VanieNlpEngine(private val context: Context) {

    private val intentPatterns = mutableMapOf<String, Pattern>()
    private val positiveWords = mutableMapOf<String, Int>()
    private val negativeWords = mutableMapOf<String, Int>()
    private val jokes = mutableListOf<String>()
    private val riddles = mutableListOf<Pair<String, String>>()
    private val quotes = mutableListOf<String>()
    private val facts = mutableListOf<String>()

    init {
        loadDataset()
    }

    private fun loadDataset() {
        try {
            val inputStream = context.assets.open("vanie_dataset.json")
            val reader = InputStreamReader(inputStream, "UTF-8")
            val jsonObject = Gson().fromJson(reader, JsonObject::class.java)

            // Load intents
            if (jsonObject.has("intents")) {
                val intentsObj = jsonObject.getAsJsonObject("intents")
                intentsObj.entrySet().forEach { (intentKey, patternElement) ->
                    intentPatterns[intentKey] = Pattern.compile(
                        patternElement.asString,
                        Pattern.CASE_INSENSITIVE or Pattern.UNICODE_CASE
                    )
                }
            }

            // Load jokes
            if (jsonObject.has("jokes")) {
                jsonObject.getAsJsonArray("jokes").forEach { item ->
                    val obj = item.asJsonObject
                    if (obj.has("joke")) jokes.add(obj.get("joke").asString)
                }
            }

            // Load riddles
            if (jsonObject.has("riddles")) {
                jsonObject.getAsJsonArray("riddles").forEach { item ->
                    val obj = item.asJsonObject
                    if (obj.has("riddle") && obj.has("answer")) {
                        riddles.add(Pair(obj.get("riddle").asString, obj.get("answer").asString))
                    }
                }
            }

            // Load quotes
            if (jsonObject.has("quotes")) {
                jsonObject.getAsJsonArray("quotes").forEach { quotes.add(it.asString) }
            }

            // Load facts
            if (jsonObject.has("facts")) {
                jsonObject.getAsJsonArray("facts").forEach { facts.add(it.asString) }
            }

            // Load sentiment
            if (jsonObject.has("sentiment")) {
                val sentObj = jsonObject.getAsJsonObject("sentiment")
                if (sentObj.has("positive")) {
                    sentObj.getAsJsonObject("positive").entrySet().forEach { (word, score) ->
                        positiveWords[word.lowercase()] = score.asInt
                    }
                }
                if (sentObj.has("negative")) {
                    sentObj.getAsJsonObject("negative").entrySet().forEach { (word, score) ->
                        negativeWords[word.lowercase()] = score.asInt
                    }
                }
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun processMessage(input: String): NlpResult {
        val cleanInput = input.trim()
        if (cleanInput.isEmpty()) {
            return NlpResult(
                intent = "general",
                confidence = 0f,
                sentiment = "neutral",
                sentimentConfidence = 0.5f,
                responseText = "कृपया कोई संदेश दें।"
            )
        }

        val (sentiment, sentimentConf) = calculateSentiment(cleanInput)
        var bestIntent = "general"
        var bestScore = 0.0f

        for ((intentKey, pattern) in intentPatterns) {
            val matcher = pattern.matcher(cleanInput)
            if (matcher.find()) {
                val score = min(1.0f, 0.7f + 0.3f * matcher.groupCount())
                if (score > bestScore) {
                    bestScore = score
                    bestIntent = intentKey
                }
            }
        }

        var actionCommand = ActionCommand.NONE
        var targetName: String? = null
        var messageBody: String? = null
        var responseText = ""

        when (bestIntent) {
            "torch_on" -> {
                actionCommand = ActionCommand.TORCH_ON
                responseText = "🔦 Flashlight turned ON!"
            }
            "torch_off" -> {
                actionCommand = ActionCommand.TORCH_OFF
                responseText = "🔦 Flashlight turned OFF!"
            }
            "wifi_on" -> {
                actionCommand = ActionCommand.WIFI_ON
                responseText = "📶 Opening Wi-Fi settings..."
            }
            "wifi_off" -> {
                actionCommand = ActionCommand.WIFI_OFF
                responseText = "📶 Opening Wi-Fi settings to disable..."
            }
            "bluetooth_on" -> {
                actionCommand = ActionCommand.BLUETOOTH_ON
                responseText = "🔵 Opening Bluetooth controls..."
            }
            "bluetooth_off" -> {
                actionCommand = ActionCommand.BLUETOOTH_OFF
                responseText = "🔵 Opening Bluetooth settings to turn OFF..."
            }
            "dnd_on" -> {
                actionCommand = ActionCommand.DND_ON
                responseText = "🌙 Do Not Disturb (DND) activated."
            }
            "dnd_off" -> {
                actionCommand = ActionCommand.DND_OFF
                responseText = "🔔 Do Not Disturb (DND) disabled."
            }
            "mode_silent" -> {
                actionCommand = ActionCommand.MODE_SILENT
                responseText = "🔕 Phone set to Silent Mode."
            }
            "mode_vibrate" -> {
                actionCommand = ActionCommand.MODE_VIBRATE
                responseText = "📳 Phone set to Vibrate Mode."
            }
            "mode_ring" -> {
                actionCommand = ActionCommand.MODE_RING
                responseText = "🔔 Phone set to Normal Ringing Mode."
            }
            "make_call" -> {
                actionCommand = ActionCommand.MAKE_CALL
                targetName = extractContactName(cleanInput, listOf("call", "dial", "कॉल करो", "फोन करो", "कॉल लगाओ"))
                responseText = if (targetName != null) "📞 Calling $targetName..." else "📞 Preparing to call..."
            }
            "send_sms" -> {
                actionCommand = ActionCommand.SEND_SMS
                val extracted = extractContactAndMessage(cleanInput)
                targetName = extracted.first
                messageBody = extracted.second
                responseText = "💬 Preparing SMS for ${targetName ?: "contact"}..."
            }
            "send_whatsapp" -> {
                actionCommand = ActionCommand.SEND_WHATSAPP
                val extracted = extractContactAndMessage(cleanInput)
                targetName = extracted.first
                messageBody = extracted.second
                responseText = "💚 Launching WhatsApp for ${targetName ?: "contact"}..."
            }
            "answer_call" -> {
                actionCommand = ActionCommand.ANSWER_CALL
                responseText = "📞 Answering incoming call!"
            }
            "reject_call" -> {
                actionCommand = ActionCommand.REJECT_CALL
                responseText = "📵 Rejecting incoming call."
            }
            "joke" -> {
                responseText = if (jokes.isNotEmpty()) "😄 ${jokes.random()}" else "😄 Why did the code crash? Because it lost its main class!"
            }
            "riddle" -> {
                if (riddles.isNotEmpty()) {
                    val r = riddles.random()
                    responseText = "🤔 ${r.first}\n\n(Answer: ${r.second})"
                } else {
                    responseText = "🤔 What has keys but no locks? (Answer: keyboard)"
                }
            }
            "motivation" -> {
                responseText = if (quotes.isNotEmpty()) "💪 ${quotes.random()}" else "🚀 Hard work beats talent when talent doesn't work hard!"
            }
            "greeting" -> {
                responseText = "नमस्ते! मैं हूँ VANIE 🤖 (Virtual Agent of Neural Integrated Engine). मैं आपकी कैसे मदद करूँ?"
            }
            "vanie" -> {
                responseText = "🤖 VANIE: Virtual Agent of Neural Integrated Engine!\nDesigned by Ayush Harinkhede.\nOffline phone controls, calling, voice hotwords & intelligent chat capabilities!"
            }
            "thanks" -> {
                responseText = "आपका बहुत स्वागत है! 😊"
            }
            "bye" -> {
                responseText = "अलविदा! फिर मिलेंगे! 👋"
            }
            else -> {
                responseText = "🤔 समझ गई! '$cleanInput' - VANIE is processing your request offline."
            }
        }

        return NlpResult(
            intent = bestIntent,
            confidence = bestScore,
            sentiment = sentiment,
            sentimentConfidence = sentimentConf,
            responseText = responseText,
            actionCommand = actionCommand,
            targetName = targetName,
            messageBody = messageBody
        )
    }

    private fun calculateSentiment(text: str): Pair<String, Float> {
        val words = text.lowercase().split("\\s+".toRegex())
        var score = 0
        var matches = 0

        for (w in words) {
            if (positiveWords.containsKey(w)) {
                score += positiveWords[w] ?: 1
                matches++
            } else if (negativeWords.containsKey(w)) {
                score -= negativeWords[w] ?: 1
                matches++
            }
        }

        if (matches == 0) return Pair("neutral", 0.5f)
        val conf = min(1.0f, matches.toFloat() / words.size.coerceAtLeast(1))
        return when {
            score > 0 -> Pair("positive", conf)
            score < 0 -> Pair("negative", conf)
            else -> Pair("neutral", conf)
        }
    }

    private fun extractContactName(input: String, keywords: List<String>): String? {
        var clean = input
        for (kw in keywords) {
            clean = clean.replace(kw, "", ignoreCase = true)
        }
        clean = clean.replace(Regex("(?i)to|for|person|naam|name|ko"), "").trim()
        return if (clean.isNotBlank()) clean else null
    }

    private fun extractContactAndMessage(input: String): Pair<String?, String?> {
        val parts = input.split(Regex("(?i)message|text|bolna|saying|that|ko"), 2)
        val contactPart = extractContactName(parts[0], listOf("whatsapp", "sms", "text", "send", "मैसेज करो", "व्हाट्सएप करो"))
        val msgPart = if (parts.size > 1 && parts[1].isNotBlank()) parts[1].trim() else null
        return Pair(contactPart, msgPart)
    }
}
