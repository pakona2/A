# CallMe

A mobile-first calling dashboard built with React, Vite, Firebase-ready configuration, and a Flask API scaffold.

## Run the front end

```bash
npm install
npm run dev
```

## Run the Flask API

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
gunicorn --chdir .. backend.app:app
```

The API exposes `GET /api/health`, `GET/POST /api/contacts`, `GET/POST /api/calls`, and `POST /api/calls/trigger`. The trigger endpoint places a real phone call through Twilio and requires `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER`. Phone numbers must be in E.164 format, such as `+14155552671`. It creates a local SQLite database and seeds the initial contacts on first launch. Set `CALLME_DATABASE`, `FRONTEND_ORIGIN`, `HOST`, and `PORT` in the environment for deployment.

For production calling, deploy the Flask API to a public HTTPS URL, configure Twilio credentials, and set `VITE_API_URL` to that API's `/api` URL before building the APK. Never put Twilio credentials in the React app or APK.

### Real phone calls

1. Create a Twilio account, buy or verify a phone number, and enable voice calling.
2. Set the three `TWILIO_*` variables from `.env.example` on the Flask server only.
3. Deploy the Flask API to a public HTTPS host. Twilio and the phone app must be able to reach that host.
4. Build the APK with `VITE_API_URL=https://your-api.example.com/api npm run mobile:build`.
5. Enter phone numbers in E.164 format, for example `+14155552671`.

The current trigger places a real outbound phone call to the entered number using Twilio. It does not use the phone's SIM directly. Twilio account verification, country permissions, billing, and caller-ID rules still apply.

For the frontend to call a deployed API, set `VITE_API_URL` to its `/api` URL before running `npm run build`.

## Android APK

CallMe is packaged with Capacitor. With Android Studio and its SDK installed, build the debug APK with:

```bash
npm run mobile:build
```

The build script automatically checks `ANDROID_HOME`, `ANDROID_SDK_ROOT`, common Android SDK locations, and the workspace container SDK. If your SDK is in a custom location, set `ANDROID_HOME=/path/to/android-sdk` before running the command.

The installable debug APK is generated at `android/app/build/outputs/apk/debug/app-debug.apk`. Install it on a connected Android device with:

```bash
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
```

This debug APK is suitable for device testing. A Play Store or public release requires a release keystore and signed bundle, which should be created with `npm run mobile:release` after configuring signing credentials in the Android project.