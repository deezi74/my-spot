#!/usr/bin/env bash
set -euo pipefail
sdk="${ANDROID_HOME:?Android SDK required}"
platform="$(find "$sdk/platforms" -maxdepth 1 -name 'android-[0-9]*' | grep -E '/android-[0-9]+$' | sort -V | tail -1)"
build="$(find "$sdk/build-tools" -maxdepth 1 -mindepth 1 -type d | grep -E '/[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)"
mkdir -p out/classes out/dex out/res/drawable
cp large.png out/res/drawable/icon.png
cat >out/AndroidManifest.xml <<'XML'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.deezi.myspot" android:versionCode="1" android:versionName="1.0-beta">
<uses-sdk android:minSdkVersion="24" android:targetSdkVersion="35"/>
<application android:label="MySpot" android:icon="@drawable/icon" android:allowBackup="false">
<activity android:name=".MainActivity" android:exported="true"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity>
</application></manifest>
XML
cat >out/MainActivity.java <<'JAVA'
package com.deezi.myspot;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
public final class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://myspot-deezi-beta.deezi.chatgpt.site")));
        finish();
    }
}
JAVA
javac -source 8 -target 8 -classpath "$platform/android.jar" -d out/classes out/MainActivity.java
"$build/d8" --min-api 24 --lib "$platform/android.jar" --output out/dex out/classes/com/deezi/myspot/MainActivity.class
"$build/aapt2" compile --dir out/res -o out/resources.zip
"$build/aapt2" link -o out/base.apk -I "$platform/android.jar" --manifest out/AndroidManifest.xml out/resources.zip
(cd out/dex && zip -q ../base.apk classes.dex)
"$build/zipalign" -f 4 out/base.apk out/aligned.apk
keytool -genkeypair -alias beta -keystore out/beta.p12 -storepass localbeta -keypass localbeta -keyalg RSA -keysize 2048 -validity 365 -dname CN=MySpot
"$build/apksigner" sign --ks out/beta.p12 --ks-pass pass:localbeta --out out/MySpot.apk out/aligned.apk
"$build/apksigner" verify --verbose out/MySpot.apk
