#!/usr/bin/env bash
set -euo pipefail

BUILD_TYPE="${1:-debug}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

find_sdk() {
  local candidate
  for candidate in "${ANDROID_HOME:-}" "${ANDROID_SDK_ROOT:-}" "$ROOT_DIR/.android-sdk" "/tmp/callme-android-sdk" "$HOME/Android/Sdk" "/opt/android-sdk"; do
    if [[ -n "$candidate" && -d "$candidate/platforms" ]]; then
      printf '%s' "$candidate"
      return 0
    fi
  done
  return 1
}

if [[ -z "${JAVA_HOME:-}" && -d "/tmp/callme-jdk/jdk-21.0.12.1+1" ]]; then
  export JAVA_HOME="/tmp/callme-jdk/jdk-21.0.12.1+1"
fi

if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/java" ]]; then
  export PATH="$JAVA_HOME/bin:$PATH"
fi

if ! ANDROID_SDK_ROOT="$(find_sdk)"; then
  cat >&2 <<'EOF'
Android SDK not found.

Set ANDROID_HOME or ANDROID_SDK_ROOT to an installed SDK, or install Android
Studio and its SDK components. Then run `npm run mobile:build` again.
EOF
  exit 1
fi
export ANDROID_HOME="$ANDROID_SDK_ROOT"

echo "Using Android SDK: $ANDROID_SDK_ROOT"
if [[ -n "${JAVA_HOME:-}" ]]; then
  echo "Using Java: $JAVA_HOME"
fi

cd "$ROOT_DIR"
npm run mobile:sync
cd android
./gradlew "assemble${BUILD_TYPE^}"

APK_PATH="app/build/outputs/apk/${BUILD_TYPE}/app-${BUILD_TYPE}.apk"
echo "APK created: $ROOT_DIR/android/$APK_PATH"