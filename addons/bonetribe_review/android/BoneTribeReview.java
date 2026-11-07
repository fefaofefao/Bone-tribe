package com.bonetribe.review;

import android.app.Activity;
import android.util.Log;

import androidx.annotation.NonNull;

import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;

import org.godotengine.godot.Godot;
import org.godotengine.godot.plugin.GodotPlugin;
import org.godotengine.godot.plugin.SignalInfo;
import org.godotengine.godot.plugin.UsedByGodot;

import java.util.Collections;
import java.util.Set;

/**
 * Avaliação do Bone Tribe no Google Play (In-App Review). O Google decide se a janela
 * aparece (há um limite por usuário) e não informa se a pessoa avaliou.
 * No GDScript: Engine.get_singleton("BoneTribeReview").requestReview().
 */
public class BoneTribeReview extends GodotPlugin {
	private static final String TAG = "BoneTribeReview";

	public BoneTribeReview(Godot godot) {
		super(godot);
	}

	@NonNull
	@Override
	public String getPluginName() {
		return "BoneTribeReview";
	}

	@NonNull
	@Override
	public Set<SignalInfo> getPluginSignals() {
		return Collections.singleton(new SignalInfo("review_finished", Boolean.class));
	}

	@UsedByGodot
	public void requestReview() {
		final Activity activity = getActivity();
		if (activity == null) {
			emitSignal("review_finished", false);
			return;
		}
		activity.runOnUiThread(() -> {
			try {
				final ReviewManager manager = ReviewManagerFactory.create(activity);
				manager.requestReviewFlow().addOnCompleteListener(task -> {
					if (!task.isSuccessful()) {
						Log.w(TAG, "requestReviewFlow falhou");
						emitSignal("review_finished", false);
						return;
					}
					ReviewInfo info = task.getResult();
					manager.launchReviewFlow(activity, info).addOnCompleteListener(done -> emitSignal("review_finished", true));
				});
			} catch (Exception e) {
				Log.w(TAG, "In-App Review indisponível", e);
				emitSignal("review_finished", false);
			}
		});
	}
}
