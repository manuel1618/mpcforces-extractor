import webbrowser
import threading
import time
import uvicorn
from mpcforces_extractor.api.main import app


def open_browser():
    """
    Opens the browser to the main page of the app
    """
    # Delay opening the browser to allow the server to start
    time.sleep(1)  # Adjust the delay as needed
    webbrowser.open("http://127.0.0.1:8000/", new=2)


def main():
    """
    This is the main function that is used to run MPCForceExtractor
    """
    # Start a new thread to open the browser shortly after the server starts
    threading.Thread(target=open_browser).start()

    # Run the uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
