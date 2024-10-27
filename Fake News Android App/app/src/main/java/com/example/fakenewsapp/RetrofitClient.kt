package com.example.fakenewsapp

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    private const val BASE_URL = "CLOUD-IP" // Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    fun create(): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

