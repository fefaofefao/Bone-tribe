package com.bonetribe.notify;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;

/** Mostra a notificação agendada; tocar nela abre o jogo. */
public class BoneTribeNotifyReceiver extends BroadcastReceiver {
	static final String CHANNEL = "bonetribe_reminders";

	@Override
	public void onReceive(Context context, Intent intent) {
		try {
			int id = intent.getIntExtra("id", 1);
			String title = intent.getStringExtra("title");
			String body = intent.getStringExtra("body");
			if (title == null || title.isEmpty()) {
				return;
			}
			NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
			if (nm == null) {
				return;
			}
			if (Build.VERSION.SDK_INT >= 26 && nm.getNotificationChannel(CHANNEL) == null) {
				nm.createNotificationChannel(new NotificationChannel(CHANNEL, "Bone Tribe", NotificationManager.IMPORTANCE_DEFAULT));
			}
			Intent open = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
			PendingIntent tap = null;
			if (open != null) {
				open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
				tap = PendingIntent.getActivity(context, id, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
			}
			int icon = context.getResources().getIdentifier("bonetribe_notify_icon", "drawable", context.getPackageName());
			if (icon == 0) {
				icon = context.getApplicationInfo().icon;
			}
			Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(context, CHANNEL) : new Notification.Builder(context);
			b.setSmallIcon(icon)
					.setContentTitle(title)
					.setContentText(body)
					.setStyle(new Notification.BigTextStyle().bigText(body))
					.setAutoCancel(true);
			if (tap != null) {
				b.setContentIntent(tap);
			}
			nm.notify(id, b.build());
		} catch (Exception e) {
			Log.w("BoneTribeNotify", "onReceive: " + e.getMessage());
		}
	}
}
