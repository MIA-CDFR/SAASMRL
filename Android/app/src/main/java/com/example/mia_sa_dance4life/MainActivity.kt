package com.example.mia_sa_dance4life

import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.widget.TextView
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.location.Geocoder
import android.os.Handler
import android.os.Looper
import java.util.Locale
import android.util.Log
import android.widget.SeekBar
import android.widget.Toast
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

class MainActivity : AppCompatActivity(), SensorEventListener  {

    private lateinit var sensorManager: SensorManager
    //Accelarometro
    private var accelerometer: Sensor? = null
    private lateinit var acelarometro_x_value : TextView
    private lateinit var acelarometro_y_value : TextView
    private lateinit var acelarometro_z_value : TextView

    //Giroscopio
    private var gyroscope: Sensor? = null
    private lateinit var giroscopio_x_value: TextView
    private lateinit var giroscopio_y_value: TextView
    private lateinit var giroscopio_z_value: TextView

    //Localização
    private lateinit var locationManager: LocationManager
    private lateinit var latitude_value: TextView
    private lateinit var longitude_value: TextView

    private lateinit var country_value: TextView
    private lateinit var city_value: TextView
    private lateinit var street_value: TextView

    private var currentLat: Double = 0.0
    private var currentLon: Double = 0.0

    //HR
    private var heartRateSensor: Sensor? = null
    private lateinit var hrSeekBar: SeekBar
    private lateinit var hr_value: TextView
    private val accData = mutableListOf<Float>() //lista de valores acelerometro
    private val gyroData = mutableListOf<Float>() // lista de valores giroscopio
    private val hrData = mutableListOf<Int>() //lista de valores HR
    private var currentHR = 0 //vai receber o valor por defeito mais tarde
    private var sliderHR = 0


    private var lastAcc = 0.0
    private var lastGyro = 0.0

    //ID
    private lateinit var userId: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        userId = android.provider.Settings.Secure.getString(
            contentResolver,
            android.provider.Settings.Secure.ANDROID_ID
        )

        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager

        //Accelarometro
        acelarometro_x_value = findViewById(R.id.acelarometro_x_value)
        acelarometro_y_value = findViewById(R.id.acelarometro_y_value)
        acelarometro_z_value = findViewById(R.id.acelarometro_z_value)
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        //Giroscopio
        giroscopio_x_value = findViewById(R.id.giroscopio_x_value)
        giroscopio_y_value = findViewById(R.id.giroscopio_y_value)
        giroscopio_z_value = findViewById(R.id.giroscopio_z_value)
        gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)


        //localização
        latitude_value = findViewById(R.id.latitude_value)
        longitude_value = findViewById(R.id.longitude_value)
        country_value = findViewById(R.id.country_value)
        city_value = findViewById(R.id.city_value)
        street_value = findViewById(R.id.street_value)

        locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager

        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {

            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        } else {
            startLocationUpdates()
        }


        //HR
        hrSeekBar = findViewById(R.id.hr_seekbar)
        hr_value = findViewById(R.id.hr_value)

        val initialHR = hrSeekBar.progress.coerceAtLeast(40)
        currentHR = initialHR
        hrData.add(currentHR)
        hr_value.text = "HR: $initialHR bpm"
        sliderHR = initialHR
        hrSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val hr = progress.coerceAtLeast(40)
                hr_value.text = "HR: $hr bpm"
                sliderHR = hr
                currentHR = sliderHR
                hrData.add(currentHR)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })


        /*
        heartRateSensor = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)
        if (heartRateSensor == null) {
            Log.d("SENSOR_DEBUG", "Heart Rate sensor Não existe")
        } else {
            Log.d("SENSOR_DEBUG", "Heart Rate sensor Existe")
        }

        val sensors = sensorManager.getSensorList(Sensor.TYPE_ALL)

        for (sensor in sensors) {
            Log.d("SENSOR_LIST", sensor.name)
        }
        */
    }

    override fun onResume() {
        super.onResume()
        accelerometer?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }

        gyroscope?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }

        startLocationUpdates()

        heartRateSensor?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }

        iniciarRecolha()
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {
        /*
        if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) {
            acelarometro_x_value.text = event.values[0].toString()
            acelarometro_y_value.text = event.values[1].toString()
            acelarometro_z_value.text = event.values[2].toString()
        }
        */
        if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) {

            val x = event.values[0]
            val y = event.values[1]
            val z = event.values[2]

            lastAcc = kotlin.math.sqrt(x*x + y*y + z*z).toDouble()

            acelarometro_x_value.text = x.toString()
            acelarometro_y_value.text = y.toString()
            acelarometro_z_value.text = z.toString()

            accData.add(lastAcc.toFloat())
        }

        /*if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {
            giroscopio_x_value.text = event.values[0].toString()
            giroscopio_y_value.text = event.values[1].toString()
            giroscopio_z_value.text = event.values[2].toString()
        }*/

        if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {

            val gx = event.values[0]
            val gy = event.values[1]
            val gz = event.values[2]

            lastGyro = kotlin.math.sqrt(gx*gx + gy*gy + gz*gz).toDouble()

            giroscopio_x_value.text = gx.toString()
            giroscopio_y_value.text = gy.toString()
            giroscopio_z_value.text = gz.toString()

            gyroData.add(lastGyro.toFloat())
        }

        val autoHR = atualizarHRComMovimento(lastAcc, lastGyro)
        currentHR = combinarHR(autoHR, sliderHR)

        hr_value.text = "HR: $currentHR bpm"
        hrData.add(currentHR)

        hr_value.text = "HR: $currentHR bpm"

        if (event.sensor.type == Sensor.TYPE_HEART_RATE) {
            hr_value.text = "HR: ${event.values[0]}"
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

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

            startLocationUpdates()
        }
    }
    private fun startLocationUpdates() {

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                val lat = location.latitude
                val lon = location.longitude

                latitude_value.text = "Lat: $lat"
                longitude_value.text = "Lon: $lon"

                currentLat = location.latitude
                currentLon = location.longitude

                val geocoder = Geocoder(this@MainActivity, Locale.getDefault())

                try {
                    val addresses = geocoder.getFromLocation(lat, lon, 1)

                    if (!addresses.isNullOrEmpty()) {
                        val address = addresses[0]

                        val street = address.thoroughfare
                        val city = address.locality
                        val country = address.countryName

                        country_value.text = country
                        city_value.text = city
                        street_value.text = street
                    }

                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }

        try {
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                2000,
                1f,
                listener
            )
        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }

    //Calcula o ritmo
    private fun calcularRitmo() {

        val avgAcc = if (accData.isNotEmpty()) accData.average() else 0.0
        val avgGyro = if (gyroData.isNotEmpty()) gyroData.average() else 0.0
        val avgHR = if (hrData.isNotEmpty()) hrData.average() else 70.0

        val ritmo = avgAcc + avgGyro + (avgHR / 10)

        Toast.makeText(this, "Ritmo: $ritmo", Toast.LENGTH_LONG).show()

        enviarParaServidor(ritmo, avgAcc, avgGyro, avgHR)

        accData.clear()
        gyroData.clear()
        hrData.clear()
    }

    //recolha de dados
    private fun iniciarRecolha() {

        accData.clear()
        gyroData.clear()
        hrData.clear()

        Toast.makeText(this, "A recolher dados...", Toast.LENGTH_SHORT).show()

        Handler(Looper.getMainLooper()).postDelayed({

            calcularRitmo()

            // repetir automaticamente
            iniciarRecolha()

        }, 30000) // 10 segundos
    }

    /*private fun dataAtual(): String {
        val date = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault())
        return date.format(java.util.Date())
    }*/

    private fun enviarParaServidor(
        ritmo: Double,
        avgAcc: Double,
        avgGyro: Double,
        avgHR: Double
    ) {

        val client = okhttp3.OkHttpClient()

        val json = org.json.JSONObject()
        json.put("userId", userId)
        json.put("ritmo", ritmo)
        json.put("acc", avgAcc)
        json.put("gyro", avgGyro)
        json.put("hr", avgHR)

        json.put("latitude", currentLat)
        json.put("longitude", currentLon)

        json.put("timestamp", System.currentTimeMillis())

        val body = json.toString()
            .toRequestBody("application/json".toMediaType())

        val request = okhttp3.Request.Builder()
            .url("http://192.168.1.68:5000/MIA_SA_ASM_RL")
            .post(body)
            .build()

        Thread {
            try {
                val response = client.newCall(request).execute()
                println("Resposta: ${response.body?.string()}")
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun atualizarHRComMovimento(acc: Double, gyro: Double): Int {

        val movimento = acc + gyro

        var novoHR = 60 + (movimento * 2).toInt()

        // limites realistas
        if (novoHR < 60) novoHR = 60
        if (novoHR > 140) novoHR = 140

        return novoHR
    }

    private fun combinarHR(autoHR: Int, sliderHR: Int): Int {

        val finalHR = (0.7 * autoHR + 0.3 * sliderHR).toInt()

        return finalHR
    }
}