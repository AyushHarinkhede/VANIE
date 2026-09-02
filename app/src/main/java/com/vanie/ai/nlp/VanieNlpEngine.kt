package com.vanie.ai.nlp

import android.content.Context
import com.google.gson.Gson
import com.google.gson.JsonObject
import java.io.InputStreamReader
import java.util.regex.Pattern
import kotlin.math.min
import kotlin.random.Random
import com.vanie.ai.control.VanieAlarmState
import com.vanie.ai.control.VanieStopwatch
import com.vanie.ai.control.VanieTaskManager

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
    SEND_WHATSAPP_CALL,
    CONFIRM_SEND_DRAFT,
    ANSWER_CALL,
    REJECT_CALL,
    BRIGHTNESS,
    ALARM,
    BATTERY,
    GET_DETAILED_BATTERY,
    GET_NETWORK_INFO,
    LOCATION_INFO,
    NOTIFICATION_READ,
    LAUNCH_APP,
    VOLUME_UP,
    VOLUME_DOWN,
    VOLUME_MUTE,
    OPEN_CAMERA,
    OPEN_GALLERY,
    OPEN_SETTINGS,
    OPEN_MAPS,
    OPEN_PLAYSTORE,
    OPEN_CALCULATOR,
    SET_ALARM,
    CONFIRM_ALARM_AM,
    CONFIRM_ALARM_PM,
    SET_TIMER,
    START_STOPWATCH,
    PAUSE_STOPWATCH,
    RESET_STOPWATCH,
    ADD_TASK,
    SHOW_TASKS,
    CLEAR_TASKS
}

class VanieNlpEngine(private val context: Context) {

    var activePersona: String = "default"
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

            if (jsonObject.has("intents")) {
                val intentsObj = jsonObject.getAsJsonObject("intents")
                intentsObj.entrySet().forEach { (intentKey, patternElement) ->
                    intentPatterns[intentKey] = Pattern.compile(
                        patternElement.asString,
                        Pattern.CASE_INSENSITIVE or Pattern.UNICODE_CASE
                    )
                }
            }

            if (jsonObject.has("jokes")) {
                jsonObject.getAsJsonArray("jokes").forEach { item ->
                    val obj = item.asJsonObject
                    if (obj.has("joke")) jokes.add(obj.get("joke").asString)
                }
            }

            if (jsonObject.has("riddles")) {
                jsonObject.getAsJsonArray("riddles").forEach { item ->
                    val obj = item.asJsonObject
                    if (obj.has("riddle") && obj.has("answer")) {
                        riddles.add(Pair(obj.get("riddle").asString, obj.get("answer").asString))
                    }
                }
            }

            if (jsonObject.has("quotes")) {
                jsonObject.getAsJsonArray("quotes").forEach { quotes.add(it.asString) }
            }

            if (jsonObject.has("facts")) {
                jsonObject.getAsJsonArray("facts").forEach { facts.add(it.asString) }
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
                responseText = "Please enter a message or command."
            )
        }

        val lower = cleanInput.lowercase()
        var bestIntent = "general"

        // 1. Math Calculation Check
        val mathMatch = Regex("(\\d+\\.?\\d*)\\s*([+\\-*/])\\s*(\\d+\\.?\\d*)").find(cleanInput)
        if (mathMatch != null) {
            val num1 = mathMatch.groupValues[1].toDoubleOrNull() ?: 0.0
            val op = mathMatch.groupValues[2]
            val num2 = mathMatch.groupValues[3].toDoubleOrNull() ?: 0.0
            val calcResult = when (op) {
                "+" -> num1 + num2
                "-" -> num1 - num2
                "*" -> num1 * num2
                "/" -> if (num2 != 0.0) num1 / num2 else Double.NaN
                else -> 0.0
            }
            val resText = if (calcResult.isNaN()) "Cannot divide by zero!" else "Result: $num1 $op $num2 = $calcResult"
            return NlpResult(
                intent = "math",
                confidence = 1.0f,
                sentiment = "neutral",
                sentimentConfidence = 0.9f,
                responseText = resText,
                actionCommand = ActionCommand.NONE
            )
        }

        // 2. Draft Send Confirmation Check ("send it", "bhej do", "ha bhej do", "confirm send")
        if (lower == "send it" || lower == "bhej do" || lower == "confirm send" || lower == "yes send" || lower == "ha bhej do" || lower == "send") {
            return NlpResult(
                intent = "confirm_send",
                confidence = 1.0f,
                sentiment = "positive",
                sentimentConfidence = 0.9f,
                responseText = "Sending queued draft message...",
                actionCommand = ActionCommand.CONFIRM_SEND_DRAFT
            )
        }

        // 3. Multi-Variation Natural Language Intent Matcher
        when {
            // Torch / Flashlight ON variations
            lower.contains("torch on") || lower.contains("flashlight on") || lower.contains("flash on") ||
            lower.contains("light on") || lower.contains("turn on torch") || lower.contains("turn on flashlight") ||
            lower.contains("enable torch") || lower.contains("light up") || lower.contains("batti jalao") ||
            lower.contains("batti on") || lower.contains("torch chalu") || lower.contains("light chalu") ||
            lower.contains("flash chalu") || lower.contains("light start") -> bestIntent = "torch_on"

            // Torch / Flashlight OFF variations
            lower.contains("torch off") || lower.contains("flashlight off") || lower.contains("flash off") ||
            lower.contains("light off") || lower.contains("turn off torch") || lower.contains("turn off flashlight") ||
            lower.contains("disable torch") || lower.contains("batti bujha") || lower.contains("batti off") ||
            lower.contains("torch band") || lower.contains("light band") || lower.contains("flash band") -> bestIntent = "torch_off"

            // WiFi ON variations (including data/internet/net synonyms)
            lower.contains("wifi on") || lower.contains("turn on wifi") || lower.contains("enable wifi") ||
            lower.contains("wifi chalu") || lower.contains("wifi start") || lower.contains("net on") ||
            lower.contains("data on") || lower.contains("internet on") || lower.contains("mobile data on") ||
            lower.contains("connect wifi") -> bestIntent = "wifi_on"

            // WiFi OFF variations
            lower.contains("wifi off") || lower.contains("turn off wifi") || lower.contains("disable wifi") ||
            lower.contains("wifi band") || lower.contains("net off") || lower.contains("data off") ||
            lower.contains("internet off") -> bestIntent = "wifi_off"

            // Bluetooth ON variations
            lower.contains("bluetooth on") || lower.contains("turn on bluetooth") || lower.contains("enable bluetooth") ||
            lower.contains("bt on") || lower.contains("bluetooth chalu") || lower.contains("bluetooth start") -> bestIntent = "bluetooth_on"

            // Bluetooth OFF variations
            lower.contains("bluetooth off") || lower.contains("turn off bluetooth") || lower.contains("disable bluetooth") ||
            lower.contains("bt off") || lower.contains("bluetooth band") || lower.contains("bluetooth stop") -> bestIntent = "bluetooth_off"

            // GPS / Location variations
            lower.contains("location") || lower.contains("gps") || lower.contains("my location") ||
            lower.contains("track location") || lower.contains("gps on") || lower.contains("rasta") -> bestIntent = "location_info"

            // Sound Modes & DND (with synonyms like quiet mode, shh mode, do not disturb)
            lower.contains("silent mode") || lower.contains("phone silent") || lower.contains("silent chalu") ||
            lower.contains("mute phone") || lower.contains("silent karo") || lower.contains("make silent") ||
            lower.contains("shh mode") || lower.contains("quiet mode") || lower.contains("silent par") -> bestIntent = "mode_silent"

            lower.contains("vibrate mode") || lower.contains("vibration mode") || lower.contains("vibrate chalu") ||
            lower.contains("vibration on") || lower.contains("vibrate karo") -> bestIntent = "mode_vibrate"

            lower.contains("ring mode") || lower.contains("normal mode") || lower.contains("ringer on") ||
            lower.contains("unmute phone") || lower.contains("ring chalu") || lower.contains("ringing mode") -> bestIntent = "mode_ring"

            lower.contains("dnd on") || lower.contains("do not disturb on") || lower.contains("dnd chalu") ||
            lower.contains("dnd enable") || lower.contains("do not disturb") || lower.contains("disturb mat karo") -> bestIntent = "dnd_on"

            lower.contains("dnd off") || lower.contains("do not disturb off") || lower.contains("dnd band") ||
            lower.contains("dnd disable") -> bestIntent = "dnd_off"

            // Network & Phone Info queries
            lower.contains("network type") || lower.contains("network info") || lower.contains("sim info") ||
            lower.contains("operator") || lower.contains("5g") || lower.contains("4g") || lower.contains("carrier") -> bestIntent = "get_network_info"

            // Battery Detailed Info queries
            lower.contains("battery percentage") || lower.contains("charge percent") || lower.contains("kitni charge") ||
            lower.contains("battery status") || lower.contains("battery info") || lower.contains("power status") -> bestIntent = "get_detailed_battery"

            // WhatsApp Voice Call vs Normal Cellular Call
            lower.contains("whatsapp call") || lower.contains("call on whatsapp") || lower.contains("whatsapp se call") ||
            (lower.contains("call ") && lower.contains("whatsapp")) -> bestIntent = "send_whatsapp_call"

            lower.contains("call ") || lower.contains("dial ") || lower.contains("phone karo") ||
            lower.contains("call lagaao") || lower.contains("milaao") -> bestIntent = "make_call"

            lower.contains("whatsapp") || lower.contains("whatsapp karo") || lower.contains("message on whatsapp") -> bestIntent = "send_whatsapp"
            lower.contains("text ") || lower.contains("sms ") || lower.contains("message karo") -> bestIntent = "send_sms"

            // Status & Info
            lower.contains("battery") || lower.contains("charge") || lower.contains("kitni battery") -> bestIntent = "battery"
            lower.contains("notification") || lower.contains("read message") || lower.contains("unread") -> bestIntent = "notification_read"
            lower.contains("brightness") || lower.contains("screen light") || lower.contains("brighten") -> bestIntent = "brightness"
            
            // AM / PM Confirmation State
            VanieAlarmState.isWaitingForAmPm && (lower.contains("am") || lower.contains("subah") || lower.contains("morning")) -> bestIntent = "confirm_alarm_am"
            VanieAlarmState.isWaitingForAmPm && (lower.contains("pm") || lower.contains("shaam") || lower.contains("raat") || lower.contains("evening") || lower.contains("night") || lower.contains("dopahar")) -> bestIntent = "confirm_alarm_pm"

            // Alarm, Timer, Stopwatch, Task intents
            lower.contains("alarm") || lower.contains("अलार्म") || (lower.contains("baje") && lower.contains("laga")) -> bestIntent = "set_alarm"
            lower.contains("timer") || lower.contains("टाइमर") -> bestIntent = "set_timer"
            lower.contains("stopwatch") || lower.contains("स्टॉपवॉच") -> bestIntent = "stopwatch"
            lower.contains("task") || lower.contains("remind") || lower.contains("yaad") || lower.contains("to do") -> bestIntent = "task"

            // Conversational & Fun
            lower.contains("hi") || lower.contains("hello") || lower.contains("hey") || lower.contains("namaste") -> bestIntent = "greeting"
            lower.contains("who made") || lower.contains("banaya") || lower.contains("creator") || lower.contains("manufacturer") || lower.contains("developer") || lower.contains("full form") || lower.contains("who are you") || lower.contains("what is vanie") || lower.contains("vanie") -> bestIntent = "vanie"
            lower.contains("joke") || lower.contains("majak") || lower.contains("hansaao") -> bestIntent = "joke"
            lower.contains("riddle") || lower.contains("paheli") -> bestIntent = "riddle"
            lower.contains("quote") || lower.contains("motivation") -> bestIntent = "motivation"
            lower.contains("thanks") || lower.contains("thank you") || lower.contains("dhanyawad") -> bestIntent = "thanks"
            lower.contains("bye") || lower.contains("goodbye") || lower.contains("alvida") -> bestIntent = "bye"
        }

        var actionCommand = ActionCommand.NONE
        var targetName: String? = null
        var messageBody: String? = null
        var responseText = ""

        when (bestIntent) {
            "torch_on" -> {
                actionCommand = ActionCommand.TORCH_ON
                responseText = "Flashlight turned ON!"
            }
            "torch_off" -> {
                actionCommand = ActionCommand.TORCH_OFF
                responseText = "Flashlight turned OFF!"
            }
            "wifi_on" -> {
                actionCommand = ActionCommand.WIFI_ON
                responseText = "Opening Wi-Fi settings..."
            }
            "wifi_off" -> {
                actionCommand = ActionCommand.WIFI_OFF
                responseText = "Opening Wi-Fi settings to disable..."
            }
            "bluetooth_on" -> {
                actionCommand = ActionCommand.BLUETOOTH_ON
                responseText = "Opening Bluetooth controls..."
            }
            "bluetooth_off" -> {
                actionCommand = ActionCommand.BLUETOOTH_OFF
                responseText = "Opening Bluetooth controls..."
            }
            "dnd_on" -> {
                actionCommand = ActionCommand.DND_ON
                responseText = "Do Not Disturb (DND) activated."
            }
            "dnd_off" -> {
                actionCommand = ActionCommand.DND_OFF
                responseText = "Do Not Disturb (DND) disabled."
            }
            "mode_silent" -> {
                actionCommand = ActionCommand.MODE_SILENT
                responseText = "Phone set to Silent Mode."
            }
            "mode_vibrate" -> {
                actionCommand = ActionCommand.MODE_VIBRATE
                responseText = "Phone set to Vibrate Mode."
            }
            "mode_ring" -> {
                actionCommand = ActionCommand.MODE_RING
                responseText = "Phone set to Normal Ringing Mode."
            }
            "volume_up" -> {
                actionCommand = ActionCommand.VOLUME_UP
                responseText = "Increasing volume..."
            }
            "volume_down" -> {
                actionCommand = ActionCommand.VOLUME_DOWN
                responseText = "Decreasing volume..."
            }
            "volume_mute" -> {
                actionCommand = ActionCommand.VOLUME_MUTE
                responseText = "Muting media volume..."
            }
            "open_camera" -> {
                actionCommand = ActionCommand.OPEN_CAMERA
                responseText = "Opening Camera..."
            }
            "open_gallery" -> {
                actionCommand = ActionCommand.OPEN_GALLERY
                responseText = "Opening Gallery..."
            }
            "open_settings" -> {
                actionCommand = ActionCommand.OPEN_SETTINGS
                responseText = "Opening System Settings..."
            }
            "open_maps" -> {
                actionCommand = ActionCommand.OPEN_MAPS
                responseText = "Opening Maps & Navigation..."
            }
            "open_playstore" -> {
                actionCommand = ActionCommand.OPEN_PLAYSTORE
                responseText = "Opening Play Store..."
            }
            "open_calculator" -> {
                actionCommand = ActionCommand.OPEN_CALCULATOR
                responseText = "Opening Calculator..."
            }
            "battery" -> {
                actionCommand = ActionCommand.BATTERY
                responseText = "Fetching battery status..."
            }
            "notification_read" -> {
                actionCommand = ActionCommand.NOTIFICATION_READ
                responseText = "Reading unread notifications..."
            }
            "brightness" -> {
                actionCommand = ActionCommand.BRIGHTNESS
                val num = Regex("\\d+").find(cleanInput)?.value
                targetName = num ?: "75"
                responseText = "Setting screen brightness to ${targetName}%..."
            }
            "confirm_alarm_am" -> {
                actionCommand = ActionCommand.CONFIRM_ALARM_AM
                responseText = "⏰ Subah (AM) ka alarm set kar diya gaya hai!"
            }
            "confirm_alarm_pm" -> {
                actionCommand = ActionCommand.CONFIRM_ALARM_PM
                responseText = "⏰ Shaam/Raat (PM) ka alarm set kar diya gaya hai!"
            }
            "set_alarm" -> {
                val digits = Regex("(\\d{1,2})(?::(\\d{2}))?").find(cleanInput)
                if (digits != null) {
                    val rawHour = digits.groupValues[1].toIntOrNull() ?: 7
                    val min = digits.groupValues.getOrNull(2)?.toIntOrNull() ?: 0
                    val hasAm = lower.contains("am") || lower.contains("subah") || lower.contains("morning")
                    val hasPm = lower.contains("pm") || lower.contains("shaam") || lower.contains("raat") || lower.contains("dopahar") || lower.contains("evening") || lower.contains("night")

                    if (hasAm) {
                        val h = if (rawHour == 12) 0 else rawHour
                        actionCommand = ActionCommand.SET_ALARM
                        targetName = "$h:$min"
                        responseText = "⏰ Alarm set for ${String.format("%02d:%02d", h, min)} (AM)!"
                        VanieAlarmState.isWaitingForAmPm = false
                    } else if (hasPm) {
                        val h = if (rawHour == 12) 12 else (rawHour % 12) + 12
                        actionCommand = ActionCommand.SET_ALARM
                        targetName = "$h:$min"
                        responseText = "⏰ Alarm set for ${String.format("%02d:%02d", h, min)} (PM)!"
                        VanieAlarmState.isWaitingForAmPm = false
                    } else {
                        VanieAlarmState.pendingHour = rawHour
                        VanieAlarmState.pendingMinute = min
                        VanieAlarmState.isWaitingForAmPm = true
                        actionCommand = ActionCommand.NONE
                        responseText = "⏰ Aapko $rawHour:${String.format("%02d", min)} ka alarm subah (AM) ka lagana hai ya shaam/raat (PM) ka?"
                    }
                } else {
                    actionCommand = ActionCommand.SET_ALARM
                    targetName = "7:0"
                    responseText = "⏰ Default alarm set for 7:00 AM!"
                }
            }
            "set_timer" -> {
                actionCommand = ActionCommand.SET_TIMER
                val num = Regex("\\d+").find(cleanInput)?.value?.toIntOrNull() ?: 60
                val isMin = lower.contains("min") || lower.contains("minute") || lower.contains("मिनट")
                val totalSec = if (isMin) num * 60 else num
                targetName = totalSec.toString()
                responseText = "⏱️ Timer set for $totalSec seconds!"
            }
            "stopwatch" -> {
                when {
                    lower.contains("pause") || lower.contains("rok") || lower.contains("stop") -> {
                        actionCommand = ActionCommand.PAUSE_STOPWATCH
                        responseText = VanieStopwatch.pause()
                    }
                    lower.contains("reset") || lower.contains("clear") -> {
                        actionCommand = ActionCommand.RESET_STOPWATCH
                        responseText = VanieStopwatch.reset()
                    }
                    else -> {
                        actionCommand = ActionCommand.START_STOPWATCH
                        responseText = VanieStopwatch.start()
                    }
                }
            }
            "task" -> {
                when {
                    lower.contains("show") || lower.contains("list") || lower.contains("dekh") || lower.contains("batao") -> {
                        actionCommand = ActionCommand.SHOW_TASKS
                        responseText = VanieTaskManager.getTasks()
                    }
                    lower.contains("clear") || lower.contains("delete") || lower.contains("hatao") -> {
                        actionCommand = ActionCommand.CLEAR_TASKS
                        responseText = VanieTaskManager.clearTasks()
                    }
                    else -> {
                        actionCommand = ActionCommand.ADD_TASK
                        val taskText = cleanInput.replace(Regex("(?i)(add|task|remind me to|remind|yaad dilana|to do)"), "").trim()
                        targetName = if (taskText.isNotEmpty()) taskText else cleanInput
                        responseText = com.vanie.ai.control.VanieTaskManager.addTask(targetName!!)
                    }
                }
            }
            "launch_app" -> {
                actionCommand = ActionCommand.LAUNCH_APP
                targetName = extractAppName(cleanInput)
                responseText = "Opening ${targetName ?: "application"}..."
            }
            "make_call" -> {
                actionCommand = ActionCommand.MAKE_CALL
                targetName = extractContactName(cleanInput, listOf("call", "dial", "phone karo", "call lagaao", "milaao"))
                responseText = if (targetName != null) "Calling $targetName..." else "Preparing to call..."
            }
            "send_sms" -> {
                actionCommand = ActionCommand.SEND_SMS
                val extracted = extractContactAndMessage(cleanInput)
                targetName = extracted.first
                messageBody = extracted.second
                responseText = "Preparing SMS for ${targetName ?: "contact"}..."
            }
            "send_whatsapp" -> {
                actionCommand = ActionCommand.SEND_WHATSAPP
                val extracted = extractContactAndMessage(cleanInput)
                targetName = extracted.first
                messageBody = extracted.second
                responseText = "Launching WhatsApp for ${targetName ?: "contact"}..."
            }
            "location_info" -> {
                actionCommand = ActionCommand.LOCATION_INFO
                responseText = "Opening Location & GPS settings..."
            }
            "get_network_info" -> {
                actionCommand = ActionCommand.GET_NETWORK_INFO
                responseText = "Fetching network and SIM info..."
            }
            "get_detailed_battery" -> {
                actionCommand = ActionCommand.GET_DETAILED_BATTERY
                responseText = "Fetching detailed battery metrics..."
            }
            "send_whatsapp_call" -> {
                actionCommand = ActionCommand.SEND_WHATSAPP_CALL
                targetName = extractContactName(cleanInput, listOf("whatsapp call", "call on whatsapp", "whatsapp se call", "whatsapp", "call"))
                responseText = if (targetName != null) "Initiating WhatsApp call to $targetName..." else "Preparing WhatsApp call..."
            }
            "joke" -> {
                responseText = if (jokes.isNotEmpty()) jokes.random() else "Why did the developer go broke? Because he used up all his cache!"
            }
            "riddle" -> {
                if (riddles.isNotEmpty()) {
                    val r = riddles.random()
                    responseText = "${r.first}\n\n(Answer: ${r.second})"
                } else {
                    responseText = "What has keys but no locks? (Answer: keyboard)"
                }
            }
            "motivation" -> {
                responseText = if (quotes.isNotEmpty()) quotes.random() else "Hard work beats talent when talent doesn't work hard!"
            }
            "greeting" -> {
                responseText = "Hello! I am VANIE (Virtual Agent of Neural Integrated Engine). How can I assist you today?"
            }
            "vanie" -> {
                responseText = "🤖 Main VANIE (Virtual Agent of Neural Integrated Engine) hoon! ✨\n👤 Mujhe mere creator Ayush Harinkhede ne design aur build kiya hai! 🚀💖 Main aapki offline hardware control, calls, messages, calculations, aur daily chit-chat me madad kar sakti hoon! 🌸"
            }
            "thanks" -> {
                responseText = "You're very welcome!"
            }
            "bye" -> {
                responseText = "Goodbye! Have a great day!"
            }
            else -> {
                val politeDenials = listOf(
                    "Aww, mujhe abhi iske baare me nahi pata ji! Main abhi seekh rahi hoon! 🌸✨",
                    "Yeh jankari mere paas abhi nahi hai, par main jald hi ise samajhna sikh lungi! 💖",
                    "Oops! Is vishay par mujhe zyada idea nahi hai. Kya main kisi aur chiz me madad karun? 😊",
                    "Arey, mujhe iske baare me abhi nahi pata! Par main har din nayi baatein sikh rahi hoon! 🚀✨",
                    "Mafi chahti hoon, yeh mere offline knowledge base me abhi nahi hai ji! 🌸"
                )
                responseText = politeDenials.random()
            }
        }

        if (activePersona == "cyberpunk") {
            responseText = "[NPU MATRIX]: $responseText"
        } else if (activePersona == "hinglish") {
            responseText = when (bestIntent) {
                "greeting" -> "Namaste ji! Main VANIE hoon. Bataiye kya madad karun?"
                "thanks" -> "Aapka swagat hai ji! VANIE hamesha ready hai."
                "bye" -> "Alvida! Phir milenge."
                else -> "Haan ji! $responseText"
            }
        }

        val sentimentResult = calculateSentiment(cleanInput)
        return NlpResult(
            intent = bestIntent,
            confidence = 0.95f,
            sentiment = sentimentResult.first,
            sentimentConfidence = sentimentResult.second,
            responseText = responseText,
            actionCommand = actionCommand,
            targetName = targetName,
            messageBody = messageBody
        )
    }

    private fun calculateSentiment(text: String): Pair<String, Float> {
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

    private fun extractAppName(input: String): String {
        var clean = input.lowercase()
        val removeWords = listOf("open", "launch", "chalao", "kholo", "start", "app", "please")
        for (w in removeWords) {
            clean = clean.replace(w, "").trim()
        }
        return if (clean.isNotBlank()) clean else "application"
    }

    private fun extractContactName(input: String, keywords: List<String>): String? {
        var clean = input
        for (kw in keywords) {
            clean = clean.replace(Regex("(?i)\\b" + Regex.escape(kw) + "\\b"), "")
        }
        clean = clean.replace(Regex("(?i)\\b(to|for|person|naam|name|ko|call|on whatsapp|in whatsapp)\\b"), "").trim()
        return if (clean.isNotBlank()) clean else null
    }

    private fun extractContactAndMessage(input: String): Pair<String?, String?> {
        val parts = input.split(Regex("(?i)\\b(message|text|bolna|saying|that|ko)\\b"), 2)
        val contactPart = extractContactName(parts[0], listOf("whatsapp", "sms", "text", "send", "message karo", "whatsapp karo"))
        val msgPart = if (parts.size > 1 && parts[1].isNotBlank()) parts[1].trim() else null
        return Pair(contactPart, msgPart)
    }
}
