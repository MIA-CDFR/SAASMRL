/* While this template provides a good starting point for using Wear Compose, you can always
 * take a look at https://github.com/android/wear-os-samples/tree/main/ComposeStarter to find the
 * most up to date changes to the libraries and their usages.
 */

package com.dance4life.myapplication.presentation


import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.*
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.compose.runtime.*
import androidx.wear.compose.material.*

class MainActivity : ComponentActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var heartRateSensor: Sensor? = null

    private val REQUEST_CODE = 100

    private val heartRate = mutableStateOf("--")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        heartRateSensor = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)

        requestPermission()

        setContent {
            WearApp(heartRate.value)
        }
    }

    private fun requestPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BODY_SENSORS)
            != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.BODY_SENSORS),
                REQUEST_CODE
            )
        }
    }

    override fun onResume() {
        super.onResume()
        heartRateSensor?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type == Sensor.TYPE_HEART_RATE) {
            val bpm = event.values[0].toInt()
            heartRate.value = "$bpm BPM"
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}

@Composable
fun WearApp(heartRate: String) {
    MaterialTheme {
        Scaffold {
            Box(
                modifier = androidx.compose.ui.Modifier.fillMaxSize(),
                contentAlignment = androidx.compose.ui.Alignment.Center
            ) {
                Text(
                    text = heartRate,
                    style = MaterialTheme.typography.display1
                )
            }
        }
    }
}