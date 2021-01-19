import glob
import os
import time

import embeddings as embeddings_lib
from flask import Flask, jsonify, render_template, request, redirect, send_from_directory 
import pandas as pd
from werkzeug.utils import secure_filename
import zipfile


DATA_PATH = '/home/amol/tmp/extracted/'
ZIP_PATH = '/home/amol/tmp/zip/'
CACHED_EMBEDDING_FILE = 'cached_embeddings.pkl'
CACHED_JSON_FILE = 'cached_data.json'
ALLOWED_EXTENSIONS = {'zip'}
IMAGE_TYPES = {'*.jpg', '*.png', '*.jpeg'}

app = Flask(__name__, template_folder='frontend/', static_folder='frontend/')


def allowed_file(filename):
  return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_untaken_file(root, filename):
  i = 0
  save_path = ""
  while True:
    maybe_filename = str(i) + filename
    maybe_save_path = os.path.join(root, maybe_filename)
    if not os.path.exists(maybe_save_path):
      save_path = maybe_save_path
      break
    i = i + 1

  return save_path


def get_last_cached_version(root, filename):
  i = 0
  save_path = ""
  while True:
    maybe_filename = str(i) + filename
    maybe_save_path = os.path.join(root, maybe_filename)
    if os.path.exists(maybe_save_path):
      save_path = maybe_save_path
    else:
      break
    i = i + 1

  return save_path


def upload_(req, load_cached=False):
  start_total = time.time()
  print("Got upload.")
  start = time.time()

  # Check if the post request has the file part.
  if 'zip' not in req.files:
    print('No file part')
    return redirect(req.url)
  f = req.files['zip']

  # If no file was selected, browser may submit an empty part with no name.
  if f.filename == '':
    print('No selected file')
    return redirect(req.url)

  # We have the file. Load the zip and extract it.
  if not (f and allowed_file(f.filename)):
    print("allowed_file failed.")
    return redirect(req.url)

  filename = secure_filename(f.filename)

  stop = time.time()
  print("Got file: ", stop - start)

  cached_extract_path = get_last_cached_version(DATA_PATH, filename)
  if (cached_extract_path and load_cached):
    print("Loading cached version.")
  else:
    start = time.time()
    save_path = get_untaken_file(ZIP_PATH, filename)
    print("Saving zip to path: ", save_path)
    f.save(save_path)
    print("Saved zip.")

    # Extract the file.
    extract_path = get_untaken_file(DATA_PATH, filename)
    print("Extracting zip to path: ", extract_path)
    with zipfile.ZipFile(f, 'r') as zip_ref:
      zip_ref.extractall(extract_path)
      print("Extracted zip.")

    stop = time.time()
    print("Saved and extracted zip: ", stop - start)

    # Get the filepaths.
    image_paths = []
    for image_type in IMAGE_TYPES:
      image_glob = os.path.join(extract_path, '**/', image_type)
      print("Path: ", image_glob)
      image_paths.extend(glob.glob(image_glob, recursive=True))

    # Get the embeddings, and the projections, then cache them.
    start = time.time()
    embeddings_filepaths = embeddings_lib.get_image_embeddings(image_paths)
    stop = time.time()
    print("Got embeddings: ", stop - start)

    start = time.time()
    df = pd.DataFrame()
    df['embeddings'], df['filepaths'] = zip(*embeddings_filepaths)
    projections_3d = embeddings_lib.run_umap(df['embeddings'])
    projections_2d = embeddings_lib.run_umap(df['embeddings'], components=2)
    grid_projections, _ = embeddings_lib.run_rasterfairy(projections_2d)
    df['3d_projections'] = pd.Series(list(projections_3d), index=df.index)
    df['2d_projections'] = pd.Series(list(projections_2d), index=df.index)
    df['grid_projections'] = pd.Series(list(grid_projections), index=df.index)
    df.to_pickle(
      os.path.join(extract_path, CACHED_EMBEDDING_FILE))
    stop = time.time()
    print("Got projections: ", stop - start)

    # Return a json and save it.
    cached_extract_path = extract_path
    df.to_json(os.path.join(extract_path, CACHED_JSON_FILE))

  return jsonify(os.path.join(cached_extract_path, CACHED_JSON_FILE))


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
  return upload_(request)


@app.route('/upload_cache', methods=['POST'])
def upload_cache():
  return upload_(request, load_cached=True)


@app.route("/path/<path:file_name>", methods=["GET"])
def get_path(file_name):
  base, fname = os.path.split(file_name)
  print("Serving: ", file_name)
  return send_from_directory('/' + base, fname)


def main():
  if not os.path.exists(ZIP_PATH):
    os.makedirs(ZIP_PATH)

  if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

  app.run(debug=True, port=5000)


if __name__ == '__main__':
  main()
