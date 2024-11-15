from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os


# creating the instance for the app #
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/download', methods=['POST'])
def down_video():
    url = request.form['url']
    quality = request.form['quality']
    try:
        yt = YouTube(url)

        if quality == 'highest':
            stream = yt.streams.get_highest_resolution()
        elif quality == 'lowest':
            stream = yt.streams.get_lowest_resolution()
        elif quality == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            return "Invalid quality selected"
    
        output_path = stream.download()
        return send_file(output_path, as_attachment=True, download_name=f"{yt.title}.{stream.subtype}")
    except Exception as e:
        return f"An error occurred: {str(e)}"
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

