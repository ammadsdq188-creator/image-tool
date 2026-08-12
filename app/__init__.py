from flask import Flask, render_template

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        error="File is too large. Maximum size is 10 MB."
    ), 413