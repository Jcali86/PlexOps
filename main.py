from api import create_app
from config import config

app = create_app()

if __name__ == "__main__":
    app.run(
        host=config["flask"]["host"],
        port=config["flask"]["port"],
        debug=config["flask"].get("debug", False),
    )
