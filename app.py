import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from main import run_analysis

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
REPORT_FOLDER = BASE_DIR / "reports"

TR_REPORT_FOLDER = REPORT_FOLDER / "tr"
EN_REPORT_FOLDER = REPORT_FOLDER / "en"

ALLOWED_EXTENSIONS = {"edf", "csv", "mat"}

UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORT_FOLDER.mkdir(exist_ok=True)
TR_REPORT_FOLDER.mkdir(exist_ok=True)
EN_REPORT_FOLDER.mkdir(exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["REPORT_FOLDER"] = str(REPORT_FOLDER)
app.config["TR_REPORT_FOLDER"] = str(TR_REPORT_FOLDER)
app.config["EN_REPORT_FOLDER"] = str(EN_REPORT_FOLDER)

app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None

    if request.method == "POST":
        if "file" not in request.files:
            error_message = "Dosya yüklenemedi."
            return render_template("index.html", error_message=error_message)

        file = request.files["file"]

        if file.filename == "":
            error_message = "Dosya seçilmedi."
            return render_template("index.html", error_message=error_message)

        if not allowed_file(file.filename):
            error_message = "Desteklenmeyen dosya formatı. Lütfen .edf, .csv veya .mat dosyası yükleyin."
            return render_template("index.html", error_message=error_message)

        file_path = None

        try:
            original_filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            unique_filename = f"{unique_id}_{original_filename}"
            file_path = UPLOAD_FOLDER / unique_filename

            file.save(str(file_path))

            result = run_analysis(str(file_path))

            pdf_name_tr = result.get("pdf_name_tr")
            pdf_name_en = result.get("pdf_name_en")

            return render_template(
                "result.html",
                channel_count=result.get("channel_count"),
                sampling_rate=result.get("sampling_rate"),
                peak_freq=result.get("peak_freq"),
                avg_p2p=result.get("avg_p2p"),
                yorum=result.get("yorum"),
                ratios=result.get("ratios"),
                brain_state=result.get("brain_state"),
                signal_quality=result.get("signal_quality"),
                analysis_scores=result.get("analysis_scores"),
                pdf_name_tr=pdf_name_tr,
                pdf_name_en=pdf_name_en
            )

        except Exception as e:
            error_message = f"Analiz sırasında bir hata oluştu: {str(e)}"
            return render_template("index.html", error_message=error_message)

        finally:
            if file_path and file_path.exists():
                try:
                    os.remove(str(file_path))
                except Exception:
                    pass

    return render_template("index.html", error_message=error_message)


@app.route("/download/<lang>/<filename>")
def download_report(lang, filename):
    safe_filename = secure_filename(filename)

    if lang == "tr":
        folder = app.config["TR_REPORT_FOLDER"]
    elif lang == "en":
        folder = app.config["EN_REPORT_FOLDER"]
    else:
        return "Geçersiz rapor dili.", 400

    return send_from_directory(
        folder,
        safe_filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)