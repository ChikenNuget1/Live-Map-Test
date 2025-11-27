from live_map import create_app

import threading
from live_map.api.api import serial_reader

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
