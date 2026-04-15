package com.dance4life.core.data.telemetry

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [RlEventEntity::class, RlOutcomeEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class Dance4LifeDatabase : RoomDatabase() {
    abstract fun rlEventDao(): RlEventDao
    abstract fun rlOutcomeDao(): RlOutcomeDao

    companion object {
        @Volatile
        private var INSTANCE: Dance4LifeDatabase? = null

        fun getInstance(context: Context): Dance4LifeDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    Dance4LifeDatabase::class.java,
                    "dance4life_db",
                ).build().also { INSTANCE = it }
            }
        }
    }
}
