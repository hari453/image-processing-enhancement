from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
PROCESSED_DIR = BASE_DIR / "processed"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_IMAGE_SIZE = (2200, 2200)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def clamp_float(value, default, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def save_image(file_storage):
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid4().hex}.{extension}"
    upload_path = UPLOAD_DIR / filename
    file_storage.save(upload_path)
    return filename


def apply_adjustments(image, options):
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail(MAX_IMAGE_SIZE)

    brightness = clamp_float(options.get("brightness"), 1, 0.2, 2.5)
    contrast = clamp_float(options.get("contrast"), 1, 0.2, 2.5)
    sharpness = clamp_float(options.get("sharpness"), 1, 0, 3)
    saturation = clamp_float(options.get("saturation"), 1, 0, 2.5)
    blur = clamp_float(options.get("blur"), 0, 0, 8)
    operation = options.get("operation", "enhance")

    image = ImageEnhance.Brightness(image).enhance(brightness)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Sharpness(image).enhance(sharpness)
    image = ImageEnhance.Color(image).enhance(saturation)

    if blur > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))

    if operation == "grayscale":
        image = ImageOps.grayscale(image).convert("RGB")
    elif operation == "invert":
        image = ImageOps.invert(image)
    elif operation == "edges":
        image = image.filter(ImageFilter.FIND_EDGES)
    elif operation == "emboss":
        image = image.filter(ImageFilter.EMBOSS)

    return image


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/process")
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "Please upload an image."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "Please choose an image file."}), 400

    if not allowed_file(image_file.filename):
        return jsonify({"error": "Only PNG, JPG, JPEG, and WEBP images are supported."}), 400

    try:
        source_filename = save_image(image_file)
        source_path = UPLOAD_DIR / source_filename

        with Image.open(source_path) as image:
            processed = apply_adjustments(image, request.form)

        output_filename = f"{Path(source_filename).stem}_processed.jpg"
        output_path = PROCESSED_DIR / output_filename
        processed.save(output_path, quality=92, optimize=True)

        return jsonify(
            {
                "original_url": f"/uploads/{source_filename}",
                "processed_url": f"/processed/{output_filename}",
                "download_url": f"/download/{output_filename}",
            }
        )
    except Exception:
        return jsonify({"error": "The image could not be processed. Try another file."}), 500


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/processed/<path:filename>")
def processed_file(filename):
    return send_from_directory(PROCESSED_DIR, filename)


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(PROCESSED_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
