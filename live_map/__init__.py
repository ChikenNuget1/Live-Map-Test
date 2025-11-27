from flask import Flask, render_template
from .api.api import api_bp, serial_reader
import threading


def create_app():
    app = Flask(
        __name__,
        static_folder="static",       # live_map/static
        template_folder="templates"   # live_map/templates
    )

    # Register /api blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    # Start serial-reading thread
    threading.Thread(target=serial_reader, args=("COM3", 9600), daemon=True).start()

    # Route for home page (map)
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
