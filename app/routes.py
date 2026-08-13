from app import app
from flask import render_template, request, Response
from PIL import Image
import io
import base64

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        image = request.files["image"]

        if not image or image.filename == "":
            return render_template(
                "index.html",
                error="Please select an image."
            )

        try:
            image_bytes = image.read()
            original_size = len(image_bytes)

            img = Image.open(io.BytesIO(image_bytes))
            img.load()

        except Exception:
            return render_template(
                "index.html",
                error="Invalid image file."
            )

        original_format = img.format

        if original_format not in ALLOWED_FORMATS:
            return render_template(
                "index.html",
                error="Unsupported image format. Use JPG, PNG, or WebP."
            )

        original_width, original_height = img.size

        try:
            width = int(request.form["width"])
            height = int(request.form["height"])
            quality = int(request.form["quality"])
        except (TypeError, ValueError):
            return render_template(
                "index.html",
                error="Please enter valid dimensions and quality."
            )

        if width < 1 or width > 5000:
            return render_template(
                "index.html",
                error="Width must be between 1 and 5000."
            )

        if height < 1 or height > 5000:
            return render_template(
                "index.html",
                error="Height must be between 1 and 5000."
            )

        if quality < 10 or quality > 100:
            return render_template(
                "index.html",
                error="Quality must be between 10 and 100."
            )

        resized = img.resize((width, height))

        if original_format == "JPEG":
            if resized.mode != "RGB":
                resized = resized.convert("RGB")

        output = io.BytesIO()

        # JPEG: quality controls compression.
        if original_format == "JPEG":

            resized.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True
            )

        # WebP: quality also controls compression.
        elif original_format == "WEBP":

            resized.save(
                output,
                format="WEBP",
                quality=quality,
                method=6
            )

        # PNG: use lossless optimization.
        else:

            resized.save(
                output,
                format="PNG",
                optimize=True
            )

        output.seek(0)

        output_bytes = output.getvalue()
        output_size = len(output_bytes)

        if original_size > 0:
            saved_percent = max(
                0,
                round((1 - output_size / original_size) * 100)
            )
        else:
            saved_percent = 0

        extension = original_format.lower()

        if extension == "jpeg":
            mime_type = "image/jpeg"
        elif extension == "png":
            mime_type = "image/png"
        else:
            mime_type = "image/webp"

        image_data = base64.b64encode(
            output_bytes
        ).decode("utf-8")

        image_data = (
            f"data:{mime_type};base64,{image_data}"
        )

        return render_template(
            "result.html",
            image_data=image_data,
            original_width=original_width,
            original_height=original_height,
            width=width,
            height=height,
            original_size=original_size,
            output_size=output_size,
            saved_percent=saved_percent,
            filename=f"resized-image.{extension}"
        )

    return render_template("index.html")

@app.route("/robots.txt")
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: http://13.219.184.188/sitemap.xml\n",
        mimetype="text/plain",
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://13.219.184.188/</loc>
    </url>
</urlset>
"""
    return Response(xml, mimetype="application/xml")


@app.route("/privacy")
def privacy():
    return render_template("legal/privacy.html")


@app.route("/terms")
def terms():
    return render_template("legal/terms.html")


@app.route("/about")
def about():
    return render_template("legal/about.html")


@app.route("/contact")
def contact():
    return render_template("legal/contact.html")
