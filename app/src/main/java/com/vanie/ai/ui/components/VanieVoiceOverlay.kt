package com.vanie.ai.ui.components

import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vanie.ai.ui.theme.AccentCyan
import com.vanie.ai.ui.theme.AccentGreen
import com.vanie.ai.ui.theme.AccentPurple
import java.util.Locale
import kotlin.math.sin

enum class VoiceMode {
    USER_LISTENING,
    THINKING,
    VANIE_SPEAKING
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VanieVoiceOverlay(
    isListening: Boolean,
    spokenText: String = "",
    isThinking: Boolean = false,
    responseText: String = "",
    onResultText: (String) -> Unit = {},
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current

    var rmsLevel by remember { mutableFloatStateOf(0f) }
    var liveTranscript by remember { mutableStateOf("") }
    var currentMode by remember { mutableStateOf(VoiceMode.USER_LISTENING) }
    var speechRecognizer by remember { mutableStateOf<SpeechRecognizer?>(null) }
    var ttsEngine by remember { mutableStateOf<TextToSpeech?>(null) }

    // User Mute & Silent VANIE States
    var isUserMuted by remember { mutableStateOf(false) }
    var isVanieSilent by remember { mutableStateOf(false) }

    // Helper to start/restart speech listening
    fun startListeningInternal(recognizer: SpeechRecognizer?) {
        if (recognizer == null || isUserMuted) return
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
        }
        try {
            recognizer.startListening(intent)
            currentMode = VoiceMode.USER_LISTENING
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    // Initialize TTS with UtteranceProgressListener for Continuous Back-to-Back Loop
    DisposableEffect(context) {
        val tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // TTS ready
            }
        }
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                currentMode = VoiceMode.VANIE_SPEAKING
            }
            override fun onDone(utteranceId: String?) {
                // Continuous Loop: Auto-restart listening for next command after response finishes!
                if (isListening && !isUserMuted) {
                    liveTranscript = ""
                    startListeningInternal(speechRecognizer)
                }
            }
            override fun onError(utteranceId: String?) {
                if (isListening && !isUserMuted) {
                    liveTranscript = ""
                    startListeningInternal(speechRecognizer)
                }
            }
        })
        ttsEngine = tts
        onDispose {
            tts.stop()
            tts.shutdown()
        }
    }

    // Update Voice Mode based on props
    LaunchedEffect(isThinking, responseText) {
        if (isThinking) {
            currentMode = VoiceMode.THINKING
        } else if (responseText.isNotBlank()) {
            currentMode = VoiceMode.VANIE_SPEAKING
        } else {
            currentMode = VoiceMode.USER_LISTENING
        }
    }

    // Trigger vibration feedback
    fun performVibration(type: String) {
        try {
            val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vibratorManager.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            }
            if (vibrator.hasVibrator()) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    when (type) {
                        "start" -> vibrator.vibrate(VibrationEffect.createOneShot(40, VibrationEffect.DEFAULT_AMPLITUDE))
                        "finish" -> vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 30, 40, 30), -1))
                    }
                } else {
                    @Suppress("DEPRECATION")
                    vibrator.vibrate(40)
                }
            } else {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            }
        } catch (e: Exception) {
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
        }
    }

    // Manage Native SpeechRecognizer Lifecycle
    DisposableEffect(isListening) {
        if (isListening && SpeechRecognizer.isRecognitionAvailable(context)) {
            val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
            recognizer.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    currentMode = VoiceMode.USER_LISTENING
                }

                override fun onBeginningOfSpeech() {
                    performVibration("start")
                }

                override fun onRmsChanged(rmsdB: Float) {
                    val normalized = ((rmsdB + 2f) / 14f).coerceIn(0.05f, 1.0f)
                    rmsLevel = normalized
                }

                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {
                    performVibration("finish")
                    currentMode = VoiceMode.THINKING
                }

                override fun onError(error: Int) {
                    rmsLevel = 0f
                    // Auto-retry listening on timeout in continuous loop mode
                    if (isListening && !isUserMuted && currentMode == VoiceMode.USER_LISTENING) {
                        startListeningInternal(recognizer)
                    }
                }

                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        val text = matches[0]
                        liveTranscript = text
                        onResultText(text)
                    }
                }

                override fun onPartialResults(partialResults: Bundle?) {
                    val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        liveTranscript = matches[0]
                    }
                }

                override fun onEvent(eventType: Int, params: Bundle?) {}
            })

            speechRecognizer = recognizer
            if (!isUserMuted) {
                startListeningInternal(recognizer)
            }
        }

        onDispose {
            speechRecognizer?.stopListening()
            speechRecognizer?.destroy()
            speechRecognizer = null
        }
    }

    // Trigger TTS when responseText arrives
    LaunchedEffect(responseText) {
        if (responseText.isNotBlank() && !isVanieSilent) {
            currentMode = VoiceMode.VANIE_SPEAKING
            performVibration("finish")
            val spokenTextClean = com.vanie.ai.ui.screens.cleanTextForTts(responseText)
            if (spokenTextClean.isNotBlank()) {
                ttsEngine?.language = Locale.US
                ttsEngine?.speak(spokenTextClean, TextToSpeech.QUEUE_FLUSH, null, "VANIE_CONTINUOUS_VOICE")
            }
        }
    }

    if (isListening) {
        ModalBottomSheet(
            onDismissRequest = {
                speechRecognizer?.stopListening()
                ttsEngine?.stop()
                onDismiss()
            },
            sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
            shape = RoundedCornerShape(topStart = 36.dp, topEnd = 36.dp),
            containerColor = Color(0xFF0D1117).copy(alpha = 0.95f),
            scrimColor = Color.Black.copy(alpha = 0.6f)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp, vertical = 20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(12.dp))

                // HYPER-REALISTIC FLUID SINE WAVE VISUALIZER CANVAS
                HyperRealisticFluidWaveVisualizer(
                    mode = currentMode,
                    rmsLevel = rmsLevel
                )

                Spacer(modifier = Modifier.height(28.dp))

                // Clean Live Subtitle Transcript Display
                Surface(
                    shape = RoundedCornerShape(22.dp),
                    color = Color.White.copy(alpha = 0.06f),
                    border = BorderStroke(
                        1.dp,
                        Brush.horizontalGradient(
                            listOf(
                                AccentCyan.copy(alpha = 0.3f),
                                AccentPurple.copy(alpha = 0.3f)
                            )
                        )
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        val displayText = when {
                            responseText.isNotBlank() -> responseText
                            liveTranscript.isNotBlank() -> liveTranscript
                            spokenText.isNotBlank() -> spokenText
                            else -> "Speak a command... e.g. 'Turn on flashlight'"
                        }

                        Text(
                            text = displayText,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = if (displayText.startsWith("Speak")) Color.White.copy(alpha = 0.45f) else Color.White,
                            fontFamily = FontFamily.SansSerif,
                            lineHeight = 24.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(28.dp))

                // 3 WATER-DROP LIQUID ACTION BUTTONS ROW (User Mute, Silent VANIE, Close Cross)
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // 1. User Mic Mute / Unmute Button
                    IconButton(
                        onClick = {
                            com.vanie.ai.util.VanieHaptics.performClick(context)
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            isUserMuted = !isUserMuted
                            if (isUserMuted) {
                                speechRecognizer?.stopListening()
                            } else {
                                startListeningInternal(speechRecognizer)
                            }
                        },
                        modifier = Modifier
                            .size(54.dp)
                            .clip(CircleShape)
                            .background(
                                if (isUserMuted) {
                                    Color(0xFFFF5252).copy(alpha = 0.25f)
                                } else {
                                    AccentCyan.copy(alpha = 0.2f)
                                }
                            )
                            .border(
                                1.5.dp,
                                if (isUserMuted) Color(0xFFFF5252).copy(alpha = 0.6f) else AccentCyan.copy(alpha = 0.6f),
                                CircleShape
                            )
                    ) {
                        Icon(
                            imageVector = if (isUserMuted) Icons.Default.MicOff else Icons.Default.Mic,
                            contentDescription = "User Mic Mute Toggle",
                            tint = if (isUserMuted) Color(0xFFFF5252) else AccentCyan,
                            modifier = Modifier.size(24.dp)
                        )
                    }

                    // 2. Silent VANIE / Voice Reader Mute Button
                    IconButton(
                        onClick = {
                            com.vanie.ai.util.VanieHaptics.performClick(context)
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            isVanieSilent = !isVanieSilent
                            if (isVanieSilent) {
                                ttsEngine?.stop()
                            }
                        },
                        modifier = Modifier
                            .size(54.dp)
                            .clip(CircleShape)
                            .background(
                                if (isVanieSilent) {
                                    Color(0xFFFF9800).copy(alpha = 0.25f)
                                } else {
                                    AccentPurple.copy(alpha = 0.2f)
                                }
                            )
                            .border(
                                1.5.dp,
                                if (isVanieSilent) Color(0xFFFF9800).copy(alpha = 0.6f) else AccentPurple.copy(alpha = 0.6f),
                                CircleShape
                            )
                    ) {
                        Icon(
                            imageVector = if (isVanieSilent) Icons.Default.VolumeOff else Icons.Default.VolumeUp,
                            contentDescription = "Silent VANIE Toggle",
                            tint = if (isVanieSilent) Color(0xFFFF9800) else AccentPurple,
                            modifier = Modifier.size(24.dp)
                        )
                    }

                    // 3. Close Overlay Cross Button
                    IconButton(
                        onClick = {
                            com.vanie.ai.util.VanieHaptics.performSuccess(context)
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            speechRecognizer?.stopListening()
                            ttsEngine?.stop()
                            onDismiss()
                        },
                        modifier = Modifier
                            .size(54.dp)
                            .clip(CircleShape)
                            .background(Color.White.copy(alpha = 0.12f))
                            .border(1.5.dp, Color.White.copy(alpha = 0.4f), CircleShape)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Close Live Voice",
                            tint = Color.White.copy(alpha = 0.9f),
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))
            }
        }
    }
}

/**
 * Hyper-Realistic Fluid Sine Wave Canvas Visualizer:
 * Renders organic multi-layered sine wave physics with distinct live color themes:
 * - User Speaking: Vibrant Liquid Cyan (AccentCyan)
 * - Thinking: Pulsing Royal Purple (AccentPurple)
 * - VANIE Responding: Neon Cyber Green (AccentGreen)
 */
@Composable
fun HyperRealisticFluidWaveVisualizer(
    mode: VoiceMode,
    rmsLevel: Float
) {
    val infiniteTransition = rememberInfiniteTransition(label = "fluidWaveTransition")

    val wavePhase by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 2f * Math.PI.toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(2200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "wavePhase"
    )

    val primaryColor = when (mode) {
        VoiceMode.USER_LISTENING -> AccentCyan
        VoiceMode.THINKING -> AccentPurple
        VoiceMode.VANIE_SPEAKING -> AccentGreen
    }

    val secondaryColor = when (mode) {
        VoiceMode.USER_LISTENING -> AccentPurple
        VoiceMode.THINKING -> AccentCyan
        VoiceMode.VANIE_SPEAKING -> AccentCyan
    }

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .fillMaxWidth()
            .height(160.dp)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val width = size.width
            val height = size.height
            val centerY = height / 2f

            val effectiveRms = if (mode == VoiceMode.USER_LISTENING) rmsLevel else 0.45f
            val baseAmplitude = (height * 0.35f) * (0.25f + effectiveRms * 0.75f)

            // Render 3 overlapping harmonic fluid sine waves
            val waveConfigs = listOf(
                Triple(1.0f, 0.0f, primaryColor.copy(alpha = 0.85f)),
                Triple(1.6f, 0.9f, secondaryColor.copy(alpha = 0.50f)),
                Triple(2.2f, 1.8f, primaryColor.copy(alpha = 0.30f))
            )

            for ((freqMultiplier, phaseOffset, color) in waveConfigs) {
                val wavePath = Path()
                wavePath.moveTo(0f, centerY)

                val step = 4.dp.toPx()
                var x = 0f
                while (x <= width) {
                    val normalizedX = x / width
                    // Taper wave edges smoothly at ends
                    val edgeEnvelope = sin(normalizedX * Math.PI.toFloat())
                    val angle = (normalizedX * 3f * Math.PI.toFloat() * freqMultiplier) + wavePhase + phaseOffset
                    val y = centerY + baseAmplitude * edgeEnvelope * sin(angle)
                    wavePath.lineTo(x, y)
                    x += step
                }

                drawPath(
                    path = wavePath,
                    color = color,
                    style = Stroke(
                        width = (3.5dp * freqMultiplier).toPx(),
                        cap = androidx.compose.ui.graphics.StrokeCap.Round
                    )
                )
            }
        }
    }
}

