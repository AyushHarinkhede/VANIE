package com.vanie.ai.util

import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import java.util.Locale

object VanieTtsUtils {

    /**
     * Complete emoji and symbol cleaner.
     * Guarantees TTS speaks ONLY words and never pronounces emoji names or symbols.
     */
    fun cleanTextForTts(text: String): String {
        if (text.isBlank()) return ""
        return text
            // High and Low surrogate pairs (Emojis, pictographs)
            .replace(Regex("[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]"), "")
            // Miscellaneous Symbols and Arrows
            .replace(Regex("[\\u2600-\\u27BF]"), "")
            // Miscellaneous Technical / Supplemental Symbols
            .replace(Regex("[\\u2300-\\u23FF]"), "")
            .replace(Regex("[\\u2B00-\\u2BFF]"), "")
            .replace(Regex("[\\u1F000-\\u1F9FF]"), "")
            .replace(Regex("[\\u1F600-\\u1F64F]"), "") // Emoticons
            .replace(Regex("[\\u1F300-\\u1F5FF]"), "") // Misc Symbols and Pictographs
            .replace(Regex("[\\u1F680-\\u1F6FF]"), "") // Transport & Map
            .replace(Regex("[\\u1F1E0-\\u1F1FF]"), "") // Flags
            .replace(Regex("[\\p{So}\\p{Cn}\\p{Cs}\\p{Co}\\p{Cc}]"), "")
            // Markdown formatting symbols
            .replace(Regex("[*_#`~]"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
    }

    /**
     * Expressive TTS Delivery with Punctuation Pauses and Prosody:
     * - Comma (,): brief pause (halki rukegi)
     * - Full stop (.): full sentence pause (rukk jayegi)
     * - Question mark (?): rising question inflection (que type tone)
     * - Exclamation mark (!): slightly louder and energetic tone (halki loud)
     */
    fun speakExpressive(
        tts: TextToSpeech?,
        text: String,
        utteranceId: String,
        speechSpeed: Float = 1.0f
    ) {
        if (tts == null) return

        val cleanedText = cleanTextForTts(text)
        if (cleanedText.isBlank()) return

        tts.setSpeechRate(speechSpeed)

        // Try SSML if supported by TTS engine (e.g. Google Speech Services)
        val ssmlSupported = try {
            val engines = tts.engines
            val defaultEngine = tts.defaultEngine
            defaultEngine != null && defaultEngine.contains("google", ignoreCase = true)
        } catch (e: Exception) {
            true
        }

        if (ssmlSupported) {
            val ssmlBuilder = StringBuilder()
            ssmlBuilder.append("<speak>")

            // Split into sentence tokens while keeping delimiters
            val pattern = Regex("(?<=[.?!,])|(?=[.?!,])")
            val parts = cleanedText.split(pattern)

            var currentPhrase = StringBuilder()

            for (part in parts) {
                when (part.trim()) {
                    "," -> {
                        if (currentPhrase.isNotBlank()) {
                            ssmlBuilder.append(escapeXml(currentPhrase.toString().trim()))
                            currentPhrase.clear()
                        }
                        ssmlBuilder.append("<break time=\"250ms\"/> ")
                    }
                    "." -> {
                        if (currentPhrase.isNotBlank()) {
                            ssmlBuilder.append(escapeXml(currentPhrase.toString().trim()))
                            currentPhrase.clear()
                        }
                        ssmlBuilder.append("<break time=\"600ms\"/> ")
                    }
                    "?" -> {
                        if (currentPhrase.isNotBlank()) {
                            ssmlBuilder.append("<prosody pitch=\"+15%\">")
                            ssmlBuilder.append(escapeXml(currentPhrase.toString().trim()))
                            ssmlBuilder.append("?</prosody>")
                            currentPhrase.clear()
                        }
                        ssmlBuilder.append("<break time=\"500ms\"/> ")
                    }
                    "!" -> {
                        if (currentPhrase.isNotBlank()) {
                            ssmlBuilder.append("<prosody volume=\"loud\" pitch=\"+8%\">")
                            ssmlBuilder.append(escapeXml(currentPhrase.toString().trim()))
                            ssmlBuilder.append("!</prosody>")
                            currentPhrase.clear()
                        }
                        ssmlBuilder.append("<break time=\"500ms\"/> ")
                    }
                    else -> {
                        currentPhrase.append(part)
                    }
                }
            }
            if (currentPhrase.isNotBlank()) {
                ssmlBuilder.append(escapeXml(currentPhrase.toString().trim()))
            }
            ssmlBuilder.append("</speak>")

            val ssmlString = ssmlBuilder.toString()
            val result = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                tts.speak(ssmlString, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
            } else {
                @Suppress("DEPRECATION")
                tts.speak(ssmlString, TextToSpeech.QUEUE_FLUSH, null)
            }

            if (result == TextToSpeech.SUCCESS) {
                return
            }
        }

        // Fallback: Sentence-by-sentence queue with pitch and pause modulation
        speakWithChunkedProsody(tts, cleanedText, utteranceId)
    }

    private fun speakWithChunkedProsody(tts: TextToSpeech, cleanedText: String, utteranceId: String) {
        // Regex splits text by sentence boundary (. ? ! ,) while keeping punctuation
        val sentenceRegex = Regex("(?<=[.?!,])\\s+")
        val chunks = cleanedText.split(sentenceRegex)

        var isFirst = true

        for ((index, chunk) in chunks.withIndex()) {
            val trimChunk = chunk.trim()
            if (trimChunk.isEmpty()) continue

            val queueMode = if (isFirst) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD
            isFirst = false

            // Adjust Pitch & Volume based on punctuation
            var pitch = 1.0f
            var volume = 1.0f
            var silentPauseMs: Long = 300L

            when {
                trimChunk.endsWith("?") -> {
                    pitch = 1.25f // Elevated question tone
                    silentPauseMs = 500L
                }
                trimChunk.endsWith("!") -> {
                    pitch = 1.12f // Excited/Louder tone
                    volume = 1.2f
                    silentPauseMs = 500L
                }
                trimChunk.endsWith(",") -> {
                    pitch = 1.0f
                    silentPauseMs = 250L // Slight pause
                }
                trimChunk.endsWith(".") -> {
                    pitch = 1.0f
                    silentPauseMs = 600L // Full stop pause
                }
            }

            tts.setPitch(pitch)

            val chunkId = "${utteranceId}_chunk_$index"

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                val params = Bundle().apply {
                    putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, volume.coerceIn(0.1f, 1.0f))
                }
                tts.speak(trimChunk, queueMode, params, chunkId)
                tts.playSilentUtterance(silentPauseMs, TextToSpeech.QUEUE_ADD, "${chunkId}_pause")
            } else {
                @Suppress("DEPRECATION")
                val params = HashMap<String, String>().apply {
                    put(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, chunkId)
                    put(TextToSpeech.Engine.KEY_PARAM_VOLUME, volume.coerceIn(0.1f, 1.0f).toString())
                }
                @Suppress("DEPRECATION")
                tts.speak(trimChunk, queueMode, params)
                @Suppress("DEPRECATION")
                tts.playSilence(silentPauseMs, TextToSpeech.QUEUE_ADD, params)
            }
        }
    }

    private fun escapeXml(input: String): String {
        return input
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;")
    }
}
