from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, LongTable, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from datetime import datetime
import os


TEXTS = {
    "tr": {
        "company_name": "Neurovia",
        "platform_name": "Neurovia EEG Analiz Platformu",
        "website_info": "www.neurovia.ai | info@neurovia.ai | +90 XXX XXX XX XX",
        "report_title": "EEG Analiz Raporu",

        "clinical_summary": "Analitik Ön Değerlendirme",
        "classification": "Otomatik Değerlendirme",
        "key_finding": "Temel Bulgu",
        "interpretation": "Analitik Yorum",
        "confidence": "Güven Düzeyi",
        "normal": "Beklenen Aralıkta",
        "abnormal": "Dikkat Gerektiren Örüntü",
        "borderline": "Sınırda Örüntü",

        "executive_summary": "Yönetici Özeti",
        "analysis_scores": "Analiz Skorları",
        "metric": "Metrik",
        "score": "Skor",
        "stability_score": "Stabilite Skoru",
        "relaxation_score": "Relaksasyon Skoru",
        "alertness_score": "Uyanıklık Skoru",
        "score_note": (
            "Bu skorlar spektral denge, zamansal stabilite ve baskın aktivite dağılımından "
            "türetilen otomatik analitik destek metrikleridir. Tek başına klinik skor veya tanı ölçütü olarak kullanılmamalıdır."
        ),

        "report_date": "Rapor Tarihi",
        "file_name": "Dosya Adı",
        "channel_count": "Kanal Sayısı",
        "sampling_rate": "Örnekleme Hızı",
        "peak_frequency": "Tepe Frekansı",
        "avg_p2p": "Ortalama Peak-to-Peak Genlik",
        "report_id": "Rapor ID",

        "method_summary": "Yöntem Özeti",
        "method_text": (
            "Yüklenen EEG verisi kanal-örnek yapısına standardize edilmiştir. Ön işleme aşamasında "
            "bant geçiren filtreleme, notch filtreleme ve normalizasyon uygulanmıştır. Frekans alanı analizi için "
            "Güç Spektral Yoğunluğu (PSD) hesaplanmış; delta, theta, alpha ve beta bant güçleri çıkarılmıştır. "
            "Ek olarak tepe frekansı, peak-to-peak genlik, bölgesel dağılım, segment bazlı değişim ve temel "
            "artefakt tarama göstergeleri rapora dahil edilmiştir."
        ),

        "band_power_results": "Bant Gücü Sonuçları",
        "global_interpretation": "Genel Beyin Aktivitesi Yorumu",
        "global_state_profile": "Genel Durum Profili",
        "dominant_band": "Baskın Bant",

        "temporal_analysis": "Genel Zamansal Analiz",
        "temporal_note": "Bu tablo, kaydın iki dakikalık segmentlere ayrılmasıyla elde edilen baskın bant dağılımını gösterir.",
        "total_segments": "Toplam Analiz Edilen Segment",
        "percentage": "Yüzde (%)",

        "segment_analysis": "Segment Bazlı Analiz",
        "segment_summary": "Segment Analizi Özeti",
        "segment_flags": "Segment Bazlı Analitik Uyarılar",

        "segment": "Segment",
        "start": "Başlangıç",
        "end": "Bitiş",
        "state": "Durum",
        "region": "Bölge",
        "channel_no": "Kanal No",
        "channel_name": "Kanal Adı",

        "regional_summary": "Bölgesel Özet",
        "regional_analysis": "Bölgesel Beyin Aktivitesi Analizi",

        "band": "Bant",
        "power_value": "Güç Değeri",
        "relative_power": "Göreceli Güç (%)",

        "relative_interpretation": "Göreceli Bant Yorumu",
        "relative_interpretation_text": "Delta: Yüksek<br/>Alpha: Baskılanmış<br/>Beta: Düşük-normal",
        "relative_interpretation_comment": (
            "Bu örüntü tam uyanıklık profilinden ziyade azalmış kortikal aktivasyon, uykululuk "
            "veya yavaş dalga baskınlığı ile uyumlu olabilir."
        ),

        "interpretation_section": "Genel Yorum",
        "advanced_analysis": "İleri Analiz",
        "brain_state": "Beyin Durumu",
        "signal_quality": "Sinyal Kalitesi",
        "artifact_screening": "Artefakt Taraması",
        "advanced_ratios": "İleri Oranlar",

        "figures": "Şekiller",
        "clinical_flags": "Analitik Uyarılar",
        "recommended_next_steps": "Önerilen Sonraki Adımlar",
        "limitations": "Kısıtlılıklar",
        "conclusion": "Sonuç",
        "disclaimer": "Sorumluluk Reddi",

        "classification_abnormal_finding": "Baskın delta aktivitesi ve baskılanmış alpha aktivitesi gözlenmiştir.",
        "classification_abnormal_interpretation": (
            "Bu bulgular azalmış kortikal aktivasyon, uykululuk veya yavaş dalga baskınlığı ile uyumlu olabilir."
        ),
        "classification_normal_finding": "Belirgin baskın dikkat gerektiren spektral örüntü saptanmamıştır.",
        "classification_normal_interpretation": (
            "EEG profili otomatik spektral değerlendirme kapsamında beklenen aralıkta görünmektedir."
        ),
        "confidence_moderate": "Orta",

        "segment_summary_text": (
            "Segmentler boyunca baskın aktivite örüntüsü zaman ekseninde değerlendirilmiştir. "
            "Belirgin bant değişimleri ve segmentler arası dalgalanmalar otomatik olarak işaretlenmiştir."
        ),
        "regional_summary_text": (
            "Bölgesel bant dağılımları frontal, central, parietal ve occipital alanlar üzerinden özetlenmiştir. "
            "Bu bölüm, fokal ya da yaygın spektral baskınlıkların ön analitik değerlendirilmesini destekler."
        ),

        "limitations_text": (
            "- Otomatik analiz spektral özelliklere ve ön tanımlı kurallara dayanmaktadır.<br/>"
            "- Klinik tanı için uzman hekim değerlendirmesi gereklidir.<br/>"
            "- Kayıt kalitesi, elektrot yerleşimi, artefaktlar ve kayıt koşulları sonucu etkileyebilir.<br/>"
            "- Bu rapor karar destek niteliğindedir; tek başına klinik karar aracı değildir."
        ),
        "conclusion_text": (
            "Elde edilen spektral, zamansal ve bölgesel metrikler EEG kaydının yapılandırılmış biçimde "
            "incelenmesine destek sağlar. Bulgular, araştırma amaçlı değerlendirme, ön analitik yorum ve "
            "ileri inceleme planlaması açısından kullanılabilir."
        ),
        "disclaimer_text": (
            "Bu rapor araştırma desteği ve analitik değerlendirme amacıyla hazırlanmıştır. "
            "Tek başına klinik tanı, tedavi kararı veya nihai tıbbi değerlendirme amacıyla kullanılmamalıdır."
        ),

        "figure_1": "Şekil 1. Ön işlenmiş temsili EEG sinyali.",
        "figure_2": "Şekil 2. Temsili EEG kanalına ait Güç Spektral Yoğunluğu (PSD).",
        "figure_3": "Şekil 3. Analiz edilen EEG kanallarında alpha bant gücü ısı haritası.",
        "figure_4": "Şekil 4. Delta, theta, alpha ve beta frekans bantlarına ait güç dağılımı.",
        "figure_5": "Şekil 5. Alpha bandına ait topografik kafa haritası.",
        "figure_6": "Şekil 6. Segment bazlı bant gücü değişim grafiği.",
        "figure_7": "Şekil 7. Segmentler boyunca delta gücü değişimi.",
        "figure_8": "Şekil 8. Segmentler boyunca alpha gücü değişimi.",
        "figure_9": "Şekil 9. Segmentler boyunca beta gücü değişimi.",
        "figure_10": "Şekil 10. Segment bazlı baskın bant dağılım grafiği.",
        "figure_11": "Şekil 11. Zamansal baskın bant zaman çizelgesi.",
    },

    "en": {
        "company_name": "Neurovia",
        "platform_name": "Neurovia EEG Analysis Platform",
        "website_info": "www.neurovia.ai | info@neurovia.ai | +90 XXX XXX XX XX",
        "report_title": "EEG Analysis Report",

        "clinical_summary": "Analytical Pre-Assessment",
        "classification": "Automated Evaluation",
        "key_finding": "Key Finding",
        "interpretation": "Analytical Interpretation",
        "confidence": "Confidence Level",
        "normal": "Within Expected Range",
        "abnormal": "Pattern Requiring Attention",
        "borderline": "Borderline Pattern",

        "executive_summary": "Executive Summary",
        "analysis_scores": "Analysis Scores",
        "metric": "Metric",
        "score": "Score",
        "stability_score": "Stability Score",
        "relaxation_score": "Relaxation Score",
        "alertness_score": "Alertness Score",
        "score_note": (
            "These scores are automated analytical support metrics derived from spectral balance, "
            "temporal stability, and dominant activity distribution. They should not be used as standalone clinical scores."
        ),

        "report_date": "Report Date",
        "file_name": "File Name",
        "channel_count": "Channel Count",
        "sampling_rate": "Sampling Rate",
        "peak_frequency": "Peak Frequency",
        "avg_p2p": "Average Peak-to-Peak Amplitude",
        "report_id": "Report ID",

        "method_summary": "Methodology Summary",
        "method_text": (
            "The uploaded EEG data was standardized to a channel-sample structure. Preprocessing steps "
            "included band-pass filtering, notch filtering, and normalization. Power Spectral Density (PSD) was calculated "
            "for frequency domain analysis; delta, theta, alpha, and beta band powers were extracted. Additionally, "
            "peak frequency, peak-to-peak amplitude, regional distribution, segment-based variation, and basic artifact "
            "screening indicators are included."
        ),

        "band_power_results": "Band Power Results",
        "global_interpretation": "Global Brain Activity Interpretation",
        "global_state_profile": "Global State Profile",
        "dominant_band": "Dominant Band",

        "temporal_analysis": "Global Temporal Analysis",
        "temporal_note": "This table shows the dominant band distribution obtained by dividing the recording into two-minute segments.",
        "total_segments": "Total Analyzed Segments",
        "percentage": "Percentage (%)",

        "segment_analysis": "Segment-Based Analysis",
        "segment_summary": "Segment Analysis Summary",
        "segment_flags": "Segment-Based Analytical Alerts",

        "segment": "Segment",
        "start": "Start",
        "end": "End",
        "state": "State",
        "region": "Region",
        "channel_no": "Channel No",
        "channel_name": "Channel Name",

        "regional_summary": "Regional Summary",
        "regional_analysis": "Regional Brain Activity Analysis",

        "band": "Band",
        "power_value": "Power Value",
        "relative_power": "Relative Power (%)",

        "relative_interpretation": "Relative Band Interpretation",
        "relative_interpretation_text": "Delta: High<br/>Alpha: Suppressed<br/>Beta: Low-normal",
        "relative_interpretation_comment": (
            "This pattern may be consistent with decreased cortical activation, drowsiness, "
            "or slow-wave dominance rather than a fully alert profile."
        ),

        "interpretation_section": "General Interpretation",
        "advanced_analysis": "Advanced Analysis",
        "brain_state": "Brain State",
        "signal_quality": "Signal Quality",
        "artifact_screening": "Artifact Screening",
        "advanced_ratios": "Advanced Ratios",

        "figures": "Figures",
        "clinical_flags": "Analytical Alerts",
        "recommended_next_steps": "Recommended Next Steps",
        "limitations": "Limitations",
        "conclusion": "Conclusion",
        "disclaimer": "Disclaimer",

        "classification_abnormal_finding": "Dominant delta activity and suppressed alpha activity were observed.",
        "classification_abnormal_interpretation": (
            "These findings may be consistent with decreased cortical activation, drowsiness, or slow-wave dominance."
        ),
        "classification_normal_finding": "No distinct dominant spectral pattern requiring attention was detected.",
        "classification_normal_interpretation": (
            "The EEG profile appears to be within the expected range under automated spectral evaluation."
        ),
        "confidence_moderate": "Moderate",

        "segment_summary_text": (
            "The dominant activity pattern was evaluated across segments over the time axis. "
            "Significant band changes and inter-segment fluctuations were automatically flagged."
        ),
        "regional_summary_text": (
            "Regional band distributions are summarized across frontal, central, parietal, and occipital areas. "
            "This section supports the pre-analytical evaluation of focal or generalized spectral dominances."
        ),

        "limitations_text": (
            "- Automated analysis is based on spectral features and predefined rules.<br/>"
            "- Expert physician evaluation is required for clinical diagnosis.<br/>"
            "- Recording quality, electrode placement, artifacts, and recording conditions can affect the results.<br/>"
            "- This report is for decision support; it is not a standalone clinical decision tool."
        ),
        "conclusion_text": (
            "The obtained spectral, temporal, and regional metrics support the structured examination of the EEG recording. "
            "The findings can be used for research evaluation, pre-analytical interpretation, and planning of further investigation."
        ),
        "disclaimer_text": (
            "This report is prepared for research support and analytical evaluation purposes. "
            "It must not be used solely for clinical diagnosis, treatment decisions, or final medical evaluation."
        ),

        "figure_1": "Figure 1. Preprocessed representative EEG signal.",
        "figure_2": "Figure 2. Power Spectral Density (PSD) of the representative EEG channel.",
        "figure_3": "Figure 3. Alpha band power heatmap across analyzed EEG channels.",
        "figure_4": "Figure 4. Power distribution of delta, theta, alpha, and beta frequency bands.",
        "figure_5": "Figure 5. Topographic head map of the alpha band.",
        "figure_6": "Figure 6. Segment-based band power trend graph.",
        "figure_7": "Figure 7. Delta power trend across segments.",
        "figure_8": "Figure 8. Alpha power trend across segments.",
        "figure_9": "Figure 9. Beta power trend across segments.",
        "figure_10": "Figure 10. Segment-based dominant band distribution graph.",
        "figure_11": "Figure 11. Temporal dominant band timeline.",
    }
}


def register_fonts():
    font_path = "C:/Windows/Fonts/arial.ttf"
    bold_path = "C:/Windows/Fonts/arialbd.ttf"

    if os.path.exists(font_path) and os.path.exists(bold_path):
        pdfmetrics.registerFont(TTFont("Arial", font_path))
        pdfmetrics.registerFont(TTFont("Arial-Bold", bold_path))
        return "Arial", "Arial-Bold"

    return "Helvetica", "Helvetica-Bold"


def get_styles(regular_font="Helvetica", bold_font="Helvetica-Bold"):
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CustomCenterTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=21,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0A1F44"),
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="CustomSubTitle",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=13,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="CustomSectionTitle",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0A1F44"),
        spaceBefore=10,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="CustomBody",
        parent=styles["Normal"],
        fontName=regular_font,
        fontSize=10,
        leading=14,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="CustomSmall",
        parent=styles["Normal"],
        fontName=regular_font,
        fontSize=8.5,
        leading=11,
        spaceAfter=4,
        textColor=colors.HexColor("#555555")
    ))

    return styles


def add_page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.darkgrey)
    canvas.drawString(40, 20, "Generated by Neurovia | Research Support Report | © 2026")
    canvas.drawRightString(555, 20, f"Page {doc.page}")
    canvas.restoreState()


def safe_text(value, default="-"):
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return str(value)


def generate_clinical_summary(avg_features, lang="tr"):
    t = TEXTS.get(lang, TEXTS["tr"])

    delta = float(avg_features.get("delta", 0.0))
    alpha = float(avg_features.get("alpha", 0.0))

    if delta > 0.4 and alpha < 0.02:
        classification = "abnormal"
        finding = t["classification_abnormal_finding"]
        interpretation = t["classification_abnormal_interpretation"]
    else:
        classification = "normal"
        finding = t["classification_normal_finding"]
        interpretation = t["classification_normal_interpretation"]

    return {
        "classification": classification,
        "finding": finding,
        "interpretation": interpretation,
        "confidence": t["confidence_moderate"]
    }


def create_report(
    avg_features, ratios, yorum, channel_count, sampling_rate, peak_freq,
    avg_p2p, brain_state, signal_quality, band_ratios, channel_band_results,
    regional_summary, dominant_band, global_comment, regional_comments,
    alerts, recommendations, artifact_flags, topomap_created, segment_results,
    segment_flags, state_profile, global_summary, analysis_scores,
    file_name="EEG Data", lang="tr",
    band_distribution=None, total_segments=None
):
    t = TEXTS.get(lang, TEXTS["tr"])

    now = datetime.now()
    report_date = now.strftime("%Y-%m-%d %H:%M:%S")
    report_date_file = now.strftime("%Y%m%d_%H%M%S")
    pdf_name = f"EEG_Report_{report_date_file}_{lang}.pdf"
    report_id = f"EEG-{report_date_file}-{lang.upper()}"

    doc = SimpleDocTemplate(
        pdf_name,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    regular_font, bold_font = register_fonts()
    styles = get_styles(regular_font, bold_font)

    title_style = styles["CustomCenterTitle"]
    subtitle_style = styles["CustomSubTitle"]
    section_style = styles["CustomSectionTitle"]
    body_style = styles["CustomBody"]
    small_style = styles["CustomSmall"]

    content = []

    logo_path = os.path.join("static", "logo.png")
    if os.path.exists(logo_path):
        content.append(Image(logo_path, width=110, height=55))
        content.append(Spacer(1, 8))
    elif os.path.exists("logo.png"):
        content.append(Image("logo.png", width=110, height=55))
        content.append(Spacer(1, 8))

    content.append(Paragraph(t["company_name"], title_style))
    content.append(Paragraph(t["platform_name"], subtitle_style))
    content.append(Paragraph(t["website_info"], small_style))
    content.append(Spacer(1, 8))
    content.append(Paragraph(t["report_title"], title_style))
    content.append(Paragraph(f"{t['report_id']}: {report_id}", small_style))
    content.append(Spacer(1, 12))

    clinical = generate_clinical_summary(avg_features, lang)

    clinical_table = Table([
        [Paragraph(f"<b>{t['clinical_summary']}</b>", body_style)],
        [Paragraph(f"<b>{t['classification']}:</b> {t[clinical['classification']]}", body_style)],
        [Paragraph(f"<b>{t['key_finding']}:</b> {clinical['finding']}", body_style)],
        [Paragraph(f"<b>{t['interpretation']}:</b> {clinical['interpretation']}", body_style)],
        [Paragraph(f"<b>{t['confidence']}:</b> {clinical['confidence']}", body_style)],
    ], colWidths=[500])

    clinical_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEBFA")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1F4E79")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))

    content.append(clinical_table)
    content.append(Spacer(1, 14))

    content.append(Paragraph(t["executive_summary"], section_style))
    content.append(Paragraph(safe_text(global_summary), body_style))
    content.append(Spacer(1, 10))

   

    content.append(Spacer(1, 10))
    content.append(Paragraph("Key Findings" if lang == "en" else "Temel Bulgular", section_style))

    

    key_findings = []

    # Delta baskınlık
    if band_distribution and band_distribution.get("delta", 0) > 60:
        key_findings.append(
            "Delta dominant pattern across majority of segments."
            if lang == "en"
            else "Segmentlerin büyük çoğunluğunda delta baskın aktivite gözlenmiştir."
        )

    # Uyanıklık düşük
    if analysis_scores and analysis_scores.get("alertness_score", 0) < 20:
        key_findings.append(
            "Very low alertness level detected."
            if lang == "en"
            else "Çok düşük uyanıklık seviyesi tespit edilmiştir."
        )

    # Sinyal kalitesi
    if signal_quality and "Orta" in signal_quality:
        key_findings.append(
            "Moderate signal quality – interpretation requires caution."
            if lang == "en"
            else "Orta sinyal kalitesi – yorum dikkatli yapılmalıdır."
        )

    # fallback
    if not key_findings:
        key_findings.append(
            "No major abnormal pattern detected."
            if lang == "en"
            else "Belirgin anormal bir örüntü saptanmamıştır."
        )

    for k in key_findings:
        content.append(Paragraph(f"• {k}", body_style))

    content.append(Spacer(1, 10))

    content.append(Paragraph(t["analysis_scores"], section_style))

    score_table_data = [
        [t["metric"], t["score"]],
        [t["stability_score"], f"{analysis_scores.get('stability_score', 0)}/100"],
        [t["relaxation_score"], f"{analysis_scores.get('relaxation_score', 0)}/100"],
        [t["alertness_score"], f"{analysis_scores.get('alertness_score', 0)}/100"],
    ]

    score_table = Table(score_table_data, colWidths=[250, 120])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1F4E79")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(score_table)
    content.append(Spacer(1, 8))
    content.append(Paragraph(t["score_note"], small_style))
    content.append(Spacer(1, 12))

    metadata_rows = [
        [Paragraph(f"<b>{t['report_date']}:</b>", body_style), Paragraph(report_date, body_style)],
        [Paragraph(f"<b>{t['file_name']}:</b>", body_style), Paragraph(safe_text(file_name), body_style)],
        [Paragraph(f"<b>{t['channel_count']}:</b>", body_style), Paragraph(str(channel_count), body_style)],
        [Paragraph(f"<b>{t['sampling_rate']}:</b>", body_style), Paragraph(f"{sampling_rate} Hz", body_style)],
        [Paragraph(f"<b>{t['peak_frequency']}:</b>", body_style), Paragraph(f"{peak_freq:.2f} Hz", body_style)],
        [Paragraph(f"<b>{t['avg_p2p']}:</b>", body_style), Paragraph(f"{avg_p2p:.4f}", body_style)],
    ]

    metadata_table = Table(metadata_rows, colWidths=[170, 330])
    metadata_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8F9FB")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(metadata_table)
    content.append(Spacer(1, 12))

    content.append(Paragraph(t["method_summary"], section_style))
    content.append(Paragraph(t["method_text"], body_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["band_power_results"], section_style))

    band_table_data = [
        [t["band"], t["power_value"], t["relative_power"]],
        ["Delta (1-4 Hz)", f"{avg_features.get('delta', 0):.4f}", f"{ratios.get('delta', 0) * 100:.2f}%"],
        ["Theta (4-8 Hz)", f"{avg_features.get('theta', 0):.4f}", f"{ratios.get('theta', 0) * 100:.2f}%"],
        ["Alpha (8-13 Hz)", f"{avg_features.get('alpha', 0):.4f}", f"{ratios.get('alpha', 0) * 100:.2f}%"],
        ["Beta (13-30 Hz)", f"{avg_features.get('beta', 0):.4f}", f"{ratios.get('beta', 0) * 100:.2f}%"],
    ]

    band_table = Table(band_table_data, colWidths=[180, 120, 140])
    band_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1F4E79")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(band_table)
    content.append(Spacer(1, 12))

    content.append(Paragraph(t["global_interpretation"], section_style))
    content.append(Paragraph(f"<b>{t['global_state_profile']}:</b> {safe_text(state_profile)}", body_style))
    content.append(Paragraph(f"<b>{t['dominant_band']}:</b> {safe_text(dominant_band).upper()}", body_style))
    content.append(Paragraph(f"<b>{t['interpretation']}:</b> {safe_text(global_comment)}", body_style))
    content.append(Spacer(1, 10))

    if band_distribution:
        content.append(Paragraph(t["temporal_analysis"], section_style))
        content.append(Paragraph(t["temporal_note"], body_style))

        temporal_table_data = [
            [t["band"], t["percentage"]],
            ["Delta", f"{band_distribution.get('delta', 0):.1f}%"],
            ["Theta", f"{band_distribution.get('theta', 0):.1f}%"],
            ["Alpha", f"{band_distribution.get('alpha', 0):.1f}%"],
            ["Beta", f"{band_distribution.get('beta', 0):.1f}%"],
        ]

        temporal_table = Table(temporal_table_data, colWidths=[200, 180])
        temporal_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A1F44")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTNAME", (0, 1), (-1, -1), regular_font),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1F4E79")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        content.append(temporal_table)

        if total_segments is not None:
            content.append(Spacer(1, 6))
            content.append(Paragraph(f"<b>{t['total_segments']}:</b> {total_segments}", body_style))

        content.append(Spacer(1, 10))

    

    if band_distribution:
        content.append(Paragraph(
            "Temporal Interpretation" if lang == "en" else "Zamansal Yorum",
            section_style
        ))

        dominant = max(band_distribution, key=band_distribution.get)

        if lang == "tr":
            text = (
                f"Kayıt boyunca baskın aktivite {dominant.upper()} olarak gözlenmiştir. "
                "Segment bazlı analiz, zaman içinde değişkenlikler olabileceğini ve "
                "özellikle belirli aralıklarda farklı bantların öne çıkabileceğini göstermektedir."
            )
        else:
            text = (
                f"The dominant activity throughout the recording was {dominant.upper()}. "
                "Segment-based analysis suggests temporal variability, with possible transitions "
                "between different frequency bands over time."
            )

        content.append(Paragraph(text, body_style))
        content.append(Spacer(1, 10))

    content.append(Paragraph(t["segment_analysis"], section_style))

    segment_table_data = [[
        t["segment"], t["start"], t["end"],
        "Delta", "Theta", "Alpha", "Beta",
        t["dominant_band"], t["state"]
    ]]

    for seg in segment_results:
        segment_table_data.append([
            str(seg.get("segment", "-")),
            f"{seg.get('start_sec', 0):.0f}",
            f"{seg.get('end_sec', 0):.0f}",
            f"{seg.get('delta', 0):.4f}",
            f"{seg.get('theta', 0):.4f}",
            f"{seg.get('alpha', 0):.4f}",
            f"{seg.get('beta', 0):.4f}",
            safe_text(seg.get("dominant_band", "")).upper(),
            safe_text(seg.get("segment_state", "-"))
        ])

    segment_table = LongTable(
        segment_table_data,
        colWidths=[45, 45, 45, 50, 50, 50, 50, 80, 85],
        repeatRows=1
    )

    segment_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004C2E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F8F5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    content.append(segment_table)
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["segment_summary"], section_style))
    content.append(Paragraph(t["segment_summary_text"], body_style))
    content.append(Spacer(1, 8))

    if segment_flags:
        content.append(Paragraph(t["segment_flags"], section_style))
        max_flags_to_show = 25

        for flag in segment_flags[:max_flags_to_show]:
            content.append(Paragraph(f"- {safe_text(flag)}", body_style))

        if len(segment_flags) > max_flags_to_show:
            remaining = len(segment_flags) - max_flags_to_show
            extra_text = (
                f"- Ek olarak {remaining} segment bazlı uyarı daha otomatik olarak saptanmıştır."
                if lang == "tr"
                else f"- Additionally, {remaining} more segment-based alerts were automatically detected."
            )
            content.append(Paragraph(extra_text, body_style))

        content.append(Spacer(1, 8))

    content.append(Paragraph(t["regional_summary"], section_style))
    content.append(Paragraph(t["regional_summary_text"], body_style))
    content.append(Spacer(1, 8))

    regional_table_data = [[t["region"], "Delta", "Theta", "Alpha", "Beta"]]

    for region, values in regional_summary.items():
        regional_table_data.append([
            region.capitalize(),
            f"{values.get('delta', 0):.4f}",
            f"{values.get('theta', 0):.4f}",
            f"{values.get('alpha', 0):.4f}",
            f"{values.get('beta', 0):.4f}",
        ])

    regional_table = Table(regional_table_data, colWidths=[100, 90, 90, 90, 90])
    regional_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1F4E79")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(regional_table)
    content.append(Spacer(1, 10))

    channel_table_data = [[t["channel_no"], t["channel_name"], "Delta", "Theta", "Alpha", "Beta"]]

    
    for row in channel_band_results[:10]:
        channel_table_data.append([
            str(row.get("channel", "-")),
            safe_text(row.get("channel_name", "-")),
            f"{row.get('delta', 0):.4f}",
            f"{row.get('theta', 0):.4f}",
            f"{row.get('alpha', 0):.4f}",
            f"{row.get('beta', 0):.4f}",
        ])

    content.append(Spacer(1, 6))
    content.append(Paragraph(
        "Detaylı kanal verileri ek bölümde sunulmuştur."
        if lang == "tr"
        else "Full channel data is provided in the appendix.",
        small_style
    ))

    channel_table = LongTable(
        channel_table_data,
        colWidths=[65, 100, 75, 75, 75, 75],
        repeatRows=1
    )

    channel_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A4A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), bold_font),
        ("FONTNAME", (0, 1), (-1, -1), regular_font),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    content.append(channel_table)
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["regional_analysis"], section_style))

    for region, bands in regional_summary.items():
        content.append(Paragraph(f"<b>{region.capitalize()}</b>", body_style))
        content.append(Paragraph(
            f"Delta: {bands.get('delta', 0):.4f}, "
            f"Theta: {bands.get('theta', 0):.4f}, "
            f"Alpha: {bands.get('alpha', 0):.4f}, "
            f"Beta: {bands.get('beta', 0):.4f}",
            body_style
        ))

        if region in regional_comments:
            content.append(Paragraph(safe_text(regional_comments.get(region)), body_style))

        content.append(Spacer(1, 4))

    content.append(Paragraph(t["relative_interpretation"], section_style))
    content.append(Paragraph(t["relative_interpretation_text"], body_style))
    content.append(Paragraph(t["relative_interpretation_comment"], body_style))
    content.append(Spacer(1, 8))

    content.append(Paragraph(t["interpretation_section"], section_style))
    content.append(Paragraph(safe_text(yorum), body_style))
    content.append(Spacer(1, 10))

    

    content.append(Paragraph(
        "Clinical Considerations" if lang == "en" else "Klinik Değerlendirme",
        section_style
    ))

    if lang == "tr":
        text = (
            "Bu bulgular aşağıdaki durumlarla ilişkili olabilir:<br/>"
            "• Uykululuk veya uyku başlangıcı<br/>"
            "• Yorgunluk durumu<br/>"
            "• Azalmış uyanıklık seviyesi<br/><br/>"
            "Kesin klinik değerlendirme için uzman görüşü gereklidir."
        )
    else:
        text = (
            "Findings may be associated with:<br/>"
            "• Drowsiness or sleep onset<br/>"
            "• Fatigue<br/>"
            "• Reduced alertness<br/><br/>"
            "Clinical confirmation is required."
        )

    content.append(Paragraph(text, body_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(
        "Clinical Interpretation" if lang == "en" else "Klinik Yorum",
        section_style
    ))

    if lang == "tr":
        text = (
            "Elde edilen bulgular, düşük kortikal aktivasyon ve yavaş dalga baskınlığı ile uyumlu bir örüntü göstermektedir. "
            "Bu durum genellikle uykululuk, derin dinlenme veya azalmış uyanıklık seviyeleri ile ilişkilidir. "
            "Klinik bağlamda değerlendirilmesi önerilir."
        )
    else:
        text = (
            "Findings are consistent with reduced cortical activation and slow-wave dominance. "
            "This pattern is commonly associated with drowsiness, deep relaxation, or reduced alertness levels. "
            "Clinical correlation is recommended."
    )

    content.append(Paragraph(text, body_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["advanced_analysis"], section_style))
    content.append(Paragraph(f"<b>{t['brain_state']}:</b> {safe_text(brain_state)}", body_style))
    content.append(Paragraph(f"<b>{t['signal_quality']}:</b> {safe_text(signal_quality)}", body_style))
    content.append(Spacer(1, 8))

    content.append(Paragraph(t["artifact_screening"], section_style))

    for flag in artifact_flags:
        content.append(Paragraph(f"- {safe_text(flag)}", body_style))

    content.append(Spacer(1, 8))

    content.append(Paragraph(t["advanced_ratios"], section_style))
    content.append(Paragraph(f"Theta/Beta: {band_ratios.get('theta_beta', 0):.4f}", body_style))
    content.append(Paragraph(f"Alpha/Beta: {band_ratios.get('alpha_beta', 0):.4f}", body_style))
    content.append(Paragraph(f"Delta/Theta: {band_ratios.get('delta_theta', 0):.4f}", body_style))
    content.append(Spacer(1, 10))

   

    content.append(Paragraph(
        "Ratio Interpretation" if lang == "en" else "Oran Yorumları",
        section_style
    ))

    theta_beta = band_ratios.get("theta_beta", 0)
    alpha_beta = band_ratios.get("alpha_beta", 0)

    if lang == "tr":
        if theta_beta > 2:
            content.append(Paragraph("• Theta/Beta oranı yüksek → dikkat azalması veya yorgunluk ile ilişkili olabilir.", body_style))
        if alpha_beta < 1:
            content.append(Paragraph("• Alpha/Beta oranı düşük → artmış zihinsel yük veya stres göstergesi olabilir.", body_style))
    else:
        if theta_beta > 2:
            content.append(Paragraph("• Elevated Theta/Beta ratio may indicate reduced attention or fatigue.", body_style))
        if alpha_beta < 1:
            content.append(Paragraph("• Low Alpha/Beta ratio may reflect increased cognitive load or stress.", body_style))

    content.append(Spacer(1, 10))

    content.append(Paragraph(t["figures"], section_style))

    figure_items = [
        ("preprocessed_signal.png", t["figure_1"], 450, 220),
        ("psd_plot.png", t["figure_2"], 450, 220),
        ("alpha_heatmap.png", t["figure_3"], 420, 320),
        ("band_bar.png", t["figure_4"], 420, 260),
    ]

    if topomap_created:
        figure_items.append(("alpha_topomap.png", t["figure_5"], 420, 320))
    figure_items.extend([
        ("temporal_distribution.png", t["figure_10"], 420, 260),
        ("temporal_timeline.png", t["figure_11"], 450, 220),
    ])
    figure_items.extend([
        ("segment_trend.png", t["figure_6"], 420, 260),
        ("delta_trend.png", t["figure_7"], 420, 220),
        ("alpha_trend.png", t["figure_8"], 420, 220),
        ("beta_trend.png", t["figure_9"], 420, 220),
    ])

    for img_path, caption, width, height in figure_items:
        if os.path.exists(img_path):
            content.append(KeepTogether([
                Paragraph(caption, body_style),
                Spacer(1, 6),
                Image(img_path, width=width, height=height),
                Spacer(1, 10),
            ]))

    content.append(Paragraph(t["clinical_flags"], section_style))

    for alert in alerts:
        content.append(Paragraph(f"- {safe_text(alert)}", body_style))

    content.append(Spacer(1, 10))

    content.append(Paragraph(t["recommended_next_steps"], section_style))

    for rec in recommendations:
        content.append(Paragraph(f"- {safe_text(rec)}", body_style))

    content.append(Spacer(1, 10))

    content.append(Paragraph(t["limitations"], section_style))
    content.append(Paragraph(t["limitations_text"], body_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["conclusion"], section_style))
    content.append(Paragraph(t["conclusion_text"], body_style))
    content.append(Spacer(1, 10))

    content.append(Paragraph(t["disclaimer"], section_style))
    content.append(Paragraph(t["disclaimer_text"], body_style))

    doc.build(content, onFirstPage=add_page_footer, onLaterPages=add_page_footer)

    return pdf_name