package com.bonetribe.notify;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;

import org.godotengine.godot.Godot;
import org.godotengine.godot.plugin.GodotPlugin;
import org.godotengine.godot.plugin.UsedByGodot;

/**
 * Notificações locais do Bone Tribe: agenda lembretes no próprio aparelho
 * (AlarmManager + BoneTribeNotifyReceiver). Nada sai do aparelho.
 * No GDScript: Engine.get_singleton("BoneTribeNotify").
 */
public class BoneTribeNotify extends GodotPlugin {
	private static final String TAG = "BoneTribeNotify";
	private static final int PERMISSION_REQUEST = 7301;

	public BoneTribeNotify(Godot godot) {
		super(godot);
	}

	@NonNull
	@Override
	public String getPluginName() {
		return "BoneTribeNotify";
	}

	/** Android 13+ precisa da permissão; antes disso, já está liberado. */
	@UsedByGodot
	public boolean hasPermission() {
		Activity activity = getActivity();
		if (activity == null) {
			return false;
		}
		if (Build.VERSION.SDK_INT < 33) {
			return true;
		}
		return activity.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
	}

	@UsedByGodot
	public void requestPermission() {
		Activity activity = getActivity();
		if (activity == null || Build.VERSION.SDK_INT < 33 || hasPermission()) {
			return;
		}
		activity.runOnUiThread(() -> activity.requestPermissions(new String[] {Manifest.permission.POST_NOTIFICATIONS}, PERMISSION_REQUEST));
	}

	/** Agenda a notificação `id` para daqui a `delaySeconds` segundos (substitui a anterior com o mesmo id). */
	@UsedByGodot
	public void schedule(int id, String title, String body, int delaySeconds) {
		Activity activity = getActivity();
		if (activity == null || delaySeconds <= 0) {
			return;
		}
		try {
			AlarmManager am = (AlarmManager) activity.getSystemService(Context.ALARM_SERVICE);
			if (am == null) {
				return;
			}
			long at = System.currentTimeMillis() + delaySeconds * 1000L;
			am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pending(activity, id, title, body));
		} catch (Exception e) {
			Log.w(TAG, "schedule: " + e.getMessage());
		}
	}

	@UsedByGodot
	public void cancel(int id) {
		Activity activity = getActivity();
		if (activity == null) {
			return;
		}
		try {
			AlarmManager am = (AlarmManager) activity.getSystemService(Context.ALARM_SERVICE);
			if (am != null) {
				am.cancel(pending(activity, id, "", ""));
			}
			android.app.NotificationManager nm = (android.app.NotificationManager) activity.getSystemService(Context.NOTIFICATION_SERVICE);
			if (nm != null) {
				nm.cancel(id);
			}
		} catch (Exception e) {
			Log.w(TAG, "cancel: " + e.getMessage());
		}
	}

	private static PendingIntent pending(Context ctx, int id, String title, String body) {
		Intent intent = new Intent(ctx, BoneTribeNotifyReceiver.class);
		intent.putExtra("id", id);
		intent.putExtra("title", title);
		intent.putExtra("body", body);
		return PendingIntent.getBroadcast(ctx, id, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
	}
}
