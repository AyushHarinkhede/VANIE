package com.vanie.ai.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vanie.ai.R
import com.vanie.ai.ui.theme.AccentCyan
import com.vanie.ai.ui.theme.AccentGreen
import com.vanie.ai.ui.theme.AccentPurple
import java.util.Locale
import java.util.UUID
import kotlinx.coroutines.delay

@Immutable
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val sender: String, // "user" or "vanie"
    val text: String,
    val timestamp: String = "Now"
)

fun cleanTextForTts(text: String): String {
    if (text.isBlank()) return ""
    return text
        .replace(Regex("[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]"), "")
        .replace(Regex("[\\u2600-\\u27BF]"), "")
        .replace(Regex("[\\u2300-\\u23FF]"), "")
        .replace(Regex("[\\u2B00-\\u2BFF]"), "")
        .replace(Regex("[\\u1F000-\\u1F9FF]"), "")
        .replace(Regex("[\\p{So}\\p{Cn}\\p{Cs}\\p{Co}\\p{Cc}]"), "")
        .replace(Regex("[*_#`~]"), "")
        .replace(Regex("\\s+"), " ")
        .trim()
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    messages: List<ChatMessage>,
    isThinking: Boolean,
    clearAnimationTrigger: Int = 0,
    onSendMessage: (String) -> Unit,
    onMicClick: () -> Unit
) {
    var textState by remember { mutableStateOf("") }
    var currentlySpeakingId by remember { mutableStateOf<String?>(null) }
    val listState = rememberLazyListState()
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current

    // Set to track message IDs whose typing animation has completed (prevents re-animating on scroll)
    val animatedMessageIds = remember { mutableStateMapOf<String, Boolean>() }

    val mediaPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            onSendMessage("Attached image: $uri")
        }
    }

    var ttsEngine by remember { mutableStateOf<TextToSpeech?>(null) }

    DisposableEffect(Unit) {
        val tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // TTS ready
            }
        }
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) {
                currentlySpeakingId = null
            }
            override fun onError(utteranceId: String?) {
                currentlySpeakingId = null
            }
        })
        ttsEngine = tts
        onDispose {
            tts.stop()
            tts.shutdown()
        }
    }

    LaunchedEffect(messages.size, isThinking) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(
                index = messages.size - 1,
                scrollOffset = 0
            )
        }
    }

    LaunchedEffect(clearAnimationTrigger) {
        if (clearAnimationTrigger > 0 && messages.isNotEmpty()) {
            listState.animateScrollToItem(0)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Transparent)
    ) {
        // Chat Message List (Scrolls edge-to-edge behind floating top bar and input bar)
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
            contentPadding = PaddingValues(top = 76.dp, bottom = 14.dp)
        ) {
            items(
                items = messages,
                key = { msg -> msg.id }
            ) { msg ->
                AnimatedVisibility(
                    visible = true,
                    enter = fadeIn() + slideInVertically(animationSpec = spring(stiffness = Spring.StiffnessLow))
                ) {
                    GlassmorphicChatBubble(
                        message = msg,
                        isSpeaking = currentlySpeakingId == msg.id,
                        hasAnimated = animatedMessageIds.containsKey(msg.id),
                        onAnimationComplete = { animatedMessageIds[msg.id] = true },
                        onEditUserMessage = { editText ->
                            textState = editText
                        },
                        onCopyText = { text ->
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            val clip = ClipData.newPlainText("VANIE Text", text)
                            clipboard.setPrimaryClip(clip)
                            Toast.makeText(context, "Copied to clipboard!", Toast.LENGTH_SHORT).show()
                        },
                        onToggleSpeakText = { text ->
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            if (currentlySpeakingId == msg.id) {
                                ttsEngine?.stop()
                                currentlySpeakingId = null
                            } else {
                                ttsEngine?.stop()
                                currentlySpeakingId = msg.id
                                val cleanText = cleanTextForTts(text)
                                ttsEngine?.language = Locale.US
                                ttsEngine?.speak(cleanText, TextToSpeech.QUEUE_FLUSH, null, msg.id)
                            }
                        }
                    )
                }
            }

            if (isThinking) {
                item(key = "thinking_indicator") {
                    ThinkingIndicator()
                }
            }
        }

        // Floating Liquid Glass Wider Input Action Bar (With Animated Send & Mic Buttons)
        Surface(
            tonalElevation = 6.dp,
            shadowElevation = 8.dp,
            shape = RoundedCornerShape(30.dp),
            color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.75f),
            border = BorderStroke(
                1.dp,
                Brush.horizontalGradient(
                    listOf(
                        AccentCyan.copy(alpha = 0.5f),
                        AccentPurple.copy(alpha = 0.5f)
                    )
                )
            ),
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 8.dp)
                .navigationBarsPadding()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 6.dp, vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Water Drop Attach File Button
                IconButton(
                    onClick = {
                        com.vanie.ai.util.VanieHaptics.performClick(context)
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        mediaPickerLauncher.launch("image/*")
                    },
                    modifier = Modifier
                        .size(42.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.5f))
                ) {
                    Icon(
                        imageVector = Icons.Default.AttachFile,
                        contentDescription = "Attach File",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(modifier = Modifier.width(4.dp))

                // Wider Input Text Field
                OutlinedTextField(
                    value = textState,
                    onValueChange = {
                        if (it.length > textState.length) {
                            com.vanie.ai.util.VanieHaptics.performModePulse(context)
                        }
                        textState = it
                    },
                    placeholder = {
                        Text(
                            text = "Ask VANIE...",
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Normal,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                        )
                    },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(26.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.65f),
                        unfocusedContainerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.4f),
                        focusedBorderColor = AccentCyan,
                        unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                    ),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = {
                        if (textState.isNotBlank()) {
                            com.vanie.ai.util.VanieHaptics.performSuccess(context)
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            onSendMessage(textState)
                            textState = ""
                        }
                    })
                )

                Spacer(modifier = Modifier.width(4.dp))

                // Live Voice VANIE Mic Button
                IconButton(
                    onClick = {
                        com.vanie.ai.util.VanieHaptics.performSuccess(context)
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onMicClick()
                    },
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.linearGradient(
                                colors = listOf(
                                    MaterialTheme.colorScheme.primary,
                                    AccentCyan
                                )
                            )
                        )
                        .border(1.dp, Color.White.copy(alpha = 0.4f), CircleShape)
                ) {
                    Icon(
                        imageVector = Icons.Default.Mic,
                        contentDescription = "Live Voice VANIE",
                        tint = Color.White
                    )
                }

                // Send Button with Smooth Fade & Spring Bouncy Scale Animation
                AnimatedVisibility(
                    visible = textState.isNotBlank(),
                    enter = fadeIn(animationSpec = tween(250)) + scaleIn(animationSpec = spring(dampingRatio = Spring.DampingRatioLowBouncy, stiffness = Spring.StiffnessLow)),
                    exit = fadeOut(animationSpec = tween(200)) + scaleOut(animationSpec = spring(stiffness = Spring.StiffnessHigh))
                ) {
                    Row {
                        Spacer(modifier = Modifier.width(4.dp))
                        IconButton(
                            onClick = {
                                if (textState.isNotBlank()) {
                                    com.vanie.ai.util.VanieHaptics.performSuccess(context)
                                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                    onSendMessage(textState)
                                    textState = ""
                                }
                            },
                            modifier = Modifier
                                .size(44.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(
                                        colors = listOf(
                                            AccentPurple,
                                            MaterialTheme.colorScheme.primary
                                        )
                                    )
                                )
                                .border(1.dp, Color.White.copy(alpha = 0.4f), CircleShape)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Send,
                                contentDescription = "Send Message",
                                tint = Color.White
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun GlassmorphicChatBubble(
    message: ChatMessage,
    isSpeaking: Boolean,
    hasAnimated: Boolean,
    onAnimationComplete: () -> Unit,
    onEditUserMessage: (String) -> Unit = {},
    onCopyText: (String) -> Unit,
    onToggleSpeakText: (String) -> Unit
) {
    val isUser = message.sender == "user"
    val alignment = if (isUser) Alignment.End else Alignment.Start

    // If message has already completed typing or is from user, start with full text directly (prevents scroll re-typing)
    var displayedText by remember(message.id) {
        mutableStateOf(if (isUser || hasAnimated) message.text else "")
    }
    var isTypingFinished by remember(message.id) {
        mutableStateOf(isUser || hasAnimated)
    }

    LaunchedEffect(message.id, message.text) {
        if (!isUser && !hasAnimated) {
            val fullText = message.text
            if (displayedText.length < fullText.length) {
                for (i in 1..fullText.length) {
                    displayedText = fullText.substring(0, i)
                    delay(12) // Smooth futuristic typing animation (~12ms per char)
                }
            }
            isTypingFinished = true
            onAnimationComplete()
        }
    }

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = alignment
    ) {
        Surface(
            shape = RoundedCornerShape(
                topStart = 20.dp,
                topEnd = 20.dp,
                bottomStart = if (isUser) 20.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 20.dp
            ),
            color = if (isUser) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f)
            },
            tonalElevation = if (isUser) 4.dp else 2.dp,
            shadowElevation = if (isUser) 2.dp else 1.dp,
            border = BorderStroke(
                1.dp,
                if (isUser) {
                    MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                } else {
                    Brush.horizontalGradient(
                        colors = listOf(
                            AccentCyan.copy(alpha = 0.5f),
                            AccentPurple.copy(alpha = 0.5f)
                        )
                    )
                }
            ),
            modifier = Modifier.widthIn(max = 310.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                // Header badge for VANIE responses
                if (!isUser) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(bottom = 8.dp)
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.vanie),
                            contentDescription = "VANIE Avatar",
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "VANIE",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = AccentCyan
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(AccentGreen)
                        )
                    }
                }

                // Message Text with optional active typing cursor
                val textToShow = if (!isTypingFinished && !isUser) "$displayedText ▋" else displayedText
                Text(
                    text = textToShow,
                    color = if (isUser) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 15.sp,
                    lineHeight = 22.sp,
                    fontWeight = FontWeight.Normal
                )

                // Action Bar for User messages (Copy & Edit)
                if (isUser) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.End,
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.4f),
                            modifier = Modifier
                                .clickable { onCopyText(message.text) }
                                .padding(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ContentCopy,
                                contentDescription = "Copy Text",
                                tint = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f),
                                modifier = Modifier.size(15.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(8.dp))

                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.4f),
                            modifier = Modifier
                                .clickable { onEditUserMessage(message.text) }
                                .padding(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Edit,
                                contentDescription = "Edit Message",
                                tint = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f),
                                modifier = Modifier.size(15.dp)
                            )
                        }
                    }
                }

                // Action Bar for VANIE messages (Copy & Voice Reader)
                if (!isUser) {
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        horizontalArrangement = Arrangement.End,
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.5f),
                            modifier = Modifier
                                .clickable { onCopyText(message.text) }
                                .padding(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ContentCopy,
                                contentDescription = "Copy Text",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(16.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(8.dp))

                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.5f),
                            modifier = Modifier
                                .clickable { onToggleSpeakText(message.text) }
                                .padding(4.dp)
                        ) {
                            Icon(
                                imageVector = if (isSpeaking) Icons.Default.VolumeOff else Icons.Default.VolumeUp,
                                contentDescription = if (isSpeaking) "Stop Voice" else "Read Out Loud",
                                tint = if (isSpeaking) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.tertiary,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ThinkingIndicator() {
    val infiniteTransition = rememberInfiniteTransition(label = "dots")
    val dotAlpha by infiniteTransition.animateFloat(
        initialValue = 0.2f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "dotAlpha"
    )

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .clip(RoundedCornerShape(18.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f))
            .border(1.dp, AccentCyan.copy(alpha = 0.5f), RoundedCornerShape(18.dp))
            .padding(horizontal = 16.dp, vertical = 10.dp)
    ) {
        Image(
            painter = painterResource(id = R.drawable.vanie),
            contentDescription = null,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = "VANIE is thinking...",
            fontSize = 13.sp,
            color = AccentCyan,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Medium
        )
        Spacer(modifier = Modifier.width(6.dp))
        Box(
            modifier = Modifier
                .size(6.dp)
                .clip(CircleShape)
                .background(AccentPurple.copy(alpha = dotAlpha))
        )
    }
}

