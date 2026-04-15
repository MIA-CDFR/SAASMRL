package com.example.dance4life_phone.domain.location

import android.content.Context
import android.location.Geocoder
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import com.dance4life.core.data.model.LocationData
import java.util.Locale

class LocationHelper(private val context: Context) {

    private val locationManager =
        context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

    fun startLocationUpdates(onLocation: (LocationData) -> Unit) {

        val listener = object : LocationListener {
            override fun onLocationChanged(location: Location) {

                val lat = location.latitude
                val lon = location.longitude

                var country: String? = null
                var city: String? = null
                var street: String? = null

                val geocoder = Geocoder(context, Locale.getDefault())

                try {
                    val addresses = geocoder.getFromLocation(lat, lon, 1)

                    if (!addresses.isNullOrEmpty()) {
                        val address = addresses[0]

                        street = address.thoroughfare
                        city = address.locality
                        country = address.countryName
                    }

                } catch (e: Exception) {
                    e.printStackTrace()
                }

                val locationData = LocationData(
                    latitude = lat,
                    longitude = lon,
                    country = country,
                    city = city,
                    street = street
                )

                onLocation(locationData)
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
}