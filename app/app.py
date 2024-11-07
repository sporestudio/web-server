from flask import Flask, render_template, request, redirect, url_for
from app import app
import hashlib

# TODO: Implement a function to redirect the short_url to the original url store in url_mapping

app = Flask(__name__)

# Global variables
DOMAIN_NAME = os.getenv('DOMAIN_NAME')

# Database with the short_url and its respectiive original_url
url_mapping = {}


def shortener_url(original_url):
    return hashlib.sha256(original_url.encode()).hexdigest()[:6]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = shortener_url(original_url) 
        url_mapping[short_url] = original_url
        return render_template('index.html', short_url=short_url, original_url=original_url)
    return render_template('index.html')
    

@app.route('/<short_url>')
def redirect_url(short_url):
    if short_url in url_mapping:
        return redirect(url_mapping[original_url])
    else:
        return f"{short_url} url no encontrada. 404"







