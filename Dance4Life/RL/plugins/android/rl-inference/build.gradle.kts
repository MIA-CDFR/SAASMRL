plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.dance4life.plugins.rlinference"
    compileSdk = 35

    defaultConfig {
        minSdk = 26
        consumerProguardFiles("consumer-rules.pro")
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation(project(":libs:core-domain"))
    implementation("com.microsoft.onnxruntime:onnxruntime-android:1.22.0")
}
