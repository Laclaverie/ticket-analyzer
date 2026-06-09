# Mobile Android App

Capture and offline-first management of receipts.

## Tech Stack
- **Kotlin**
- **Jetpack Compose**
- **Room** (Persistence)
- **Retrofit** (Networking)

## Prerequisites
- Android Studio (Hedgehog or newer recommended).
- JDK 21.

## Building the App

To build the APK in debug mode:
```bash
./gradlew assembleDebug
```
The resulting APK will be located at `app/build/outputs/apk/debug/app-debug.apk`.

To build the release version:
```bash
./gradlew assembleRelease
```

## Running the App

1. **On a physical device or emulator**:
   Ensure your device is connected via ADB.
   ```bash
   ./gradlew installDebug
   ```

2. **Using Android Studio**:
   Open the `apps/mobile-android` directory as a project in Android Studio and click the "Run" button.

## Architecture
This app follows MVVM + Repository pattern. See `doc/ADR/ADR-013-mobile-app-architecture.md` for more details.

## Testing
- **Unit tests**: `./gradlew testDebugUnitTest`
- **Instrumented tests**: `./gradlew connectedDebugAndroidTest`
