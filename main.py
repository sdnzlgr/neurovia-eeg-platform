import os
import math
import shutil
from collections import Counter

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
import mne

from data_loader import EEGLoader
from preprocessing import Preprocessor
from analysis import Analyzer
from report import create_report


sns.set_theme(style="whitegrid", rc={
    "axes.edgecolor": "#b0b0b0",
    "grid.color": "#e0e0e0",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "font.family": "sans-serif"
})


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
TR_REPORT_DIR = os.path.join(REPORT_DIR, "tr")
EN_REPORT_DIR = os.path.join(REPORT_DIR, "en")

os.makedirs(TR_REPORT_DIR, exist_ok=True)
os.makedirs(EN_REPORT_DIR, exist_ok=True)


def ensure_report_in_folder(pdf_path, lang):
    if not pdf_path:
        return None

    target_dir = TR_REPORT_DIR if lang == "tr" else EN_REPORT_DIR
    pdf_filename = os.path.basename(pdf_path)
    target_path = os.path.join(target_dir, pdf_filename)

    if os.path.abspath(pdf_path) != os.path.abspath(target_path):
        if os.path.exists(pdf_path):
            shutil.move(pdf_path, target_path)

    return pdf_filename


def build_temporal_summary(lang, band_distribution, total_segments):
    delta = band_distribution.get("delta", 0)
    theta = band_distribution.get("theta", 0)
    alpha = band_distribution.get("alpha", 0)
    beta = band_distribution.get("beta", 0)

    dominant = max(band_distribution, key=band_distribution.get) if band_distribution else "mixed"

    if lang == "tr":
        summary = (
            f"Kayıt toplam {total_segments} adet iki dakikalık segmente ayrılarak analiz edilmiştir. "
            f"Segment dağılımına göre delta baskın segment oranı %{delta:.1f}, theta baskın segment oranı %{theta:.1f}, "
            f"alpha baskın segment oranı %{alpha:.1f} ve beta baskın segment oranı %{beta:.1f} olarak hesaplanmıştır. "
        )

        if dominant == "delta":
            summary += (
                "Genel zamansal örüntü delta baskın görünmektedir. Bu durum kayıt boyunca yavaş dalga aktivitesinin "
                "ön planda olduğunu, ancak segment bazlı geçişlerin ayrıca dikkate alınması gerektiğini gösterir."
            )
        elif dominant == "alpha":
            summary += (
                "Genel zamansal örüntü alpha baskın görünmektedir. Bu durum kayıt boyunca rahat uyanıklık benzeri "
                "aktivitenin daha belirgin olduğunu düşündürebilir."
            )
        elif dominant == "theta":
            summary += (
                "Genel zamansal örüntü theta baskın görünmektedir. Bu durum uykuya eğilim, içsel odaklanma veya "
                "azalmış uyanıklık ile ilişkili olabilir."
            )
        elif dominant == "beta":
            summary += (
                "Genel zamansal örüntü beta baskın görünmektedir. Bu durum aktif bilişsel süreçler, dikkat veya "
                "artmış zihinsel yük ile ilişkili olabilir."
            )
        else:
            summary += "Genel zamansal örüntü karışık görünmektedir."

    else:
        summary = (
            f"The recording was divided into {total_segments} two-minute segments. "
            f"Based on segment distribution, delta-dominant segments accounted for {delta:.1f}%, "
            f"theta-dominant segments for {theta:.1f}%, alpha-dominant segments for {alpha:.1f}%, "
            f"and beta-dominant segments for {beta:.1f}%. "
        )

        if dominant == "delta":
            summary += (
                "The overall temporal pattern appears delta-dominant, indicating that slow-wave activity was prominent "
                "throughout the recording while segment-level transitions should still be considered."
            )
        elif dominant == "alpha":
            summary += (
                "The overall temporal pattern appears alpha-dominant, which may suggest relaxed wakefulness-like activity."
            )
        elif dominant == "theta":
            summary += (
                "The overall temporal pattern appears theta-dominant, which may be associated with drowsiness or internally focused states."
            )
        elif dominant == "beta":
            summary += (
                "The overall temporal pattern appears beta-dominant, which may be associated with active cognitive processing or increased mental load."
            )
        else:
            summary += "The overall temporal pattern appears mixed."

    return summary, dominant


def build_language_texts(lang, dominant_band, ratios, raw_brain_state, raw_signal_quality, temporal_summary=None):
    if lang == "tr":
        brain_state_map = {
            "Deep Rest / Slow-wave Activity": "Derin Dinlenme / Yavaş Dalga Aktivitesi",
            "Relaxed Wakefulness": "Rahat Uyanıklık",
            "Drowsy-like State": "Uykuya Eğilimli Durum",
            "Alert / Active Cognitive State": "Uyanık / Aktif Bilişsel Durum",
        }

        signal_quality_map = {
            "Moderate Signal Quality": "Orta Sinyal Kalitesi",
            "Low Signal (Possible Flat or Noise)": "Düşük Sinyal (Olası Düz Çizgi veya Gürültü)",
            "Good Signal Quality": "İyi Sinyal Kalitesi",
        }

        brain_state = brain_state_map.get(raw_brain_state, raw_brain_state)
        signal_quality = signal_quality_map.get(raw_signal_quality, raw_signal_quality)

        if dominant_band == "delta":
            global_comment = "Baskın delta aktivitesi derin dinlenme, uykululuk veya yavaş dalga beyin aktivitesini düşündürebilir."
            yorum = "Segment bazlı değerlendirmeye göre baskın yavaş dalga aktivitesi ile uyumlu bir örüntü gözlenmiştir."
            state_profile = "Yavaş dalga baskın / Derin dinlenme benzeri örüntü"
            global_summary = (
                "Analiz, segment bazlı değerlendirmede yavaş dalga baskın / derin dinlenme benzeri bir örüntü göstermektedir. "
                "Baskın frekans bandı DELTA olarak bulunmuştur. Sinyal kalitesi orta düzeydedir."
            )
        elif dominant_band == "theta":
            global_comment = "Baskın theta aktivitesi uykuya eğilim veya içsel bilişsel süreçlerle ilişkili olabilir."
            yorum = "Segment bazlı değerlendirmeye göre theta aktivitesi baskın bir örüntü gözlenmiştir."
            state_profile = "Uykuya eğilimli / İçsel odaklı örüntü"
            global_summary = f"Segment bazlı değerlendirmede baskın frekans bandı {dominant_band.upper()} olarak bulunmuştur."
        elif dominant_band == "alpha":
            global_comment = "Baskın alpha aktivitesi rahat uyanıklık hali ile uyumlu olabilir."
            yorum = "Segment bazlı değerlendirmeye göre rahat uyanıklık ile uyumlu alpha baskın bir örüntü gözlenmiştir."
            state_profile = "Rahat uyanıklık / Sakin durum örüntüsü"
            global_summary = f"Segment bazlı değerlendirmede baskın frekans bandı {dominant_band.upper()} olarak bulunmuştur."
        elif dominant_band == "beta":
            global_comment = "Baskın beta aktivitesi dikkat, bilişsel aktivasyon veya artmış zihinsel çaba ile ilişkili olabilir."
            yorum = "Segment bazlı değerlendirmeye göre beta aktivitesi baskın bir örüntü gözlenmiştir."
            state_profile = "Uyanık / Aktif bilişsel durum örüntüsü"
            global_summary = f"Segment bazlı değerlendirmede baskın frekans bandı {dominant_band.upper()} olarak bulunmuştur."
        else:
            global_comment = "Belirgin bir baskın bant yorumu üretilememiştir."
            yorum = "Belirgin bir baskın frekans örüntüsü saptanmamıştır."
            state_profile = "Karışık veya dengeli aktivite örüntüsü"
            global_summary = "Segment bazlı değerlendirmede karışık veya dengeli bir aktivite örüntüsü gözlenmiştir."

        if temporal_summary:
            global_summary += "<br/><br/>" + temporal_summary

    else:
        brain_state = raw_brain_state
        signal_quality = raw_signal_quality

        if dominant_band == "delta":
            global_comment = "Dominant delta activity suggests deep relaxation, drowsiness, or slow-wave brain activity."
            yorum = "A segment-based slow-wave dominant pattern is observed."
            state_profile = "Slow-wave dominant / Deep rest-like pattern"
            global_summary = (
                "Segment-based analysis indicates a slow-wave dominant / deep rest-like pattern. "
                "The dominant frequency band is DELTA. Signal quality is assessed as moderate."
            )
        elif dominant_band == "theta":
            global_comment = "Dominant theta activity may be associated with drowsiness or internally directed cognitive processes."
            yorum = "A segment-based theta-dominant activity pattern is observed."
            state_profile = "Drowsy-like / Internal focus pattern"
            global_summary = f"The segment-based dominant frequency band was {dominant_band.upper()}."
        elif dominant_band == "alpha":
            global_comment = "Dominant alpha activity is commonly associated with relaxed wakefulness."
            yorum = "A segment-based alpha-dominant relaxed wakefulness pattern is observed."
            state_profile = "Relaxed wakefulness / Calm state pattern"
            global_summary = f"The segment-based dominant frequency band was {dominant_band.upper()}."
        elif dominant_band == "beta":
            global_comment = "Dominant beta activity may reflect alertness or increased cognitive engagement."
            yorum = "A segment-based beta-dominant activity pattern is observed."
            state_profile = "Alert / Active cognitive state pattern"
            global_summary = f"The segment-based dominant frequency band was {dominant_band.upper()}."
        else:
            global_comment = "No clear dominant band interpretation was generated."
            yorum = "No clear dominant frequency pattern was detected."
            state_profile = "Mixed or balanced activity pattern"
            global_summary = "A mixed or balanced activity pattern was observed."

        if temporal_summary:
            global_summary += "<br/><br/>" + temporal_summary

    return brain_state, signal_quality, global_comment, yorum, state_profile, global_summary


def build_segment_texts(lang, dominant_band):
    if lang == "tr":
        if dominant_band == "delta":
            return "Segmentte baskın delta aktivitesi gözlenmiştir. Bu durum derin dinlenme, uykululuk veya yavaş dalga baskınlığı ile ilişkili olabilir.", "Yavaş dalga baskın"
        elif dominant_band == "theta":
            return "Segmentte baskın theta aktivitesi gözlenmiştir. Bu durum uykuya geçiş veya içe yönelimli bilişsel durumlarla ilişkili olabilir.", "Uykuya eğilimli"
        elif dominant_band == "alpha":
            return "Segmentte baskın alpha aktivitesi gözlenmiştir. Bu durum genellikle rahat uyanıklık hali ile ilişkilidir.", "Rahat uyanıklık"
        elif dominant_band == "beta":
            return "Segmentte baskın beta aktivitesi gözlenmiştir. Bu durum dikkat, aktif düşünme veya artmış bilişsel yük ile ilişkili olabilir.", "Uyanık / bilişsel olarak aktif"
        return "Bu segment için belirgin bir baskın bant yorumu üretilememiştir.", "Karışık"

    else:
        if dominant_band == "delta":
            return "Segment shows dominant delta activity, which may reflect deep rest, drowsiness, or slow-wave predominance.", "Slow-wave dominant"
        elif dominant_band == "theta":
            return "Segment shows dominant theta activity, which may be associated with drowsiness or internally focused cognitive state.", "Drowsy-like"
        elif dominant_band == "alpha":
            return "Segment shows dominant alpha activity, which is commonly associated with relaxed wakefulness.", "Relaxed wakefulness"
        elif dominant_band == "beta":
            return "Segment shows dominant beta activity, which may reflect alertness, active thinking, or increased cognitive load.", "Alert / cognitively active"
        return "No clear dominant band interpretation was generated for this segment.", "Mixed"


def build_regional_comments(regional_summary, lang):
    regional_comments = {}

    for region, bands in regional_summary.items():
        dominant = max(bands, key=bands.get)

        if lang == "tr":
            if dominant == "delta":
                comment = "düşük kortikal aktivite veya derin dinlenme ile ilişkili olabilir"
            elif dominant == "theta":
                comment = "uykuya eğilim veya içsel odaklanma ile ilişkili olabilir"
            elif dominant == "alpha":
                comment = "rahat ve sakin durum ile uyumlu olabilir"
            elif dominant == "beta":
                comment = "aktif düşünme ve uyanıklık ile ilişkili olabilir"
            else:
                comment = "belirgin bir yorum üretilememiştir"

            regional_comments[region] = f"{region.capitalize()} bölgede {dominant.upper()} baskınlığı gözlenmiştir ve bu durum {comment}."
        else:
            if dominant == "delta":
                comment = "may indicate low cortical activity or deep rest"
            elif dominant == "theta":
                comment = "may reflect drowsiness or internal focus"
            elif dominant == "alpha":
                comment = "may suggest a relaxed and calm state"
            elif dominant == "beta":
                comment = "may be associated with active thinking and alertness"
            else:
                comment = "has no clear interpretation"

            regional_comments[region] = f"{region.capitalize()} region shows {dominant.upper()} dominance and {comment}."

    return regional_comments


def build_alerts_and_recommendations(lang, dominant_band, ratios, raw_signal_quality):
    alerts = []
    recommendations = []

    if lang == "tr":
        if dominant_band == "delta":
            alerts.append("Segment bazlı değerlendirmeye göre delta baskınlığı öne çıkmaktadır; bu durum derin dinlenme, uykululuk veya yavaş dalga aktivitesi ile ilişkili olabilir.")
            recommendations.append("Kayıt sırasında uykululuk, yorgunluk veya derin dinlenme durumunun klinik olarak gözden geçirilmesi önerilir.")

        if ratios["alpha"] < 0.15:
            alerts.append("Alpha göreceli gücü düşük görünmektedir; bu durum azalmış rahat uyanıklık hali ile ilişkili olabilir.")
            recommendations.append("Özellikle gözler kapalı dinlenim koşullarında rahat uyanıklık belirteçlerinin ek olarak incelenmesi faydalı olabilir.")

        if ratios["beta"] > 0.25:
            alerts.append("Beta göreceli gücünde artış gözlenmiştir; bu durum artmış bilişsel yük veya gerginlik ile ilişkili olabilir.")

        if raw_signal_quality == "Moderate Signal Quality":
            alerts.append("Sinyal kalitesi orta düzeydedir. Sonuçlar dikkatli yorumlanmalıdır.")
            recommendations.append("Sinyal kalitesini artırmak amacıyla daha kontrollü koşullarda tekrar kayıt alınması değerlendirilebilir.")

        if raw_signal_quality == "Low Signal (Possible Flat or Noise)":
            alerts.append("Sinyal kalitesi düşüktür. Kayıt artefaktları veya teknik problemler yorumu etkileyebilir.")
            recommendations.append("Yorumlama öncesinde elektrotlar, impedans düzeyi ve kayıt koşulları açısından teknik değerlendirme yapılması önerilir.")

        if not alerts:
            alerts.append("Mevcut kayıtta belirgin bir analitik uyarı saptanmamıştır.")

        if not recommendations:
            recommendations.append("Mevcut otomatik analize göre acil ek bir takip adımı önerilmemektedir.")

    else:
        if dominant_band == "delta":
            alerts.append("Segment-based evaluation indicates delta dominance, which may reflect deep rest, drowsiness, or slow-wave predominance.")
            recommendations.append("Consider reviewing the subject state for drowsiness, fatigue, or deep relaxation during recording.")

        if ratios["alpha"] < 0.15:
            alerts.append("Alpha relative power appears low, which may be associated with reduced relaxed wakefulness.")
            recommendations.append("Further inspection of relaxed wakefulness markers may be useful, particularly under eyes-closed resting conditions.")

        if ratios["beta"] > 0.25:
            alerts.append("Elevated beta relative power may reflect increased cognitive load or tension.")

        if raw_signal_quality == "Moderate Signal Quality":
            alerts.append("Signal quality is moderate. Results should be interpreted with caution.")
            recommendations.append("Consider repeating the recording under more controlled conditions to improve signal quality.")

        if raw_signal_quality == "Low Signal (Possible Flat or Noise)":
            alerts.append("Signal quality is low. Recording artifacts or technical issues may affect interpretation.")
            recommendations.append("Technical review of electrodes, impedance, and recording conditions is recommended before interpretation.")

        if not alerts:
            alerts.append("No major analytical warning flags were detected.")

        if not recommendations:
            recommendations.append("No immediate follow-up action is suggested based on the current automated analysis.")

    return alerts, recommendations


def run_analysis(file_path):
    if not file_path:
        raise ValueError("file_path is empty or None.")

    print("RUNNING FILE:", file_path)

    loader = EEGLoader(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".edf":
        loader.load_edf()
    elif ext == ".csv":
        loader.load_csv()
    elif ext == ".mat":
        loader.load_mat()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    data = loader.get_standardized_data()

    max_fs = 250
    if loader.sampling_rate > max_fs:
        factor = int(loader.sampling_rate // max_fs)
        if factor > 1:
            data = data[:, ::factor]
            loader.sampling_rate = loader.sampling_rate / factor

    channel_names = loader.channel_names

    if channel_names is not None:
        eeg_indices = []
        eeg_channel_names = []

        for i, ch in enumerate(channel_names):
            ch_upper = str(ch).upper()

            if (
                "PSG_F" in ch_upper or
                "PSG_C" in ch_upper or
                "PSG_O" in ch_upper or
                ch_upper in ["F3", "F4", "C3", "C4", "O1", "O2", "FP1", "FP2", "FZ", "CZ", "PZ", "OZ"]
            ):
                eeg_indices.append(i)
                eeg_channel_names.append(ch)

        if eeg_indices:
            data = data[eeg_indices, :]
            channel_names = eeg_channel_names
            loader.channel_names = eeg_channel_names

    clean_channel = []

    for channel in data:
        pre = Preprocessor(channel, fs=loader.sampling_rate)
        clean_signal = pre.preprocess()
        clean_channel.append(clean_signal)

    clean_data = np.array(clean_channel)

    segment_duration_sec = 120
    segment_samples = int(loader.sampling_rate * segment_duration_sec)
    total_samples = clean_data.shape[1]
    num_segments = math.ceil(total_samples / segment_samples)

    base_segment_results = []

    for seg_idx in range(num_segments):
        start = seg_idx * segment_samples
        end = min(start + segment_samples, total_samples)
        segment_data = clean_data[:, start:end]

        segment_features = []

        for ch in segment_data:
            analyzer = Analyzer(ch, loader.sampling_rate)
            features = analyzer.extract_features()
            segment_features.append(features)

        avg_segment_features = {
            "delta": np.mean([f["delta"] for f in segment_features]),
            "theta": np.mean([f["theta"] for f in segment_features]),
            "alpha": np.mean([f["alpha"] for f in segment_features]),
            "beta": np.mean([f["beta"] for f in segment_features]),
        }

        segment_dominant_band = max(avg_segment_features, key=avg_segment_features.get)

        base_segment_results.append({
            "segment": seg_idx + 1,
            "start_sec": start / loader.sampling_rate,
            "end_sec": end / loader.sampling_rate,
            "delta": avg_segment_features["delta"],
            "theta": avg_segment_features["theta"],
            "alpha": avg_segment_features["alpha"],
            "beta": avg_segment_features["beta"],
            "dominant_band": segment_dominant_band,
        })

    dominant_bands = [seg["dominant_band"] for seg in base_segment_results]
    counts = Counter(dominant_bands)
    total_segments = len(base_segment_results)

    band_distribution = {
        "delta": (counts.get("delta", 0) / total_segments) * 100,
        "theta": (counts.get("theta", 0) / total_segments) * 100,
        "alpha": (counts.get("alpha", 0) / total_segments) * 100,
        "beta": (counts.get("beta", 0) / total_segments) * 100,
    }

    segment_dominant_band = max(band_distribution, key=band_distribution.get)

    all_features = []
    all_p2p = []

    for ch in clean_data:
        analyzer = Analyzer(ch, loader.sampling_rate)
        features = analyzer.extract_features()
        all_features.append(features)
        all_p2p.append(analyzer.peak_to_peak())

    channel_band_results = []

    for i, feat in enumerate(all_features):
        channel_label = channel_names[i] if channel_names and i < len(channel_names) else f"Ch{i + 1}"

        channel_band_results.append({
            "channel": i + 1,
            "channel_name": channel_label,
            "delta": feat["delta"],
            "theta": feat["theta"],
            "alpha": feat["alpha"],
            "beta": feat["beta"]
        })

    regional_analysis = {
        "frontal": [],
        "central": [],
        "parietal": [],
        "occipital": []
    }

    total = len(channel_band_results)

    for i, row in enumerate(channel_band_results):
        if i < total * 0.25:
            region = "frontal"
        elif i < total * 0.5:
            region = "central"
        elif i < total * 0.75:
            region = "parietal"
        else:
            region = "occipital"

        regional_analysis[region].append(row)

    regional_summary = {}

    for region, channels in regional_analysis.items():
        if len(channels) == 0:
            regional_summary[region] = {"delta": 0, "theta": 0, "alpha": 0, "beta": 0}
        else:
            regional_summary[region] = {
                "delta": np.mean([c["delta"] for c in channels]),
                "theta": np.mean([c["theta"] for c in channels]),
                "alpha": np.mean([c["alpha"] for c in channels]),
                "beta": np.mean([c["beta"] for c in channels]),
            }

    avg_features = {
        "delta": np.mean([f["delta"] for f in all_features]),
        "theta": np.mean([f["theta"] for f in all_features]),
        "alpha": np.mean([f["alpha"] for f in all_features]),
        "beta": np.mean([f["beta"] for f in all_features]),
    }

    dominant_band = segment_dominant_band

    global_analyzer = Analyzer(clean_data[0], loader.sampling_rate)

    ratios = global_analyzer.compute_ratios(avg_features)
    band_ratios = global_analyzer.band_ratios(avg_features)
    peak_freq = global_analyzer.peak_frequency()
    avg_p2p = np.mean(all_p2p)

    raw_brain_state = global_analyzer.classify_brain_state(avg_features)
    raw_signal_quality = global_analyzer.signal_quality()

    artifact_flags_raw = global_analyzer.detect_artifacts()

    if not artifact_flags_raw:
        artifact_flags_raw = ["No major artifact pattern detected in the representative signal."]

    freqs, psd = global_analyzer.compute_psd()

    segments_x = [s["segment"] for s in base_segment_results]
    delta_y = [s["delta"] for s in base_segment_results]
    theta_y = [s["theta"] for s in base_segment_results]
    alpha_y = [s["alpha"] for s in base_segment_results]
    beta_y = [s["beta"] for s in base_segment_results]

    topomap_created = False
    matched_names = []
    matched_values = []
    montage = None

    try:
        if channel_names:
            cleaned_channel_names = []

            for ch in channel_names:
                ch = str(ch).strip().replace(".", "")

                replacements = {
                    "FP1": "Fp1",
                    "FP2": "Fp2",
                    "FPZ": "Fpz",
                    "FCZ": "FCz",
                    "CPZ": "CPz",
                    "POZ": "POz",
                    "CZ": "Cz",
                    "PZ": "Pz",
                    "FZ": "Fz",
                    "OZ": "Oz",
                    "IZ": "Iz"
                }

                ch = replacements.get(ch.upper(), ch)
                cleaned_channel_names.append(ch)

            alpha_channel_values = np.array([f["alpha"] for f in all_features], dtype=float)
            montage = mne.channels.make_standard_montage("standard_1020")

            for ch_name, ch_val in zip(cleaned_channel_names, alpha_channel_values):
                if ch_name in montage.ch_names:
                    matched_names.append(ch_name)
                    matched_values.append(ch_val)

            if len(matched_names) >= 4:
                topomap_created = True

    except Exception as e:
        print("TOPO MAP CHECK ERROR:", e)
        topomap_created = False

    report_files = {}
    ui_values = {}

    for lang in ["tr", "en"]:
        temporal_summary, _ = build_temporal_summary(lang, band_distribution, total_segments)

        brain_state, signal_quality, global_comment, yorum, state_profile, global_summary = build_language_texts(
            lang=lang,
            dominant_band=dominant_band,
            ratios=ratios,
            raw_brain_state=raw_brain_state,
            raw_signal_quality=raw_signal_quality,
            temporal_summary=temporal_summary
        )

        segment_results = []

        for seg in base_segment_results:
            segment_interpretation, segment_state = build_segment_texts(lang, seg["dominant_band"])

            segment_results.append({
                **seg,
                "segment_interpretation": segment_interpretation,
                "segment_state": segment_state,
                "comment": segment_interpretation
            })

        segment_flags = []

        if len(segment_results) > 1:
            for i in range(1, len(segment_results)):
                prev_seg = segment_results[i - 1]
                curr_seg = segment_results[i]

                if curr_seg["delta"] > prev_seg["delta"] * 1.20:
                    segment_flags.append(
                        f"{curr_seg['segment']}. segmentte, {prev_seg['segment']}. segmente göre belirgin delta artışı gözlenmiştir."
                        if lang == "tr"
                        else f"Segment {curr_seg['segment']} shows a notable increase in delta power compared to Segment {prev_seg['segment']}."
                    )

                if curr_seg["beta"] > prev_seg["beta"] * 1.20:
                    segment_flags.append(
                        f"{curr_seg['segment']}. segmentte, {prev_seg['segment']}. segmente göre belirgin beta artışı gözlenmiştir."
                        if lang == "tr"
                        else f"Segment {curr_seg['segment']} shows a notable increase in beta power compared to Segment {prev_seg['segment']}."
                    )

                if curr_seg["alpha"] < prev_seg["alpha"] * 0.80:
                    segment_flags.append(
                        f"{curr_seg['segment']}. segmentte, {prev_seg['segment']}. segmente göre belirgin alpha azalması gözlenmiştir."
                        if lang == "tr"
                        else f"Segment {curr_seg['segment']} shows a notable decrease in alpha power compared to Segment {prev_seg['segment']}."
                    )

        if not segment_flags:
            segment_flags.append(
                "Analiz edilen kayıtta segmentler arasında belirgin bir dalgalanma saptanmamıştır."
                if lang == "tr"
                else "No major segment-to-segment fluctuation was detected."
            )

        artifact_flags = []

        for flag in artifact_flags_raw:
            if lang == "tr":
                if "No major artifact" in flag:
                    artifact_flags.append("Temsili sinyalde belirgin majör artefakt örüntüsü saptanmamıştır.")
                elif "eye blink" in flag.lower():
                    artifact_flags.append("Göz kırpma kaynaklı artefakt şüphesi tespit edilmiştir.")
                elif "muscle" in flag.lower():
                    artifact_flags.append("Kas aktivitesine bağlı artefakt şüphesi gözlenmiştir.")
                elif "noise" in flag.lower():
                    artifact_flags.append("Yüksek frekanslı gürültü tespit edilmiştir.")
                else:
                    artifact_flags.append("Artefakt ile ilişkili bir durum tespit edilmiştir.")
            else:
                artifact_flags.append(flag)

        regional_comments = build_regional_comments(regional_summary, lang)

        alerts, recommendations = build_alerts_and_recommendations(
            lang=lang,
            dominant_band=dominant_band,
            ratios=ratios,
            raw_signal_quality=raw_signal_quality
        )

        if segment_flags:
            if len(segment_flags) == 1 and (
                "No major" in segment_flags[0] or
                "belirgin bir dalgalanma saptanmamıştır" in segment_flags[0]
            ):
                stability_score = 90
            else:
                stability_score = max(50, 90 - 10 * min(len(segment_flags) - 1, 4))
        else:
            stability_score = 85

        relaxation_score = int(
            min(100, max(0, (ratios["alpha"] * 200) + (ratios["delta"] * 50) - (ratios["beta"] * 100)))
        )

        alertness_score = int(
            min(100, max(0, (ratios["beta"] * 220) + (ratios["alpha"] * 40) - (ratios["delta"] * 80)))
        )

        analysis_scores = {
            "stability_score": stability_score,
            "relaxation_score": relaxation_score,
            "alertness_score": alertness_score
        }

        plt.figure(figsize=(10, 4))
        plt.plot(clean_data[0], color="#2C3E50", linewidth=0.8)
        plt.title("Preprocessed EEG Signal - Representative Channel" if lang == "en" else "Ön İşlenmiş EEG Sinyali - Temsili Kanal")
        plt.xlabel("Samples" if lang == "en" else "Örnekler")
        plt.ylabel("Amplitude" if lang == "en" else "Genlik")
        plt.tight_layout()
        plt.savefig("preprocessed_signal.png", dpi=300)
        plt.close()

        plt.figure(figsize=(9, 4))
        plt.plot(segments_x, delta_y, label="Delta", marker="o", color="#1f77b4")
        plt.plot(segments_x, theta_y, label="Theta", marker="s", color="#ff7f0e")
        plt.plot(segments_x, alpha_y, label="Alpha", marker="^", color="#2ca02c")
        plt.plot(segments_x, beta_y, label="Beta", marker="d", color="#d62728")
        plt.title("Segment-Based Band Power Trends" if lang == "en" else "Segment Bazlı Bant Gücü Trendleri")
        plt.xlabel("Segment Number" if lang == "en" else "Segment Numarası")
        plt.ylabel("Band Power" if lang == "en" else "Bant Gücü")
        plt.legend()
        plt.tight_layout()
        plt.savefig("segment_trend.png", dpi=300)
        plt.close()

        trend_configs = [
            ("delta_trend.png", delta_y, "Delta", "#1f77b4"),
            ("alpha_trend.png", alpha_y, "Alpha", "#2ca02c"),
            ("beta_trend.png", beta_y, "Beta", "#d62728")
        ]

        for filename, y_data, band_name, color in trend_configs:
            plt.figure(figsize=(8, 3))
            plt.plot(segments_x, y_data, marker="o", color=color, linewidth=2)
            plt.title(f"{band_name} Power Across Segments" if lang == "en" else f"Segmentler Boyunca {band_name} Gücü")
            plt.xlabel("Segment Number" if lang == "en" else "Segment Numarası")
            plt.ylabel(f"{band_name} Power" if lang == "en" else f"{band_name} Gücü")
            plt.tight_layout()
            plt.savefig(filename, dpi=300)
            plt.close()

        plt.figure(figsize=(8, 4))
        plt.semilogy(freqs, psd, color="#2980B9", linewidth=1.5)
        plt.title("Power Spectral Density - Representative Channel" if lang == "en" else "Güç Spektral Yoğunluğu (PSD)")
        plt.xlabel("Frequency (Hz)" if lang == "en" else "Frekans (Hz)")
        plt.ylabel("Power" if lang == "en" else "Güç")
        plt.fill_between(freqs, psd, color="#2980B9", alpha=0.1)
        plt.tight_layout()
        plt.savefig("psd_plot.png", dpi=300)
        plt.close()

        if topomap_created and montage is not None:
            try:
                info = mne.create_info(
                    ch_names=matched_names,
                    sfreq=loader.sampling_rate,
                    ch_types=["eeg"] * len(matched_names)
                )
                info.set_montage(montage)

                fig, ax = plt.subplots(figsize=(6, 5))
                mne.viz.plot_topomap(
                    np.array(matched_values, dtype=float),
                    info,
                    axes=ax,
                    show=False,
                    cmap="viridis"
                )
                ax.set_title("Alpha Band Topographic Map" if lang == "en" else "Alpha Bandı Topografik Haritası")
                plt.tight_layout()
                plt.savefig("alpha_topomap.png", dpi=300)
                plt.close(fig)

            except Exception as e:
                print("TOPO MAP DRAW ERROR:", e)
                topomap_created = False

        alpha_values = [f["alpha"] for f in all_features]
        n_channel = len(alpha_values)
        grid_cols = math.ceil(math.sqrt(n_channel))
        grid_rows = math.ceil(n_channel / grid_cols)
        padded_alpha = alpha_values + [0] * (grid_rows * grid_cols - n_channel)
        alpha_array = np.array(padded_alpha).reshape(grid_rows, grid_cols)

        plt.figure(figsize=(7, 5))
        sns.heatmap(alpha_array, annot=False, cmap="YlGnBu", cbar_kws={"label": "Power"})
        plt.title("Alpha Power Heatmap" if lang == "en" else "Alpha Gücü Isı Haritası")
        plt.tight_layout()
        plt.savefig("alpha_heatmap.png", dpi=300)
        plt.close()

        bands = list(avg_features.keys())
        values = list(avg_features.values())

        plt.figure(figsize=(7, 4))
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        plt.bar(bands, values, color=colors[:len(bands)], alpha=0.8)
        plt.title("Band Power Distribution" if lang == "en" else "Bant Gücü Dağılımı")
        plt.xlabel("Frequency Bands" if lang == "en" else "Frekans Bantları")
        plt.ylabel("Power" if lang == "en" else "Güç")
        plt.tight_layout()
        plt.savefig("band_bar.png", dpi=300)
        plt.close()

        

        temporal_bands = ["delta", "theta", "alpha", "beta"]
        temporal_values = [band_distribution.get(b, 0) for b in temporal_bands]

        plt.figure(figsize=(7, 4))
        plt.bar(
            [b.upper() for b in temporal_bands],
            temporal_values,
            color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
            alpha=0.85
        )
        plt.title("Segment-Based Dominant Band Distribution" if lang == "en" else "Segment Bazlı Baskın Bant Dağılımı")
        plt.xlabel("Dominant Frequency Band" if lang == "en" else "Baskın Frekans Bandı")
        plt.ylabel("Percentage (%)" if lang == "en" else "Yüzde (%)")
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig("temporal_distribution.png", dpi=300)
        plt.close()


       

        

        band_numeric_map = {
            "delta": 1,
            "theta": 2,
            "alpha": 3,
            "beta": 4
        }

        timeline_x = [seg["segment"] for seg in base_segment_results]
        timeline_y = [band_numeric_map.get(seg["dominant_band"], 0) for seg in base_segment_results]

        plt.figure(figsize=(10, 3.5))

        if len(timeline_x) == 1:
            plt.scatter(timeline_x, timeline_y, s=120)
            plt.text(timeline_x[0], timeline_y[0] + 0.1, "Single Segment", ha='center')
        else:
            plt.step(timeline_x, timeline_y, where="mid", linewidth=2)

        plt.yticks([1, 2, 3, 4], ["DELTA", "THETA", "ALPHA", "BETA"])
        plt.xlabel("Segment Number")
        plt.ylabel("Dominant Band")
        plt.title("Temporal Dominant Band Timeline")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("temporal_timeline.png", dpi=300)
        plt.close()

        pdf_file = create_report(
            avg_features=avg_features,
            ratios=ratios,
            yorum=yorum,
            channel_count=len(clean_data),
            sampling_rate=loader.sampling_rate,
            peak_freq=peak_freq,
            avg_p2p=avg_p2p,
            brain_state=brain_state,
            signal_quality=signal_quality,
            band_ratios=band_ratios,
            channel_band_results=channel_band_results,
            regional_summary=regional_summary,
            dominant_band=dominant_band,
            global_comment=global_comment,
            regional_comments=regional_comments,
            alerts=alerts,
            recommendations=recommendations,
            artifact_flags=artifact_flags,
            topomap_created=topomap_created,
            segment_results=segment_results,
            segment_flags=segment_flags,
            state_profile=state_profile,
            global_summary=global_summary,
            analysis_scores=analysis_scores,
            file_name=os.path.basename(file_path),
            band_distribution=band_distribution,
            total_segments=total_segments,
            lang=lang
        )

        report_files[lang] = ensure_report_in_folder(pdf_file, lang)

        if lang == "tr":
            ui_values = {
                "yorum": yorum,
                "brain_state": brain_state,
                "signal_quality": signal_quality,
                "state_profile": state_profile,
                "global_summary": global_summary,
                "analysis_scores": analysis_scores
            }

    return {
        "pdf_name_tr": report_files.get("tr"),
        "pdf_name_en": report_files.get("en"),

        "channel_count": len(clean_data),
        "sampling_rate": loader.sampling_rate,
        "peak_freq": peak_freq,
        "avg_p2p": avg_p2p,
        "yorum": ui_values.get("yorum"),
        "ratios": ratios,
        "band_ratios": band_ratios,
        "brain_state": ui_values.get("brain_state"),
        "signal_quality": ui_values.get("signal_quality"),
        "regional_summary": regional_summary,
        "topomap_created": topomap_created,
        "state_profile": ui_values.get("state_profile"),
        "global_summary": ui_values.get("global_summary"),
        "analysis_scores": ui_values.get("analysis_scores"),
        "band_distribution": band_distribution,
        "total_segments": total_segments
    }