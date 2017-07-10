import io
import os

from flask import Flask, jsonify, render_template, request, url_for
from hashids import Hashids
from pymongo import MongoClient

from ..io import FitbodLoader, DictOutput


app = Flask('gains.web')
hashids = Hashids(salt='gains')


@app.before_first_request
def configure_database():
    database_uri = os.environ['MONGODB_URI']
    app.database = MongoClient(database_uri).get_default_database()


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

    uploads = app.database.uploads

    record = {
        'analysis': data,
        'slug': None,
    }

    inserted_id = uploads.insert_one(record).inserted_id
    slug = hashids.encode(inserted_id.binary)

    uploads.find_one_and_update(inserted_id, {'$set': {'slug': slug}})

    return redirect(url_for('.analysis', slug=slug))


@app.route('/<slug>')
def analysis(slug):
    return render_template('analysis.html')
