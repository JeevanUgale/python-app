"""Module entrypoint so the package can be executed with `python -m python_app`."""
import os

from .app import create_app


def main():
    """Create and run the Flask app using env vars HOST/PORT."""
    app = create_app()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    debug = app.config.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
