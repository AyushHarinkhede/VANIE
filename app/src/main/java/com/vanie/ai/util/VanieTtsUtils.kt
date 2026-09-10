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

        try {
            // Ensure TTS language is set
            val langResult = tts.setLanguage(Locale.US)
            if (langResult == TextToSpeech.LANG_MISSING_DATA || langResult == TextToSpeech.LANG_NOT_SUPPORTED) {
                tts.setLanguage(Locale.getDefault())
            }
            tts.setSpeechRate(speechSpeed)

            // Sentence-by-sentence prosody with punctuation pauses
            val sentenceRegex = Regex("(?<=[.?!,])\\s+")
            val chunks = cleanedText.split(sentenceRegex)

            if (chunks.size <= 1) {
                // Single sentence: speak directly with punctuation pitch
                var pitch = 1.0f
                if (cleanedText.endsWith("?")) pitch = 1.22f
                else if (cleanedText.endsWith("!")) pitch = 1.12f
                tts.setPitch(pitch)

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    tts.speak(cleanedText, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
                } else {
                    @Suppress("DEPRECATION")
                    tts.speak(cleanedText, TextToSpeech.QUEUE_FLUSH, null)
                }
                return
            }

            var isFirst = true
            for ((index, chunk) in chunks.withIndex()) {
                val trimChunk = chunk.trim()
                if (trimChunk.isEmpty()) continue

                val queueMode = if (isFirst) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD
                isFirst = false

                var pitch = 1.0f
                var silentPauseMs: Long = 350L

                when {
                    trimChunk.endsWith("?") -> {
                        pitch = 1.25f // Elevated question tone
                        silentPauseMs = 500L
                    }
                    trimChunk.endsWith("!") -> {
                        pitch = 1.14f // Excited/Louder tone
                        silentPauseMs = 500L
                    }
                    trimChunk.endsWith(",") -> {
                        pitch = 1.0f
                        silentPauseMs = 250L // Slight pause (halki rukegi)
                    }
                    trimChunk.endsWith(".") -> {
                        pitch = 1.0f
                        silentPauseMs = 600L // Full stop pause (rukk jayegi)
                    }
                }

                tts.setPitch(pitch)
                val chunkId = "${utteranceId}_$index"

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    tts.speak(trimChunk, queueMode, null, chunkId)
                    tts.playSilentUtterance(silentPauseMs, TextToSpeech.QUEUE_ADD, "${chunkId}_pause")
                } else {
                    @Suppress("DEPRECATION")
                    val params = HashMap<String, String>().apply {
                        put(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, chunkId)
                    }
                    @Suppress("DEPRECATION")
                    tts.speak(trimChunk, queueMode, params)
                    @Suppress("DEPRECATION")
                    tts.playSilence(silentPauseMs, TextToSpeech.QUEUE_ADD, params)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Direct fallback
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    tts.speak(cleanedText, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
                } else {
                    @Suppress("DEPRECATION")
                    tts.speak(cleanedText, TextToSpeech.QUEUE_FLUSH, null)
                }
            } catch (ex: Exception) {
                ex.printStackTrace()
            }
        }
    }
}
