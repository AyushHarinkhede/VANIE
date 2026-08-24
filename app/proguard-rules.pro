# ProGuard rules for VANIE Android App

# Chaquopy Python Rules
-keep class com.chaquo.python.** { *; }
-dontwarn com.chaquo.python.**

# Vosk Speech Recognition Rules
-keep class com.alphacephei.vosk.** { *; }
-dontwarn com.alphacephei.vosk.**

# Jetpack Compose Rules
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Gson Rules
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keep class com.google.gson.** { *; }
