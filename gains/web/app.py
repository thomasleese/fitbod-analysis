from datetime import datetime
import io
import os
import random
import sys

from flask import Flask, jsonify, render_template, redirect, request, url_for
from hashids import Hashids
from pymongo import MongoClient

from ..io import FitbodLoader, DictInput, DictOutput
from ..gym import Muscle


app = Flask('gains.web')
hashids = Hashids(salt='gains')


@app.before_first_request
def configure_database():
    database_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost/gains')
    app.database = MongoClient(database_uri).get_default_database()

    app.database.uploads.create_index('slug', unique=True)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return redirect(url_for('.home'))

    loader = FitbodLoader(io.TextIOWrapper(file.stream, encoding='UTF-8'))
    data = DictOutput(loader.analysis).dict

    slug = hashids.encode(random.randint(0, sys.maxsize))
    record = {'analysis': data, 'slug': slug, 'date': datetime.now()}
    app.database.uploads.insert_one(record)

    return redirect(url_for('.analysis', slug=slug))


@app.route('/<slug>')
def analysis(slug):
    upload = app.database.uploads.find_one({'slug': slug})
    analysis = DictInput(upload['analysis']).analysis

    return render_template('analysis.html',
                           date=upload['date'], analysis=analysis)


@app.route('/<slug>/json')
def analysis_json(slug):
    upload = app.database.uploads.find_one({'slug': slug})
    return jsonify(**upload['analysis'])
