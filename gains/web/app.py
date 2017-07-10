import io

from flask import Flask, jsonify, render_template, request, url_for

from ..io import FitbodLoader, DictOutput


app = Flask('gains.web')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return redirect(url_for('.home'))

    loader = FitbodLoader(io.TextIOWrapper(file.stream, encoding='UTF-8'))
    json = DictOutput(loader.analysis).dict
    return jsonify(**json)


@app.route('/<slug>')
def analysis(slug):
    return render_template('analysis.html')
