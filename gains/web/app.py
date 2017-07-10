from flask import Flask, render_template


app = Flask('gains.web')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/<slug>')
def analysis(slug):
    return render_template('analysis.html')
