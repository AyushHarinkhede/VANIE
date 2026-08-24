# 🤖 VANIE - Virtual Agent of Neural Integrated Engine

![VANIE Banner](app/src/main/res/drawable/vanie.png)

> **Blazing-Fast, 100% Offline On-Device AI Voice Assistant & System Controller for Android**  
> *Scrapped legacy HTML web app; re-architected completely in Native Kotlin, Jetpack Compose (Material You + Glassmorphism), and Chaquopy embedded Python 3.11 engine.*

---

## 👨‍💻 Developer & Project Credits

- **Developer & Architect**: **Ayush Harinkhede**
- **📧 Email**: [ayushharinkhere2005@gmail.com](mailto:ayushharinkhere2005@gmail.com)
- **💻 GitHub**: [github.com/AyushHarinkhede](https://github.com/AyushHarinkhede)
- **📌 Project Repository**: [AyushHarinkhede/VANIE](https://github.com/AyushHarinkhede/VANIE)
- **🏷️ Version**: `3.0-ENHANCED` (Native Android Kotlin Edition)

---

## 🚀 Key Features

### ⚡ 1. On-Device Zero-Latency NPU/TPU Execution
- **100% Offline Processing**: Sub-5ms intent classification and response generation with **zero network requests**.
- **Chaquopy Python Engine**: Embedded Python 3.11 runs directly inside the Android APK via JNI/Java bridge on background `Dispatchers.IO` coroutines.
- **120Hz/144Hz Butter-Smooth UI**: 0ms UI main thread locking for high refresh rate displays.

### 🎙️ 2. Voice Wake Word & Privacy Controls
- **Wake Word Detection**: Background listener for *"Hey VANIE"* and *"Hello VANIE"*.
- **Battery-Saving Voice Toggle**: Turn background wake-word listening ON/OFF in Settings to eliminate 24/7 mic battery drain and protect user privacy.
- **Dynamic Pulsing Visualizer**: Modal Bottom Sheet overlay with pulsing neon aura synced to voice RMS decibels.

### 📱 3. Hardware & System Controls
- **Torch / Flashlight**: Instant camera flash hardware toggle.
- **Wi-Fi & Bluetooth**: One-tap panel controls.
- **Audio Profiles**: Switch between Ring, Vibrate, Silent, and Do Not Disturb (DND) modes.
- **Screen Brightness**: Live interactive slider controlling `Settings.System.SCREEN_BRIGHTNESS` (0%–100%).
- **App Launcher**: Instant voice app launcher ("Open YouTube", "Open WhatsApp", "Open Camera", "Open Chrome").
- **Alarms & Timers**: Native `AlarmClock` triggers.
- **Battery Inspector**: Live battery percentage and charging state lookup.

### 📞 4. Telephony, SMS & Hands-Free WhatsApp Automation
- **Direct Calling**: *"Call [Contact Name]"* resolves contacts via `ContactsContract` and places direct calls.
- **Incoming Call Caller ID & Voice Pickup/Cut**: Speaks caller name out loud (*"Incoming call from [Name]"*) and listens for *"Hey VANIE Pickup call"* or *"Cut call"*.
- **Hands-Free WhatsApp Automation**: Uses Android `AccessibilityService` (`VanieAccessibilityService`) to automate recipient search, message entry, and dispatch in WhatsApp.
- **Notification Reader**: Reads unread app notifications out loud via `NotificationListenerService`.

### 🎨 5. Glassmorphism + Material You (M3) UI Design
- **Single Unified Home Screen**: Clean chat and voice assistant interface.
- **Top App Bar**: Pulsing VANIE logo, title, and action icons (Setup 🛡️, Settings ⚙️, More Options ⋮).
- **Live System Status Bar**: Top bar chip showing NPU Status, Battery %, and Audio Mode.
- **Message Action Buttons**: Every VANIE response bubble features **Copy Text (📋)** and **Speak Out Loud (🔊)** buttons.
- **AI Tools Drawer**: Quick access tool sheet (Math Calculator, Unit Converter, Riddles & Trivia, System Specs).
- **Categorized Command Carousel**: Categorized command chips (⚡ Hardware, 📞 Telecom, ⏰ Productivity, 🧠 AI Fun).

---

## ⚙️ Tech Stack & Architecture

| Layer | Technology |
| :--- | :--- |
| **Language** | Kotlin 1.9+, Java 17 |
| **UI Framework** | Jetpack Compose (Material 3 / Monet Dynamic Colors) |
| **Embedded AI Engine** | Chaquopy (Python 3.11 inside APK JNI bridge) |
| **Offline Speech Engine** | Vosk Android STT SDK + Android Native Offline TTS |
| **Automation Services** | `AccessibilityService` (WhatsApp) & `NotificationListenerService` |
| **Hardware APIs** | `CameraManager`, `AudioManager`, `TelecomManager`, `BatteryManager`, `SmsManager` |
| **Async Architecture** | Kotlin Coroutines (`Dispatchers.IO`, `Dispatchers.Main`), Flow |

---

## 📁 Repository & Project Structure

```
VANIE/
├── build.gradle.kts (Root with Chaquopy Plugin)
├── settings.gradle.kts
├── sync_dataset.py
├── VANIE.py
├── VANIE_ENHANCED.py
└── app/
    ├── build.gradle.kts (App level)
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── assets/
        │   └── vanie_dataset.json
        ├── python/
        │   └── VANIE_ENHANCED.py (Native Chaquopy Brain)
        ├── res/
        │   ├── drawable/vanie.png
        │   ├── values/strings.xml & themes.xml
        │   └── xml/accessibility_service_config.xml
        └── java/com/vanie/ai/
            ├── MainActivity.kt (App Orchestrator & Top Bar Popup Sheets)
            ├── accessibility/
            │   └── VanieAccessibilityService.kt (WhatsApp Automation)
            ├── control/
            │   └── VanieDeviceController.kt (Torch, Brightness, Alarms, Battery, Apps)
            ├── nlp/
            │   └── VanieNlpEngine.kt (Intent Engine & Action Commands)
            ├── notification/
            │   └── VanieNotificationService.kt (Notification Reader)
            ├── python/
            │   └── VaniePythonBridge.kt (Chaquopy JNI Bridge)
            ├── receiver/
            │   └── VanieCallReceiver.kt (Caller ID & Voice Call Pickup/Cut)
            ├── service/
            │   └── VanieVoiceService.kt (Offline "Hey VANIE" Wake Word Service)
            ├── telephony/
            │   └── VanieTelephonyController.kt (Direct Calling & SMS)
            └── ui/
                ├── components/
                │   └── VanieVoiceOverlay.kt (Pulsing Logo Visualizer Sheet)
                ├── screens/
                │   ├── ChatScreen.kt (Glassmorphic Chat & AI Tools Drawer)
                │   ├── DashboardScreen.kt (Control Center)
                │   └── PermissionsScreen.kt (Setup Guide)
                └── theme/
                    ├── Color.kt
                    ├── Theme.kt
                    └── Type.kt
```

---

## 🛠️ How to Build APK in Android Studio

1. **Clone Repository**:
   ```bash
   git clone https://github.com/AyushHarinkhede/VANIE.git
   ```
2. **Open in Android Studio**: Open the root `VANIE` project folder in Android Studio (Hedgehog / Iguana or later).
3. **Gradle Sync**: Allow Android Studio to sync Gradle and download Chaquopy dependencies.
4. **Build APK**:
   - Menu: **Build ➔ Build Bundle(s) / APK(s) ➔ Build APK(s)**
   - Generated APK Path: `app/build/outputs/apk/debug/app-debug.apk`

---

## 📜 License & Copyright

Developed by **Ayush Harinkhede** © 2026. All rights reserved.  
*Virtual Agent of Neural Integrated Engine (VANIE).*
