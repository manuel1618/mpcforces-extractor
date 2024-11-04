import uvicorn
from mpcforces_extractor.api.main import app


def main():
    """
    This is the main function that is used to run MPCForceExtractor
    """
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
