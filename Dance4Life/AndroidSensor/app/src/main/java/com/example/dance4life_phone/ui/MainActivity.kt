package com.example.dance4life_phone.ui

import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.widget.TextView
import android.os.Handler
import android.os.Looper
import android.widget.SeekBar
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.controller.DanceController
import org.json.JSONArray
import com.example.dance4life_phone.R


import com.dance4life.core.domain.sensor.SensorProvider
import com.dance4life.core.domain.location.LocationProvider
import com.dance4life.core.utils.RitmoCalculator
import com.dance4life.core.domain.device.DeviceProvider
import com.example.dance4life_phone.domain.device.PhoneDeviceProvider
import com.example.dance4life_phone.domain.location.PhoneLocationProvider
import com.example.dance4life_phone.domain.sensor.PhoneSensorProvider
import com.example.dance4life_phone.ui.notifier.InviteNotifier

import com.dance4life.core.rlinference.RlCoachPolicyFactory

class MainActivity : AppCompatActivity()  {

    private lateinit var sensorProvider: SensorProvider
    private lateinit var locationProvider: LocationProvider
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var controller: DanceController

    // UI
    private lateinit var accelerometer_x_value : TextView
    private lateinit var accelerometer_y_value : TextView
    private lateinit var accelerometer_z_value : TextView

    private lateinit var gyroscope_x_value: TextView
    private lateinit var gyroscope_y_value: TextView
    private lateinit var gyroscope_z_value: TextView

    private lateinit var latitude_value: TextView
    private lateinit var longitude_value: TextView
    private lateinit var country_value: TextView
    private lateinit var city_value: TextView
    private lateinit var street_value: TextView

    private lateinit var hr_value: TextView

    // polling matches
    private lateinit var handler: Handler
    private lateinit var runnable: Runnable



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "invite_channel",
                "Convites",
                NotificationManager.IMPORTANCE_HIGH
            )

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
        //-------------------------


        // Providers
        deviceProvider = PhoneDeviceProvider(this)
        sensorProvider = PhoneSensorProvider(this)
        locationProvider = PhoneLocationProvider(this)

        // UI binding
        accelerometer_x_value = findViewById(R.id.accelerometer_x_value)
        accelerometer_y_value = findViewById(R.id.accelerometer_y_value)
        accelerometer_z_value = findViewById(R.id.accelerometer_z_value)

        gyroscope_x_value = findViewById(R.id.gyroscope_x_value)
        gyroscope_y_value = findViewById(R.id.gyroscope_y_value)
        gyroscope_z_value = findViewById(R.id.gyroscope_z_value)

        latitude_value = findViewById(R.id.latitude_value)
        longitude_value = findViewById(R.id.longitude_value)
        country_value = findViewById(R.id.country_value)
        city_value = findViewById(R.id.city_value)
        street_value = findViewById(R.id.street_value)

        hr_value = findViewById(R.id.hr_value)

        // Controller
        controller = DanceController(
            sensorProvider,
            locationProvider,
            DataRepository(),
            RitmoCalculator(),
            deviceProvider,
            RlCoachPolicyFactory.create(this)
        )

        controller.setInviteListener { id, user ->
            InviteNotifier.show(this, id, user)
        }
        controller.setMatchListener { user, score ->
            showMatchDialog(user, score)
        }

        // 🔥 SENSOR → UI
        controller.setSensorListener { data ->
            accelerometer_x_value.text = data.accX.toString()
            accelerometer_y_value.text = data.accY.toString()
            accelerometer_z_value.text = data.accZ.toString()

            gyroscope_x_value.text = data.gyroX.toString()
            gyroscope_y_value.text = data.gyroY.toString()
            gyroscope_z_value.text = data.gyroZ.toString()

            hr_value.text = "${data.heartRate} bpm"
        }

        // 📍 LOCATION → UI
        controller.setLocationListener { location ->
            latitude_value.text = location.latitude.toString()
            longitude_value.text = location.longitude.toString()

            country_value.text = location.country
            city_value.text = location.city
            street_value.text = location.street
        }

        // 🎵 RITMO → UI
        controller.setRitmoListener { ritmo ->
            Toast.makeText(this, "Ritmo: $ritmo", Toast.LENGTH_SHORT).show()
        }

        controller.setMovementRecommendationListener { recommendation ->
            Toast.makeText(
                this,
                "${recommendation.title}\n${recommendation.encouragementMessage}",
                Toast.LENGTH_LONG
            ).show()
        }

        // Permissões
        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {

            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        }

        // polling matches
        /*
        handler = Handler(Looper.getMainLooper())
        runnable = object : Runnable {
            override fun run() {

                val userId = deviceProvider.getUserId()

                DataRepository().obterUpdates(userId) { body ->
                    runOnUiThread {
                        if (!body.isNullOrEmpty()) {
                            val jsonArray = JSONArray(body)

                            for (i in 0 until jsonArray.length()) {
                                val obj = jsonArray.getJSONObject(i)

                                if (obj.getString("type") == "match") {
                                    val user = obj.getString("user")
                                    val score = obj.getDouble("score")

                                    showMatchDialog(user, score)
                                }
                            }
                        }
                    }
                }

                handler.postDelayed(this, 5000)
            }
        }*/

        //Notificações
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != android.content.pm.PackageManager.PERMISSION_GRANTED) {

                requestPermissions(
                    arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),
                    200
                )
            }
        }
    }

    override fun onResume() {
        super.onResume()
        controller.start()
        //handler.postDelayed(runnable, 5000)
    }

    override fun onPause() {
        super.onPause()
        controller.stop()
        handler.removeCallbacks(runnable)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(runnable)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {

            controller.start()
        }
    }

    private fun showMatchDialog(user: String, score: Double) {
        AlertDialog.Builder(this)
            .setTitle("Novo Match!")
            .setMessage("Encontraste o $user!\nCompatibilidade: $score")
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()
    }
}