package com.vanie.ai.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.speech.tts.TextToSpeech
import android.widget.Toast
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
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.platform.LocalContext
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

@Immutable
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val sender: String, // "user" or "vanie"
    val text: String,
    val timestamp: String = "Now"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    messages: List<ChatMessage>,
    isThinking: Boolean,
    onSendMessage: (String) -> Unit,
    onMicClick: () -> Unit
) {
    var textState by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableIntStateOf(0) }
    var isToolsDrawerOpen by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    val context = LocalContext.current

    var ttsEngine by remember { mutableStateOf<TextToSpeech?>(null) }

    DisposableEffect(Unit) {
        val tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // Initialized
            }
        }
        ttsEngine = tts
        onDispose {
            tts.stop()
            tts.shutdown()
        }
    }

    val categoryTabs = listOf("⚡ Hardware", "📞 Telecom", "⏰ Productivity", "🧠 AI Fun")

    val commandsByCategory = remember {
        mapOf(
            0 to listOf("🔦 Flashlight ON", "🔕 Silent Mode", "🌙 Turn on DND", "🔋 Battery Status", "📱 System Info"),
            1 to listOf("📞 Call Contact", "💬 Send SMS", "💚 WhatsApp Message", "📞 Answer Call"),
            2 to listOf("⏰ Set Alarm 7 AM", "📲 Read Notifications", "🚀 Open YouTube", "🌐 Open Chrome"),
            3 to listOf("😄 Tell me a joke", "🤔 Give me a riddle", "💪 Motivational quote", "🧮 Calculate 25 * 4")
        )
    }

    LaunchedEffect(messages.size, isThinking) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(
                index = messages.size - 1,
                scrollOffset = 0
            )
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.background,
                        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    )
                )
            )
    ) {
        // Live System Status Bar
        LiveSystemStatusBar(onOpenTools = { isToolsDrawerOpen = true })

        // Chat Message List
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
            contentPadding = PaddingValues(vertical = 14.dp)
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
                        onCopyText = { text ->
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            val clip = ClipData.newPlainText("VANIE Text", text)
                            clipboard.setPrimaryClip(clip)
                            Toast.makeText(context, "Copied to clipboard! 📋", Toast.LENGTH_SHORT).show()
                        },
                        onSpeakText = { text ->
                            ttsEngine?.language = Locale.US
                            ttsEngine?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "VANIE_SPEAK")
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

        // Categorized Command Category Chips
        ScrollableTabRow(
            selectedTabIndex = selectedCategory,
            edgePadding = 12.dp,
            modifier = Modifier.fillMaxWidth(),
            containerColor = Color.Transparent,
            divider = {}
        ) {
            categoryTabs.forEachIndexed { index, title ->
                Tab(
                    selected = selectedCategory == index,
                    onClick = { selectedCategory = index },
                    text = {
                        Text(
                            text = title,
                            fontSize = 12.sp,
                            fontWeight = if (selectedCategory == index) FontWeight.Bold else FontWeight.Normal,
                            color = if (selectedCategory == index) AccentCyan else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                )
            }
        }

        // Command Action Pills for Selected Category
        LazyRow(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(
                items = commandsByCategory[selectedCategory] ?: emptyList(),
                key = { pill -> pill }
            ) { pill ->
                SuggestionChip(
                    onClick = { onSendMessage(pill) },
                    label = { Text(pill, fontSize = 12.sp, color = AccentCyan, fontFamily = FontFamily.Monospace) },
                    shape = RoundedCornerShape(20.dp),
                    colors = SuggestionChipDefaults.suggestionChipColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.85f)
                    ),
                    border = BorderStroke(1.dp, AccentCyan.copy(alpha = 0.4f))
                )
            }
        }

        // Glassmorphic Input Action Bar
        Surface(
            tonalElevation = 8.dp,
            modifier = Modifier.fillMaxWidth(),
            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.88f)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 10.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Tools Drawer Trigger
                IconButton(onClick = { isToolsDrawerOpen = true }) {
                    Icon(Icons.Default.Build, contentDescription = "AI Tools", tint = AccentGreen)
                }

                // Media Upload Button
                IconButton(
                    onClick = {
                        Toast.makeText(context, "Media attachment clicked", Toast.LENGTH_SHORT).show()
                    }
                ) {
                    Icon(
                        imageVector = Icons.Default.AttachFile,
                        contentDescription = "Attach File",
                        tint = AccentCyan
                    )
                }

                // Camera Upload Button
                IconButton(
                    onClick = {
                        Toast.makeText(context, "Camera upload clicked", Toast.LENGTH_SHORT).show()
                    }
                ) {
                    Icon(
                        imageVector = Icons.Default.CameraAlt,
                        contentDescription = "Camera",
                        tint = AccentPurple
                    )
                }

                Spacer(modifier = Modifier.width(4.dp))

                // Text Input Field with STRICT "Ask VANIE" Placeholder
                OutlinedTextField(
                    value = textState,
                    onValueChange = { textState = it },
                    placeholder = {
                        Text(
                            text = "Ask VANIE",
                            fontSize = 15.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Medium,
                            color = AccentCyan.copy(alpha = 0.7f)
                        )
                    },
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(24.dp),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = {
                        if (textState.isNotBlank()) {
                            onSendMessage(textState)
                            textState = ""
                        }
                    })
                )

                Spacer(modifier = Modifier.width(6.dp))

                // Voice Mic Button
                IconButton(
                    onClick = onMicClick,
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.linearGradient(listOf(AccentCyan, AccentPurple))
                        )
                ) {
                    Icon(
                        imageVector = Icons.Default.Mic,
                        contentDescription = "Voice Input",
                        tint = Color.White
                    )
                }

                Spacer(modifier = Modifier.width(4.dp))

                // Send Button
                IconButton(
                    onClick = {
                        if (textState.isNotBlank()) {
                            onSendMessage(textState)
                            textState = ""
                        }
                    },
                    enabled = textState.isNotBlank()
                ) {
                    Icon(
                        imageVector = Icons.Default.Send,
                        contentDescription = "Send",
                        tint = if (textState.isNotBlank()) AccentCyan else Color.Gray
                    )
                }
            }
        }
    }

    // AI Tools Drawer Modal Sheet
    if (isToolsDrawerOpen) {
        AiToolsModalSheet(
            onDismiss = { isToolsDrawerOpen = false },
            onSelectToolCommand = { cmd ->
                onSendMessage(cmd)
                isToolsDrawerOpen = false
            }
        )
    }
}

@Composable
fun LiveSystemStatusBar(onOpenTools: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 6.dp)
            .clip(RoundedCornerShape(16.dp))
            .border(1.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(16.dp)),
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(AccentGreen)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "NPU Engine: Active",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = AccentGreen
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.BatteryChargingFull, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text(text = "Offline Mode", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }

            IconButton(onClick = onOpenTools, modifier = Modifier.size(24.dp)) {
                Icon(Icons.Default.Widgets, contentDescription = "Tools", tint = AccentPurple, modifier = Modifier.size(18.dp))
            }
        }
    }
}

@Composable
fun GlassmorphicChatBubble(
    message: ChatMessage,
    onCopyText: (String) -> Unit,
    onSpeakText: (String) -> Unit
) {
    val isUser = message.sender == "user"
    val alignment = if (isUser) Alignment.End else Alignment.Start

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = alignment
    ) {
        if (!isUser) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 4.dp, start = 4.dp)
            ) {
                Image(
                    painter = painterResource(id = R.drawable.vanie),
                    contentDescription = null,
                    modifier = Modifier
                        .size(20.dp)
                        .clip(CircleShape)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "VANIE Neural Engine",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = AccentCyan
                )
            }
        }

        Box(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 22.dp,
                        topEnd = 22.dp,
                        bottomStart = if (isUser) 22.dp else 4.dp,
                        bottomEnd = if (isUser) 4.dp else 22.dp
                    )
                )
                .background(
                    if (isUser) MaterialTheme.colorScheme.primary
                    else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.75f)
                )
                .border(
                    width = 1.dp,
                    brush = if (isUser) Brush.linearGradient(listOf(Color.White.copy(alpha = 0.4f), Color.Transparent))
                    else Brush.linearGradient(listOf(AccentCyan.copy(alpha = 0.7f), AccentPurple.copy(alpha = 0.5f))),
                    shape = RoundedCornerShape(
                        topStart = 22.dp,
                        topEnd = 22.dp,
                        bottomStart = if (isUser) 22.dp else 4.dp,
                        bottomEnd = if (isUser) 4.dp else 22.dp
                    )
                )
                .padding(14.dp)
        ) {
            Column {
                Text(
                    text = message.text,
                    color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 15.sp,
                    lineHeight = 22.sp,
                    fontFamily = if (!isUser) FontFamily.Monospace else FontFamily.Default
                )

                if (!isUser) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        horizontalArrangement = Arrangement.End,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        IconButton(
                            onClick = { onCopyText(message.text) },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ContentCopy,
                                contentDescription = "Copy Text",
                                tint = AccentCyan,
                                modifier = Modifier.size(16.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(10.dp))

                        IconButton(
                            onClick = { onSpeakText(message.text) },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.VolumeUp,
                                contentDescription = "Speak Out Loud",
                                tint = AccentPurple,
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
            modifier = Modifier
                .size(18.dp)
                .clip(CircleShape)
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AiToolsModalSheet(onDismiss: () -> Unit, onSelectToolCommand: (String) -> Unit) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "VANIE AI Smart Utilities & Tools",
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                color = AccentCyan
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ToolCard(title = "Math Calculator", icon = Icons.Default.Calculate, onClick = { onSelectToolCommand("Calculate 125 * 8") }, modifier = Modifier.weight(1f))
                ToolCard(title = "Unit Converter", icon = Icons.Default.Transform, onClick = { onSelectToolCommand("Convert 10 km to miles") }, modifier = Modifier.weight(1f))
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ToolCard(title = "Riddles & Trivia", icon = Icons.Default.QuestionAnswer, onClick = { onSelectToolCommand("Give me a riddle") }, modifier = Modifier.weight(1f))
                ToolCard(title = "System Inspector", icon = Icons.Default.DeveloperBoard, onClick = { onSelectToolCommand("System specs") }, modifier = Modifier.weight(1f))
            }

            Button(onClick = onDismiss, modifier = Modifier.fillMaxWidth().height(48.dp), shape = RoundedCornerShape(14.dp)) {
                Text("Close Tools Drawer")
            }
        }
    }
}

@Composable
fun ToolCard(title: String, icon: androidx.compose.ui.graphics.vector.ImageVector, onClick: () -> Unit, modifier: Modifier = Modifier) {
    Card(
        onClick = onClick,
        modifier = modifier.height(90.dp),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(
            modifier = Modifier.fillMaxSize().padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(imageVector = icon, contentDescription = title, tint = AccentCyan)
            Text(text = title, fontWeight = FontWeight.Bold, fontSize = 13.sp)
        }
    }
}
