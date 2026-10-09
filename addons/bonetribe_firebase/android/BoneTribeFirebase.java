package com.bonetribe.firebase;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;

import androidx.annotation.NonNull;

import com.google.firebase.analytics.FirebaseAnalytics;
import com.google.firebase.remoteconfig.FirebaseRemoteConfig;
import com.google.firebase.remoteconfig.FirebaseRemoteConfigSettings;

import org.godotengine.godot.Dictionary;
import org.godotengine.godot.Godot;
import org.godotengine.godot.plugin.GodotPlugin;
import org.godotengine.godot.plugin.UsedByGodot;

/**
 * Plugin Android do Bone Tribe para o Firebase (Analytics + Remote Config).
 * É copiado para o projeto Gradle do Godot pelo plugin do editor
 * (addons/bonetribe_firebase) só quando existe o google-services.json.
 * No GDScript: Engine.get_singleton("BoneTribeFirebase").
 */
public class BoneTribeFirebase extends GodotPlugin {
	private static final String TAG = "BoneTribeFirebase";
	private FirebaseAnalytics analytics;
	private FirebaseRemoteConfig remoteConfig;
	private boolean remoteReady = false;

	public BoneTribeFirebase(Godot godot) {
		super(godot);
	}

	@NonNull
	@Override
	public String getPluginName() {
		return "BoneTribeFirebase";
	}

	/** Liga o Analytics e busca o Remote Config (chamado uma vez ao abrir o jogo). */
	@UsedByGodot
	public void initialize(boolean debug) {
		Activity activity = getActivity();
		if (activity == null) {
			return;
		}
		try {
			analytics = FirebaseAnalytics.getInstance(activity);
			remoteConfig = FirebaseRemoteConfig.getInstance();
			FirebaseRemoteConfigSettings settings = new FirebaseRemoteConfigSettings.Builder()
					.setMinimumFetchIntervalInSeconds(debug ? 60 : 3600)
					.build();
			remoteConfig.setConfigSettingsAsync(settings);
			remoteConfig.fetchAndActivate().addOnCompleteListener(task -> remoteReady = task.isSuccessful());
		} catch (Exception e) {
			Log.w(TAG, "Firebase indisponível: " + e.getMessage());
		}
	}

	@UsedByGodot
	public boolean isReady() {
		return analytics != null;
	}

	/** Registra um evento. Números viram long/double; o resto vira texto. */
	@UsedByGodot
	public void logEvent(String name, Dictionary params) {
		if (analytics == null) {
			return;
		}
		Bundle bundle = new Bundle();
		if (params != null) {
			for (java.util.Map.Entry<String, Object> e : params.entrySet()) {
				String key = e.getKey();
				Object v = e.getValue();
				if (v instanceof Integer || v instanceof Long) {
					bundle.putLong(key, ((Number) v).longValue());
				} else if (v instanceof Float || v instanceof Double) {
					bundle.putDouble(key, ((Number) v).doubleValue());
				} else if (v instanceof Boolean) {
					bundle.putLong(key, ((Boolean) v) ? 1L : 0L);
				} else if (v != null) {
					String s = String.valueOf(v);
					bundle.putString(key, s.length() > 100 ? s.substring(0, 100) : s);
				}
			}
		}
		analytics.logEvent(name, bundle);
	}

	@UsedByGodot
	public void setUserProperty(String name, String value) {
		if (analytics != null) {
			analytics.setUserProperty(name, value);
		}
	}

	/** Coleta de dados ligada/desligada (consentimento). */
	@UsedByGodot
	public void setCollectionEnabled(boolean enabled) {
		if (analytics != null) {
			analytics.setAnalyticsCollectionEnabled(enabled);
		}
	}

	@UsedByGodot
	public boolean isRemoteConfigReady() {
		return remoteReady;
	}

	/** Valor do Remote Config como texto ("" se a chave não existe). */
	@UsedByGodot
	public String getRemoteString(String key) {
		if (remoteConfig == null) {
			return "";
		}
		return remoteConfig.getString(key);
	}
}
