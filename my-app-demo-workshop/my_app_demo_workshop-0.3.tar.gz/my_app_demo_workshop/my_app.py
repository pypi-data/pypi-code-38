import argparse
from flask import Flask, render_template

from .quote_generator import random_quote

app = Flask(__name__)
DEFAULT_PORT = 5000


@app.route("/")
def home():
    return render_template('home.html', text=random_quote())


def main():
    parser = argparse.ArgumentParser(description='Workshop demo app.')
    parser.add_argument('-port', default=DEFAULT_PORT,
                        help=f'the port for the web app, default value is  {DEFAULT_PORT}')

    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)


if __name__ == "__main__":
    main()
