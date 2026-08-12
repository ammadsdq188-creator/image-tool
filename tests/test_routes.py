import io

from PIL import Image

from run import app as flask_app


def create_test_image(image_format="JPEG"):
    image = Image.new("RGB", (100, 80), "white")

    output = io.BytesIO()
    image.save(output, format=image_format)
    output.seek(0)

    return output


def test_home_page():
    client = flask_app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Resize Images in Seconds" in response.data


def test_invalid_image():
    client = flask_app.test_client()

    response = client.post(
        "/",
        data={
            "image": (
                io.BytesIO(b"this is not an image"),
                "test.txt"
            ),
            "width": "500",
            "height": "400",
            "quality": "80",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Invalid image file." in response.data


def test_invalid_width():
    client = flask_app.test_client()

    image = create_test_image()

    response = client.post(
        "/",
        data={
            "image": (image, "test.jpg"),
            "width": "6000",
            "height": "400",
            "quality": "80",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Width must be between 1 and 5000." in response.data


def test_resize_jpeg():
    client = flask_app.test_client()

    image = create_test_image("JPEG")

    response = client.post(
        "/",
        data={
            "image": (image, "test.jpg"),
            "width": "50",
            "height": "40",
            "quality": "80",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Image Resized Successfully" in response.data


def test_resize_png():
    client = flask_app.test_client()

    image = create_test_image("PNG")

    response = client.post(
        "/",
        data={
            "image": (image, "test.png"),
            "width": "50",
            "height": "40",
            "quality": "80",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Image Resized Successfully" in response.data