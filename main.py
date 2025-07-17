import os
import logging
from dotenv import load_dotenv

from _flask import app

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    handlers=[
                        logging.StreamHandler()
                    ],
                    format="[%(asctime)s][%(levelname)s] - %(message)s")

api_key = os.environ.get("API_KEY")
endpoint = os.environ.get("ENDPOINT")
            
if __name__ == "__main__":
    app.run(debug=True, threaded=True)