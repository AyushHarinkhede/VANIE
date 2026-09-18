package com.vanie.ai.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.speech.tts.TextToSpeech
import android.telecom.TelecomManager
import android.telephony.TelephonyManager
import android.util.Log
import com.vanie.ai.telephony.VanieTelephonyController
import java.util.Locale

class VanieCallReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "VanieCallReceiver"
        private var tts: TextToSpeech? = null
    }

    override fun onReceive(context: Context, intent: Intent) {
        try {
            if (intent.action == TelephonyManager.ACTION_PHONE_STATE_CHANGED) {
                val state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
                @Suppress("DEPRECATION")
                val incomingNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)

                if (state == TelephonyManager.EXTRA_STATE_RINGING) {
                    Log.d(TAG, "Incoming call ringing: $incomingNumber")
                    val telephonyController = VanieTelephonyController(context)
                    val contactName = if (!incomingNumber.isNullOrBlank()) {
                        telephonyController.resolvePhoneNumber(incomingNumber) ?: incomingNumber
                    } else {
                        "Unknown Caller"
                    }

                    announceCaller(context, contactName)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error processing phone state broadcast: ${e.message}", e)
        }
    }

    private fun announceCaller(context: Context, callerName: String) {
        try {
            tts = TextToSpeech(context.applicationContext) { status ->
                if (status == TextToSpeech.SUCCESS) {
                    try {
                        tts?.language = Locale.US
                        val announcement = com.vanie.ai.util.VanieTtsUtils.cleanTextForTts("Incoming call from $callerName. Say Hey VANIE Pickup call or Cut call.")
                        tts?.speak(announcement, TextToSpeech.QUEUE_FLUSH, null, "CALL_ID")
                    } catch (e: Exception) {
                        Log.e(TAG, "TTS speak error: ${e.message}", e)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "TTS creation error: ${e.message}", e)
        }
    }

    fun answerCall(context: Context): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            return try {
                @Suppress("DEPRECATION")
                telecomManager?.acceptRingingCall()
                true
            } catch (e: SecurityException) {
                Log.e(TAG, "Permission required to accept ringing call: ${e.message}")
                false
            } catch (e: Exception) {
                Log.e(TAG, "Error accepting ringing call: ${e.message}")
                false
            }
        }
        return false
    }

    fun cutCall(context: Context): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            return try {
                telecomManager?.endCall() ?: false
            } catch (e: SecurityException) {
                Log.e(TAG, "Permission required to end call: ${e.message}")
                false
            } catch (e: Exception) {
                Log.e(TAG, "Error ending call: ${e.message}")
                false
            }
        }
        return false
    }
}
