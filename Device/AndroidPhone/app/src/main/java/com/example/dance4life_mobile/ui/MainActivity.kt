package com.example.dance4life_mobile.ui

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
import com.example.dance4life_mobile.data.repository.DataRepository
import org.json.JSONArray
import com.example.dance4life_mobile.R
import com.example.dance4life_mobile.utils.Device
import com.example.dance4life_mobile.utils.LocationHelper
import com.example.dance4life_mobile.utils.RitmoCalculator
import com.example.dance4life_mobile.utils.SensorHelper

class MainActivity : AppCompatActivity()  {


    private val repository = DataRepository()

    private lateinit var locationHelper: LocationHelper

    private lateinit var sensorHelper: SensorHelper

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
    private lateinit var hrSeekBar: SeekBar
    private lateinit var hr_value: TextView
    private val accData = mutableListOf<Float>() //lista de valores acelerometro
    private val gyroData = mutableListOf<Float>() // lista de valores gyroscope
    private val hrData = mutableListOf<Int>() //lista de valores HR
    private var currentHR = 0 //vai receber o valor por defeito mais tarde
    private var sliderHR = 0

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

        //Get Android ID, to be used as user ID
        userId  = Device.getAndroidID(this)

        //Accelarometro
        accelerometer_x_value = findViewById(R.id.accelerometer_x_value)
        accelerometer_y_value = findViewById(R.id.accelerometer_y_value)
        accelerometer_z_value = findViewById(R.id.accelerometer_z_value)

        //Giroscopio
        gyroscope_x_value = findViewById(R.id.gyroscope_x_value)
        gyroscope_y_value = findViewById(R.id.gyroscope_y_value)
        gyroscope_z_value = findViewById(R.id.gyroscope_z_value)

        //localização
        latitude_value = findViewById(R.id.latitude_value)
        longitude_value = findViewById(R.id.longitude_value)
        country_value = findViewById(R.id.country_value)
        city_value = findViewById(R.id.city_value)
        street_value = findViewById(R.id.street_value)

        locationHelper = LocationHelper(this)

        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {

            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        } else {
            startLocation()
        }


        //HR
        hrSeekBar = findViewById(R.id.hr_seekbar)
        hr_value = findViewById(R.id.hr_value)


        sensorHelper = SensorHelper(this) { data ->

            accelerometer_x_value.text = data.accX.toString()
            accelerometer_y_value.text = data.accY.toString()
            accelerometer_z_value.text = data.accZ.toString()

            gyroscope_x_value.text = data.gyroX.toString()
            gyroscope_y_value.text = data.gyroY.toString()
            gyroscope_z_value.text = data.gyroZ.toString()

            if (accData.size > 100) accData.removeAt(0)

            accData.add(data.accMagnitude.toFloat())
            gyroData.add(data.gyroMagnitude.toFloat())
            hrData.add(data.heartRate)

            hr_value.text = "${data.heartRate} bpm"
        }

        val initialHR = hrSeekBar.progress.coerceAtLeast(40)
        currentHR = initialHR
        hrData.add(currentHR)
        hr_value.text = "$initialHR bpm"
        sliderHR = initialHR
        hrSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val hr = progress.coerceAtLeast(40)
                hr_value.text = "$hr bpm"
                sliderHR = hr
                currentHR = sliderHR
                hrData.add(currentHR)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        //mensagens do servidor
        handler = Handler(Looper.getMainLooper())

        runnable = object : Runnable {
            override fun run() {
                repository.obterUpdates(userId) { body ->

                    runOnUiThread {
                        if (!body.isNullOrEmpty()) {

                            val jsonArray = JSONArray(body)

                            if (jsonArray.length() == 0) return@runOnUiThread

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

        //handler.postDelayed(runnable, 5000)


        //calculo do ritmo
        dataHandler = Handler(Looper.getMainLooper())

        dataRunnable = object : Runnable {
            override fun run() {
                calcularRitmo()

                dataHandler.postDelayed(this, 10000) // repete
            }
        }
    }
    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(runnable)
    }

    override fun onResume() {
        super.onResume()

        sensorHelper.start()

        startLocation()

        handler.postDelayed(runnable, 5000)
        dataHandler.postDelayed(dataRunnable, 10000)
    }

    override fun onPause() {
        super.onPause()

        sensorHelper.stop()

        dataHandler.removeCallbacks(dataRunnable)
        handler.removeCallbacks(runnable)
    }

    //Localização
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {

            startLocation()
        }
    }
    private fun startLocation() {
        if (isLocationStarted) return

        isLocationStarted = true

        locationHelper.startLocationUpdates { location ->

            latitude_value.text = location.latitude.toString()
            longitude_value.text = location.longitude.toString()

            country_value.text = location.country
            city_value.text = location.city
            street_value.text = location.street

            currentLat = location.latitude
            currentLon = location.longitude
        }
    }

    //Calcula o ritmo
    private fun calcularRitmo() {

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
    }

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