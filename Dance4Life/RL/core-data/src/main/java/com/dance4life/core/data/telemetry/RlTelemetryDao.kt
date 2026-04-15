package com.dance4life.core.data.telemetry

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Dao
interface RlEventDao {
    @Insert
    suspend fun insert(event: RlEventEntity): Long

    @Query("SELECT * FROM rl_events WHERE synced = 0 LIMIT 100")
    suspend fun getUnsynced(): List<RlEventEntity>

    @Query("UPDATE rl_events SET synced = 1, syncedAtMs = :ts WHERE id IN (:ids)")
    suspend fun markSynced(ids: List<Long>, ts: Long)

    @Query("SELECT COUNT(*) FROM rl_events WHERE synced = 0")
    suspend fun unsyncedCount(): Int
}

@Dao
interface RlOutcomeDao {
    @Insert
    suspend fun insert(outcome: RlOutcomeEntity): Long

    @Query("SELECT * FROM rl_outcomes WHERE synced = 0 LIMIT 100")
    suspend fun getUnsynced(): List<RlOutcomeEntity>

    @Query("UPDATE rl_outcomes SET synced = 1, syncedAtMs = :ts WHERE id IN (:ids)")
    suspend fun markSynced(ids: List<Long>, ts: Long)

    @Query("SELECT COUNT(*) FROM rl_outcomes WHERE synced = 0")
    suspend fun unsyncedCount(): Int
}
