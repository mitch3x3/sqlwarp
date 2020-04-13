# sqlwrap
Simple wrapper for various database libraries

# Set up package for distribution
poetry init
poetry add psycopg2-binary
poetry install
poetry run python main.py
poetry build
poetry publish
