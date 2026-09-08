import os

files = {
    ".github/workflows/build-apk.yml": """name: Build Android APK
on:
  push:
    branches: [ main, master ]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: android-actions/setup-android@v3
      - run: chmod +x gradlew
      - run: ./gradlew assembleDebug
      - run: mkdir -p .build-outputs && mkdir -p "APK DOWNLOAD"
      - run: cp app/build/outputs/apk/debug/app-debug.apk .build-outputs/app-debug.apk && cp app/build/outputs/apk/debug/app-debug.apk "APK DOWNLOAD/app-debug.apk"
      - uses: actions/upload-artifact@v4
        with:
          name: app-debug-apk
          path: |
            .build-outputs/app-debug.apk
            APK DOWNLOAD/app-debug.apk
""",
    "settings.gradle": """pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "TurniApp"
include ':app'
""",
    "build.gradle": """buildscript { repositories { google(); mavenCentral() } dependencies { classpath "com.android.tools.build:gradle:8.2.2"; classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22" } }
allprojects { repositories { google(); mavenCentral() } }
""",
    "app/build.gradle": """plugins { id 'com.android.application'; id 'org.jetbrains.kotlin.android' }
android {
    namespace 'com.example.turni'
    compileSdk 34
    defaultConfig { applicationId "com.example.turni"; minSdk 26; targetSdk 34; versionCode 1; versionName "1.0" }
    compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = '17' }
    buildFeatures { compose true }
    composeOptions { kotlinCompilerExtensionVersion '1.5.8' }
}
dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.2'
    implementation platform('androidx.compose:compose-bom:2023.10.01')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.ui:ui-graphics'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.documentfile:documentfile:1.0.1'
}
""",
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:allowBackup="true" android:label="Turni" android:theme="@android:style/Theme.Material.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",
    "app/src/main/java/com/example/turni/MainActivity.kt": """package com.example.turni

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class AppTheme(
    val name: String,
    val backgroundBrush: Brush,
    val cellBrush: Brush,
    val borderColor: Color,
    val neonAccent: Color
)

val DarkThemes = listOf(
    AppTheme("Nero Carbonio", Brush.verticalGradient(listOf(Color(0xFF181818), Color(0xFF090909))), Brush.verticalGradient(listOf(Color(0xFF2C2C2C), Color(0xFF1E1E1E))), Color(0xFF444444), Color(0xFF00E5FF)),
    AppTheme("Verde Smeraldo", Brush.verticalGradient(listOf(Color(0xFF0A1F18), Color(0xFF030D0A))), Brush.verticalGradient(listOf(Color(0xFF13382B), Color(0xFF0D261E))), Color(0xFF1DB954), Color(0xFF00FF66)),
    AppTheme("Cioccolato 3D", Brush.verticalGradient(listOf(Color(0xFF241611), Color(0xFF0D0806))), Brush.verticalGradient(listOf(Color(0xFF3D2720), Color(0xFF261914))), Color(0xFF8D5524), Color(0xFFFF9933)),
    AppTheme("Blu Oceano", Brush.verticalGradient(listOf(Color(0xFF0B192C), Color(0xFF02070D))), Brush.verticalGradient(listOf(Color(0xFF16325C), Color(0xFF0E223F))), Color(0xFF1E88E5), Color(0xFF00B0FF)),
    AppTheme("Turchese Caraibi", Brush.verticalGradient(listOf(Color(0xFF0B2529), Color(0xFF020B0C))), Brush.verticalGradient(listOf(Color(0xFF133E43), Color(0xFF0D292C))), Color(0xFF00ACC1), Color(0xFF18FFFF)),
    AppTheme("Marrone Profondo", Brush.verticalGradient(listOf(Color(0xFF281C1A), Color(0xFF0F0A0A))), Brush.verticalGradient(listOf(Color(0xFF422E2B), Color(0xFF2B1E1C))), Color(0xFFBCAAA4), Color(0xFFFF7043))
)

data class ShiftConfig(val name: String, val dailyPay: Double, val overtimePay: Double)
data class AssignedShift(val day: Int, val shiftName: String, val hours: Double)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TurniApp()
        }
    }
}

@Composable
fun TurniApp() {
    var currentTheme by remember { mutableStateOf(DarkThemes[0]) }
    var showThemeMenu by remember { mutableStateOf(false) }
    var selectedDayForShift by remember { mutableStateOf<Int?>(null) }
    
    val shiftTypes = remember { mutableStateOf(listOf(
        ShiftConfig("Mattina", 100.0, 15.0),
        ShiftConfig("Pomeriggio", 110.0, 16.0),
        ShiftConfig("Notte", 130.0, 20.0)
    )) }

    val assignedShifts = remember { mutableStateOf(mutableMapOf<Int, AssignedShift>()) }
    var selectedFolderUri = remember { mutableStateOf<Uri?>(null) }
    val context = androidx.compose.ui.platform.LocalContext.current

    val folderPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        if (uri != null) {
            context.contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )
            selectedFolderUri.value = uri
        }
    }

    val totalEarnings = assignedShifts.value.values.sumOf { shift ->
        val config = shiftTypes.value.find { it.name == shift.shiftName }
        if (config != null) config.dailyPay + (shift.hours * config.overtimePay) else 0.0
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(currentTheme.backgroundBrush)
    ) {
        Column(modifier = Modifier.fillMaxSize().padding(12.dp)) {
            
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Button(
                    onClick = { showThemeMenu = true },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                    modifier = Modifier.border(1.dp, currentTheme.borderColor, RoundedCornerShape(8.dp))
                ) {
                    Text("🎨 Temi 3D", color = Color.White)
                }

                Button(
                    onClick = { folderPickerLauncher.launch(null) },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                    modifier = Modifier.border(1.dp, currentTheme.borderColor, RoundedCornerShape(8.dp))
                ) {
                    Text("📁 Cartella", color = Color.White)
                }
            }

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp)
                    .shadow(8.dp, RoundedCornerShape(12.dp)),
                colors = CardDefaults.cardColors(containerColor = Color.Transparent)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(currentTheme.cellBrush)
                        .border(1.dp, currentTheme.borderColor, RoundedCornerShape(12.dp))
                        .padding(16.dp)
                ) {
                    Column {
                        Text("Saldo Mese Corrente", color = Color.LightGray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Totale: €%.2f".format(totalEarnings), color = currentTheme.neonAccent, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text("Calendario Turni", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
            Spacer(modifier = Modifier.height(8.dp))

            LazyVerticalGrid(
                columns = GridCells.Fixed(7),
                modifier = Modifier.fillMaxWidth().weight(1f),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                items(31) { index ->
                    val day = index + 1
                    val shift = assignedShifts.value[day]

                    Box(
                        modifier = Modifier
                            .aspectRatio(1f)
                            .shadow(6.dp, RoundedCornerShape(10.dp))
                            .background(currentTheme.cellBrush, RoundedCornerShape(10.dp))
                            .border(1.dp, currentTheme.borderColor, RoundedCornerShape(10.dp))
                            .clickable { selectedDayForShift = day },
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center,
                            modifier = Modifier.fillMaxSize().padding(4.dp)
                        ) {
                            Text("$day", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                            if (shift != null) {
                                Text(shift.shiftName, color = Color.LightGray, fontSize = 10.sp)
                            }
                        }
                        Box(
                            modifier = Modifier
                                .align(Alignment.BottomCenter)
                                .fillMaxWidth()
                                .height(4.dp)
                                .background(if (shift != null) currentTheme.neonAccent else Color.Transparent)
                        )
                    }
                }
            }
        }

        if (showThemeMenu) {
            AlertDialog(
                onDismissRequest = { showThemeMenu = false },
                title = { Text("Seleziona Tema 3D") },
                text = {
                    Column {
                        DarkThemes.forEach { theme ->
                            Button(
                                onClick = {
                                    currentTheme = theme
                                    showThemeMenu = false
                                },
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = Color.DarkGray)
                            ) {
                                Text(theme.name, color = Color.White)
                            }
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = { showThemeMenu = false }) { Text("Chiudi") }
                }
            )
        }

        if (selectedDayForShift != null) {
            val day = selectedDayForShift!!
            AlertDialog(
                onDismissRequest = { selectedDayForShift = null },
                title = { Text("Gestisci Giorno $day") },
                text = {
                    Column {
                        shiftTypes.value.forEach { config ->
                            Button(
                                onClick = {
                                    assignedShifts.value = assignedShifts.value.toMutableMap().apply {
                                        put(day, AssignedShift(day, config.name, 2.0))
                                    }
                                    selectedDayForShift = null
                                },
                                modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp)
                            ) {
                                Text("Assegna: ${config.name}")
                            }
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(
                            onClick = {
                                assignedShifts.value = assignedShifts.value.toMutableMap().apply {
                                    remove(day)
                                }
                                selectedDayForShift = null
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.Red),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Elimina Turno")
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = { selectedDayForShift = null }) { Text("Annulla") }
                }
            )
        }
    }
}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
print("Tutti i file corretti sono stati generati con successo!")
