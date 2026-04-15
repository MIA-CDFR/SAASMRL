package com.dance4life.wear.domain.location

import android.content.Context
import android.location.*
import com.dance4life.core.data.model.LocationData
import java.util.Locale
import kotlinx.coroutines.*
import android.location.*
import android.os.Build


class LocationHelper(private val context: Context) {

    private val locationManager =
        context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

    private var lastGeocodeTime = 0L

    private var lastCountry: String? = null
    private var lastCity: String? = null
    private var lastStreet: String? = null

    private val geocodeInterval = 60000L // 60 segundos

    //private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun startLocationUpdates(onLocation: (LocationData) -> Unit) {

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {

                val lat = location.latitude
                val lon = location.longitude

                val now = System.currentTimeMillis()

                if (now - lastGeocodeTime > geocodeInterval) {
                    lastGeocodeTime = now

                    try {
                        val geocoder = Geocoder(context, Locale.getDefault())

                        /*
                        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {

                            // ✅ API 33+
                            geocoder.getFromLocation(lat, lon, 1) { addresses ->

                                if (!addresses.isNullOrEmpty()) {
                                    val address = addresses[0]

                                    lastStreet = address.thoroughfare
                                    lastCity = address.locality ?: "Desconhecido"
                                    lastCountry = address.countryName
                                }
                            }

                        } else {

                            // ⚠️ API < 33 (deprecated mas necessário)
                            @Suppress("DEPRECATION")
                            val addresses = geocoder.getFromLocation(lat, lon, 1)

                            if (!addresses.isNullOrEmpty()) {
                                val address = addresses[0]

                                lastStreet = address.thoroughfare
                                lastCity = address.locality ?: "Desconhecido"
                                lastCountry = address.countryName
                            }
                        }*/
                        if (Geocoder.isPresent()) {

                            val geocoder = Geocoder(context, Locale.getDefault())

                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {

                                geocoder.getFromLocation(lat, lon, 1) { addresses ->

                                    if (!addresses.isNullOrEmpty()) {
                                        val address = addresses[0]

                                        lastStreet = address.thoroughfare ?: address.featureName
                                        lastCity = address.locality ?: "Desconhecido"
                                        lastCountry = address.countryName
                                    }

                                    onLocation(
                                        LocationData(
                                            latitude = lat,
                                            longitude = lon,
                                            country = lastCountry,
                                            city = lastCity,
                                            street = lastStreet
                                        )
                                    )
                                }

                            } else {
                                val addresses = geocoder.getFromLocation(lat, lon, 1)

                                if (!addresses.isNullOrEmpty()) {
                                    val address = addresses[0]

                                    lastStreet = address.thoroughfare ?: address.featureName
                                    lastCity = address.locality ?: "Desconhecido"
                                    lastCountry = address.countryName
                                }

                                onLocation(
                                    LocationData(lat, lon, lastCountry, lastCity, lastStreet)
                                )
                            }

                        } else {
                            // fallback sem geocoder
                            onLocation(
                                LocationData(lat, lon, null, null, null)
                            )
                        }

                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }

                val locationData = LocationData(
                    latitude = lat,
                    longitude = lon,
                    country = lastCountry,
                    city = lastCity,
                    street = lastStreet
                )

                onLocation(locationData)
            }
        }

        try {
            val provider = if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                LocationManager.GPS_PROVIDER
            } else {
                LocationManager.NETWORK_PROVIDER
            }

            locationManager.requestLocationUpdates(
                provider,
                10000L,
                5f,
                listener
            )

        } catch (e: SecurityException) {
            e.printStackTrace()
        }
    }
}