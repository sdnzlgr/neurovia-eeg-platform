import numpy as np
from scipy import signal
from scipy.integrate import simpson

class Analyzer:
    def __init__(self, data, fs):
        self.data = data
        self.fs = fs

    def compute_psd(self):
        freqs, psd = signal.welch(self.data, self.fs)
        return freqs, psd

    def band_power(self, freqs, psd, band):
        low, high = band
        idx = (freqs >= low) & (freqs <= high)
        power = simpson(psd[idx], freqs[idx])
        return power

    def extract_features(self):
        freqs, psd = self.compute_psd()

        features = {
            "delta": self.band_power(freqs, psd, (1, 4)),
            "theta": self.band_power(freqs, psd, (4, 8)),
            "alpha": self.band_power(freqs, psd, (8, 13)),
            "beta": self.band_power(freqs, psd, (13, 30)),
        }

        return features
    
    def interpret(self, features):
        alpha = features["alpha"]
        beta = features["beta"]
        theta = features["theta"]
        delta = features["delta"]

        total = alpha + beta + theta + delta

        alpha_ratio = alpha / total
        beta_ratio = beta / total
        theta_ratio = theta / total

        if alpha_ratio > 0.4:
            return "A relatively elevated relaxation-related activity may be present."
        elif beta_ratio > 0.4:
            return "An increased level of mental activity or attentional engagement may be present."
        elif theta_ratio > 0.4:
            return "A pattern associated with fatigue or reduced attentional state may be present."
        else:
            return "A balanced brain activity pattern is observed."
    
    def compute_ratios(self, features):
        total = sum(features.values())

        ratios = {
            "delta": features["delta"] / total,
            "theta": features["theta"] / total,
            "alpha": features["alpha"] / total,
            "beta": features["beta"] / total,
    }

        return ratios

    def peak_frequency(self):
        freqs, psd = self.compute_psd()

    # sadece 1 Hz üstünü al
        valid_idx = freqs >= 1
        freqs = freqs[valid_idx]
        psd = psd[valid_idx]

        peak_idx = np.argmax(psd)
        return freqs[peak_idx]
    
    def peak_to_peak(self):
        return np.max(self.data) - np.min(self.data)
    
    def band_ratios(self, features):
        ratios = {}

        ratios["theta_beta"] = features["theta"] / (features["beta"] + 1e-6)
        ratios["alpha_beta"] = features["alpha"] / (features["beta"] + 1e-6)
        ratios["delta_theta"] = features["delta"] / (features["theta"] + 1e-6)

        return ratios
    def classify_brain_state(self, features):
        dominant = max(features, key=features.get)

        if dominant == "alpha":
            return "Relaxed / Calm State"
        elif dominant == "beta":
            return "Focused / Alert State"
        elif dominant == "theta":
            return "Drowsy / Light Sleep State"
        elif dominant == "delta":
            return "Deep Rest / Slow-wave Activity"
        else:
            return "Mixed Activity"
    
    def signal_quality(self):
        variance = np.var(self.data)

        if variance < 0.5:
            return "Low Signal (Possible Flat or Noise)"
        elif variance < 2:
            return "Moderate Signal Quality"
        else:
            return "Good Signal Quality"
    
    def detect_artifacts(self):
        freqs, psd = self.compute_psd()

        delta_power = self.band_power(freqs, psd, (0.5, 2))
        muscle_power = self.band_power(freqs, psd, (30, 45))
        peak_to_peak_value = self.peak_to_peak()

        artifact_flags = []

        if delta_power > 0.5:
            artifact_flags.append("Possible low-frequency drift or movement artifact detected.")

        if muscle_power > 0.05:
            artifact_flags.append("Possible muscle-related high-frequency noise detected.")

        if peak_to_peak_value > 15:
            artifact_flags.append("High amplitude variation detected; artifact contamination may be present.")

        if not artifact_flags:
            artifact_flags.append("No major artifact pattern detected in the representative signal.")

        return artifact_flags