package com.vanie.ai

import android.app.Application
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class VanieApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        initChaquopy()
    }

    private fun initChaquopy() {
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
            }
            Log.d(TAG, "Chaquopy Python engine initialized successfully in Application.")
        } catch (e: Throwable) {
            Log.e(TAG, "Chaquopy initialization exception: ${e.message}", e)
        }
    }

    companion object {
        private const val TAG = "VanieApplication"
    }
}
