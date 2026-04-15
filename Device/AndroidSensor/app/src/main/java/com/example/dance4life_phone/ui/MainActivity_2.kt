package com.example.dance4life_phone.ui

import android.Manifest
import android.content.pm.PackageManager
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

class MainActivity_2 : AppCompatActivity()  {


    private lateinit var sensorProvider: SensorProvider

    private val repository = DataRepository()

    private lateinit var locationProvider: LocationProvider

    private lateinit var deviceProvider: DeviceProvider

    private lateinit var controller: DanceController

    private val ritmoCalculator = RitmoCalculator()

    //Accelarometro
    private lateinit var accelerometer_x_value : TextView
    private lateinit var accelerometer_y_value : TextView
    private lateinit var accelerometer_z_value : TextView

    //Giroscopio
    private lateinit var gyroscope_x_value: TextView
    private lateinit var gyroscope_y_value: TextView
    private lateinit var gyroscope_z_value: TextView

    //Localização
    private var isLocationStarted = false
    private lateinit var latitude_value: TextView
    private lateinit var longitude_value: TextView

    private lateinit var country_value: TextView
    private lateinit var city_value: TextView
    private lateinit var street_value: TextView

    private var currentLat: Double = 0.0
    private var currentLon: Double = 0.0

    //HR

    private lateinit var hr_value: TextView
    /*
    private val accData = mutableListOf<Float>() //lista de valores acelerometro
    private val gyroData = mutableListOf<Float>() // lista de valores gyroscope
    private val hrData = mutableListOf<Int>() //lista de valores HR
    private var currentHR = 0 //vai receber o valor por defeito mais tarde
    private var sliderHR = 0
*/
    //ID
    private lateinit var userId: String

    //poling de mensagens
    private lateinit var handler: Handler
    private lateinit var runnable: Runnable

    private lateinit var dataHandler: Handler
    private lateinit var dataRunnable: Runnable

    private var accX = 0f
    private var accY = 0f
    private var accZ = 0f

    private var gyroX = 0f
    private var gyroY = 0f
    private var gyroZ = 0f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        // Providers
        deviceProvider = PhoneDeviceProvider(this)
        sensorProvider = PhoneSensorProvider(this)
        locationProvider = PhoneLocationProvider(this)

        // UI
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
            sensorProvider = sensorProvider,
            locationProvider = locationProvider,
            repository = DataRepository(),
            ritmoCalculator = RitmoCalculator(),
            deviceProvider = deviceProvider
        )

        // Sensor updates → UI
        controller.setSensorListener { data ->

            accelerometer_x_value.text = data.accX.toString()
            accelerometer_y_value.text = data.accY.toString()
            accelerometer_z_value.text = data.accZ.toString()

            gyroscope_x_value.text = data.gyroX.toString()
            gyroscope_y_value.text = data.gyroY.toString()
            gyroscope_z_value.text = data.gyroZ.toString()

            hr_value.text = "${data.heartRate} bpm"
        }

        controller.setLocationListener { location ->

            latitude_value.text = location.latitude.toString()
            longitude_value.text = location.longitude.toString()

            country_value.text = location.country
            city_value.text = location.city
            street_value.text = location.street
        }

        // Ritmo → UI
        controller.setRitmoListener { ritmo ->
            Toast.makeText(this, "Ritmo: $ritmo", Toast.LENGTH_LONG).show()
        }

        // HR slider (continua aqui)


        // Permissões (mantém)
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {

            requestPermissions(
                arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        }

        // Polling (podes manter como está para já)
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
        }

        // Ritmo timer
        dataHandler = Handler(Looper.getMainLooper())


        dataRunnable = object : Runnable {
            override fun run() {
               // controller.calcularRitmo()
                dataHandler.postDelayed(this, 10000)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(runnable)
    }

    override fun onResume() {
        super.onResume()

        controller.start()

        handler.postDelayed(runnable, 5000)
        dataHandler.postDelayed(dataRunnable, 10000)
    }

    override fun onPause() {
        super.onPause()

        controller.stop()

        dataHandler.removeCallbacks(dataRunnable)
        handler.removeCallbacks(runnable)
    }

    //Localização
    /*override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {

            //startLocation()
        }
    }*/

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == PackageManager.PERMISSION_GRANTED) {

            controller.start() // 👈 isto sim!
        }
    }
    /*private fun startLocation() {
        if (isLocationStarted) return

        isLocationStarted = true

        locationProvider.start { location ->

            latitude_value.text = location.latitude.toString()
            longitude_value.text = location.longitude.toString()

            country_value.text = location.country
            city_value.text = location.city
            street_value.text = location.street

            currentLat = location.latitude
            currentLon = location.longitude
        }
    }*/

    //Calcula o ritmo
    /*private fun calcularRitmo() {

        val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        Toast.makeText(this, "Ritmo: ${result.ritmo}", Toast.LENGTH_LONG).show()

        repository.enviarDados(
            userId,
            result.ritmo,
            result.avgAcc,
            result.avgGyro,
            result.avgHR,
            currentLat,
            currentLon
        )

        accData.clear()
        gyroData.clear()
        hrData.clear()
    }*/

    private fun showMatchDialog(user: String, score: Double) {
        val builder = AlertDialog.Builder(this)

        builder.setTitle("Novo Match!")
        builder.setMessage("Encontraste o $user!\nCompatibilidade: $score")

        builder.setPositiveButton("OK") { dialog, _ ->
            dialog.dismiss()
        }

        val dialog = builder.create()
        dialog.show()
    }
}