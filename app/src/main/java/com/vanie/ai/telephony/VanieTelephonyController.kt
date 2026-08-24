package com.vanie.ai.telephony

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.ContactsContract
import android.telephony.SmsManager
import android.widget.Toast
import java.net.URLEncoder

class VanieTelephonyController(private val context: Context) {

    fun makeCall(contactNameOrNumber: String?) {
        if (contactNameOrNumber.isNull_or_blank()) {
            Toast.makeText(context, "Please specify a contact name or number", Toast.LENGTH_SHORT).show()
            return
        }

        val phoneNumber = resolvePhoneNumber(contactNameOrNumber!!) ?: contactNameOrNumber!!

        try {
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$phoneNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: SecurityException) {
            // Fallback to dialer if CALL_PHONE permission not granted
            val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:$phoneNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(dialIntent)
        } catch (e: Exception) {
            Toast.makeText(context, "Could not initiate call: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    fun sendSms(contactNameOrNumber: String?, messageText: String?) {
        if (contactNameOrNumber.isNull_or_blank()) {
            Toast.makeText(context, "Specify a recipient for SMS", Toast.LENGTH_SHORT).show()
            return
        }

        val phoneNumber = resolvePhoneNumber(contactNameOrNumber!!) ?: contactNameOrNumber!!
        val textToSend = messageText ?: "Hello from VANIE AI Assistant!"

        try {
            val smsManager = context.getSystemService(SmsManager::class.java)
            smsManager.sendTextMessage(phoneNumber, null, textToSend, null, null)
            Toast.makeText(context, "SMS sent to $contactNameOrNumber", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            // Fallback to system SMS App
            val intent = Intent(Intent.ACTION_SENDTO).apply {
                data = Uri.parse("smsto:$phoneNumber")
                putExtra("sms_body", textToSend)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        }
    }

    fun sendWhatsAppMessage(contactNameOrNumber: String?, messageText: String?) {
        if (contactNameOrNumber.isNull_or_blank()) {
            Toast.makeText(context, "Specify a WhatsApp contact name or number", Toast.LENGTH_SHORT).show()
            return
        }

        val rawNumber = resolvePhoneNumber(contactNameOrNumber!!) ?: contactNameOrNumber!!
        val cleanNumber = rawNumber.replace("[^0-9+]".toRegex(), "")
        val textToSend = messageText ?: "Hello from VANIE AI!"

        try {
            val encodedMsg = URLEncoder.encode(textToSend, "UTF-8")
            val url = "https://api.whatsapp.com/send?phone=$cleanNumber&text=$encodedMsg"
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse(url)
                setPackage("com.whatsapp")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback if WhatsApp is not installed or package check fails
            val genericIntent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse("https://api.whatsapp.com/send?phone=$cleanNumber&text=" + URLEncoder.encode(textToSend, "UTF-8"))
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(genericIntent)
        }
    }

    fun resolvePhoneNumber(nameQuery: String): String? {
        val contentResolver = context.contentResolver
        val cursor = contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Phone.NUMBER,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME
            ),
            "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?",
            arrayOf("%$nameQuery%"),
            null
        )

        cursor?.use {
            if (it.moveToFirst()) {
                val numberIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                if (numberIndex != -1) {
                    return it.getString(numberIndex)
                }
            }
        }
        return null
    }

    private fun String?.isNull_or_blank(): Boolean = this == null || this.trim().isEmpty()
}
