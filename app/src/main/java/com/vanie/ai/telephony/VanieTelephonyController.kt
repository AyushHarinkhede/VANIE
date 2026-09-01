package com.vanie.ai.telephony

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.ContactsContract
import android.telephony.SmsManager
import android.widget.Toast
import java.net.URLEncoder

data class ResolvedContact(
    val id: String,
    val name: String,
    val number: String
)

sealed class ContactResolutionResult {
    data class SingleMatch(val contact: ResolvedContact) : ContactResolutionResult()
    data class MultipleMatches(val query: String, val matches: List<ResolvedContact>) : ContactResolutionResult()
    object NoMatch : ContactResolutionResult()
}

data class PendingMessageDraft(
    val contactName: String,
    val number: String,
    val messageText: String,
    val isWhatsApp: Boolean
)

class VanieTelephonyController(private val context: Context) {

    var pendingDraft: PendingMessageDraft? = null

    /**
     * Precision Smart Contact Resolver Engine:
     * 1. Exact Name Matching: "Ayush" matches exact contact "Ayush" over "Ayush Sharma" / "Ayush Gupta".
     * 2. Full Name Matching: "Ayush Gupta" matches specific "Ayush Gupta".
     * 3. Disambiguation: "Sharma" returns MultipleMatches if multiple contacts match.
     */
    fun resolveContactPrecision(query: String): ContactResolutionResult {
        val cleanQuery = query.trim().lowercase()
        if (cleanQuery.isBlank()) return ContactResolutionResult.NoMatch

        val contentResolver = context.contentResolver
        val cursor = contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER
            ),
            "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?",
            arrayOf("%$query%"),
            null
        )

        val contactsList = mutableListOf<ResolvedContact>()
        cursor?.use {
            val idIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
            val nameIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val numberIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)

            while (it.moveToNext()) {
                val id = if (idIndex != -1) it.getString(idIndex) else ""
                val name = if (nameIndex != -1) it.getString(nameIndex) ?: "" else ""
                val number = if (numberIndex != -1) it.getString(numberIndex) ?: "" else ""
                if (name.isNotBlank() && number.isNotBlank()) {
                    if (contactsList.none { c -> c.name.equals(name, ignoreCase = true) && c.number == number }) {
                        contactsList.add(ResolvedContact(id, name, number))
                    }
                }
            }
        }

        if (contactsList.isEmpty()) {
            return ContactResolutionResult.NoMatch
        }

        // Rule 1: Prioritize EXACT Name Match (e.g. "Ayush" vs "Ayush Sharma" / "Ayush Gupta")
        val exactMatch = contactsList.firstOrNull { it.name.equals(query.trim(), ignoreCase = true) }
        if (exactMatch != null) {
            return ContactResolutionResult.SingleMatch(exactMatch)
        }

        // Rule 2: Single partial match
        if (contactsList.size == 1) {
            return ContactResolutionResult.SingleMatch(contactsList[0])
        }

        // Rule 3: Multiple matches exist (e.g. "Sharma" matching "Ayush Sharma" & "Jay Sharma")
        return ContactResolutionResult.MultipleMatches(query, contactsList)
    }

    fun makeCall(contactNameOrNumber: String?): String {
        if (contactNameOrNumber.isNullOrBlank()) {
            return "Please specify a contact name or number to call."
        }

        val query = contactNameOrNumber!!.trim()
        val result = resolveContactPrecision(query)

        return when (result) {
            is ContactResolutionResult.SingleMatch -> {
                val contact = result.contact
                initiateCellularCall(contact.number)
                "Calling ${contact.name} (${contact.number})..."
            }
            is ContactResolutionResult.MultipleMatches -> {
                val matchNames = result.matches.mapIndexed { i, c -> "${i + 1}. ${c.name}" }.joinToString(", ")
                "Multiple contacts found for '$query': $matchNames. Please specify full name."
            }
            is ContactResolutionResult.NoMatch -> {
                if (query.matches(Regex("^[+0-9\\s\\-]+$"))) {
                    initiateCellularCall(query)
                    "Calling $query..."
                } else {
                    "No contact found for '$query'."
                }
            }
        }
    }

    fun makeWhatsAppCall(contactNameOrNumber: String?): String {
        if (contactNameOrNumber.isNullOrBlank()) {
            return "Please specify a contact name or number for WhatsApp call."
        }

        val query = contactNameOrNumber!!.trim()
        val result = resolveContactPrecision(query)

        return when (result) {
            is ContactResolutionResult.SingleMatch -> {
                val contact = result.contact
                val cleanNumber = contact.number.replace("[^0-9+]".toRegex(), "")
                try {
                    val url = "https://api.whatsapp.com/send?phone=$cleanNumber"
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        data = Uri.parse(url)
                        setPackage("com.whatsapp")
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    }
                    context.startActivity(intent)
                    "Opening WhatsApp call for ${contact.name}..."
                } catch (e: Exception) {
                    "Could not start WhatsApp call for ${contact.name}."
                }
            }
            is ContactResolutionResult.MultipleMatches -> {
                val matchNames = result.matches.mapIndexed { i, c -> "${i + 1}. ${c.name}" }.joinToString(", ")
                "Multiple contacts found for WhatsApp call '$query': $matchNames. Please specify full name."
            }
            is ContactResolutionResult.NoMatch -> {
                "No contact found for WhatsApp call '$query'."
            }
        }
    }

    fun prepareWhatsAppDraft(contactNameOrNumber: String?, messageText: String?): String {
        if (contactNameOrNumber.isNullOrBlank()) {
            return "Please specify a recipient for the WhatsApp message."
        }

        val query = contactNameOrNumber!!.trim()
        val body = messageText ?: "Hello from VANIE AI!"
        val result = resolveContactPrecision(query)

        return when (result) {
            is ContactResolutionResult.SingleMatch -> {
                val contact = result.contact
                pendingDraft = PendingMessageDraft(contact.name, contact.number, body, isWhatsApp = true)
                "Drafted WhatsApp message for ${contact.name}: '$body'. Say 'Send it' or 'Bhej do' to confirm!"
            }
            is ContactResolutionResult.MultipleMatches -> {
                val matchNames = result.matches.mapIndexed { i, c -> "${i + 1}. ${c.name}" }.joinToString(", ")
                "Multiple contacts found for '$query': $matchNames. Specify exact contact name to draft message."
            }
            is ContactResolutionResult.NoMatch -> {
                pendingDraft = PendingMessageDraft(query, query, body, isWhatsApp = true)
                "Drafted message for $query: '$body'. Say 'Send it' or 'Bhej do' to confirm!"
            }
        }
    }

    fun confirmAndSendPendingDraft(): String {
        val draft = pendingDraft
        if (draft == null) {
            return "No pending draft message to send."
        }

        return try {
            val cleanNumber = draft.number.replace("[^0-9+]".toRegex(), "")
            val encodedMsg = URLEncoder.encode(draft.messageText, "UTF-8")
            val url = "https://api.whatsapp.com/send?phone=$cleanNumber&text=$encodedMsg"
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse(url)
                setPackage("com.whatsapp")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            pendingDraft = null
            "Sent message to ${draft.contactName} on WhatsApp!"
        } catch (e: Exception) {
            pendingDraft = null
            "Could not send WhatsApp message: ${e.message}"
        }
    }

    private fun initiateCellularCall(phoneNumber: String) {
        val cleanNumber = phoneNumber.replace("[^0-9+]".toRegex(), "")
        try {
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$cleanNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: SecurityException) {
            val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:$cleanNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(dialIntent)
        }
    }

    fun sendSms(contactNameOrNumber: String?, messageText: String?) {
        if (contactNameOrNumber.isNullOrBlank()) {
            Toast.makeText(context, "Specify a recipient for SMS", Toast.LENGTH_SHORT).show()
            return
        }

        val query = contactNameOrNumber!!.trim()
        val textToSend = messageText ?: "Hello from VANIE AI Assistant!"
        val result = resolveContactPrecision(query)
        val phoneNumber = when (result) {
            is ContactResolutionResult.SingleMatch -> result.contact.number
            else -> query
        }

        try {
            val smsManager = context.getSystemService(SmsManager::class.java)
            smsManager.sendTextMessage(phoneNumber, null, textToSend, null, null)
            Toast.makeText(context, "SMS sent to $query", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            val intent = Intent(Intent.ACTION_SENDTO).apply {
                data = Uri.parse("smsto:$phoneNumber")
                putExtra("sms_body", textToSend)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        }
    }

    fun sendWhatsAppMessage(contactNameOrNumber: String?, messageText: String?) {
        prepareWhatsAppDraft(contactNameOrNumber, messageText)
    }
}

