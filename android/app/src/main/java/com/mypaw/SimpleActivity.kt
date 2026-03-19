package com.mypaw

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

// 简化的数据类
data class SimpleMessage(val sender: String, val content: String, val timestamp: Long)
data class SimpleResponse(val status: String, val message: String)

// 简化的 API 接口
interface SimpleApiService {
    @POST("send")
    fun sendMessage(@Body message: SimpleMessage): Call<SimpleResponse>
}

class SimpleActivity : AppCompatActivity() {

    companion object {
        private const val REQUEST_RECORD_AUDIO_PERMISSION = 200
    }

    private var apiService: SimpleApiService? = null
    private lateinit var chatArea: TextView
    private lateinit var inputField: EditText
    private lateinit var serverUrlField: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            val sharedPrefs = getSharedPreferences("mypaw_prefs", MODE_PRIVATE)
            val savedUrl = sharedPrefs.getString("api_url", "http://192.168.3.1:8000/") ?: "http://192.168.3.1:8000/"

            // 创建主布局
            val mainLayout = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(16, 16, 16, 16)
                setBackgroundColor(Color.WHITE)
            }
            
            // 创建标题栏
            val titleBar = TextView(this).apply {
                text = "myPAW"
                textSize = 20f
                setTypeface(null, Typeface.BOLD)
                setTextColor(Color.BLACK)
                setPadding(0, 0, 0, 16)
                gravity = Gravity.CENTER
            }
            mainLayout.addView(titleBar)

            // 服务器配置区域
            val serverLayout = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                setPadding(0, 0, 0, 16)
            }

            serverUrlField = EditText(this).apply {
                hint = "服务器地址 (如 http://192.168.1.5:8000/)"
                setText(savedUrl)
                textSize = 14f
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            serverLayout.addView(serverUrlField)

            val updateButton = TextView(this).apply {
                text = "连接"
                textSize = 14f
                setPadding(12, 8, 12, 8)
                setTextColor(Color.WHITE)
                setBackgroundColor(Color.parseColor("#4CAF50"))
                setOnClickListener {
                    val newUrl = serverUrlField.text.toString().trim()
                    if (newUrl.isNotEmpty()) {
                        val formattedUrl = if (newUrl.endsWith("/")) newUrl else "$newUrl/"
                        sharedPrefs.edit().putString("api_url", formattedUrl).apply()
                        initApiService(formattedUrl)
                        Toast.makeText(this@SimpleActivity, "已更新并保存地址", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            serverLayout.addView(updateButton)
            mainLayout.addView(serverLayout)
            
            // 创建聊天消息区域
            chatArea = TextView(this).apply {
                text = "欢迎使用 myPAW!\n\n请输入指令并发送到桌面端"
                textSize = 16f
                setTextColor(Color.DKGRAY)
                setPadding(16, 16, 16, 16)
                setBackgroundResource(android.R.drawable.edit_text)
                minHeight = 200
            }
            mainLayout.addView(chatArea)
            
            // 创建输入区域
            val inputLayout = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                setPadding(0, 16, 0, 0)
            }
            
            inputField = EditText(this).apply {
                hint = "输入指令..."
                textSize = 16f
                layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            }
            inputLayout.addView(inputField)
            
            val sendButton = TextView(this).apply {
                text = "发送"
                setPadding(16, 16, 16, 16)
                setTextColor(Color.WHITE)
                setBackgroundColor(0xFF006491.toInt())
                setOnClickListener {
                    val content = inputField.text.toString().trim()
                    if (content.isNotEmpty()) {
                        inputField.text.clear()
                        sendMessage(content)
                    } else {
                        Toast.makeText(this@SimpleActivity, "请输入内容", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            inputLayout.addView(sendButton)
            
            mainLayout.addView(inputLayout)
            setContentView(mainLayout)
            
            Toast.makeText(this, "myPAW 已启动", Toast.LENGTH_SHORT).show()
            
            // 初始化 API 服务
            initApiService(savedUrl)
            
            // 检查权限
            if (!checkPermissions()) {
                requestPermissions()
            }
            
        } catch (e: Exception) {
            Toast.makeText(this, "启动失败: ${e.message}", Toast.LENGTH_LONG).show()
            e.printStackTrace()
        }
    }
    
    private fun sendMessage(content: String) {
        chatArea.text = "发送: $content\n(等待响应...)"
        
        val message = SimpleMessage(
            sender = "User",
            content = content,
            timestamp = System.currentTimeMillis()
        )
        
        apiService?.sendMessage(message)?.enqueue(object : Callback<SimpleResponse> {
            override fun onResponse(call: Call<SimpleResponse>, response: Response<SimpleResponse>) {
                if (response.isSuccessful) {
                    response.body()?.let {
                        if (it.status == "success") {
                            chatArea.text = "发送成功: $content\n\n回复:\n${it.message}"
                        } else {
                            chatArea.text = "发送失败: ${it.message}"
                        }
                    }
                } else {
                    chatArea.text = "网络错误: ${response.code()}"
                }
            }
            
            override fun onFailure(call: Call<SimpleResponse>, t: Throwable) {
                chatArea.text = "连接错误: ${t.message}\n\n请检查桌面端地址是否正确且已启动"
            }
        })
    }
    
    private fun initApiService(baseUrl: String) {
        try {
            // 创建支持长超时的 OkHttpClient
            val okHttpClient = OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS)
                .build()

            val retrofit = Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(okHttpClient) // 注入长超时配置
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            apiService = retrofit.create(SimpleApiService::class.java)
        } catch (e: Exception) {
            Toast.makeText(this, "API 初始化失败: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
    
    private fun checkPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            this, Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.RECORD_AUDIO),
            REQUEST_RECORD_AUDIO_PERMISSION
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            REQUEST_RECORD_AUDIO_PERMISSION -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "录音权限已授予", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}