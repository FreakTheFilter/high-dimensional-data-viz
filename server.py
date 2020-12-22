import glob
import os

import embeddings as embeddings_lib
from flask import Flask, jsonify, render_template, request, redirect
import networkx as nx
from werkzeug.utils import secure_filename
from sklearn.metrics.pairwise import cosine_similarity
import zipfile


DATA_PATH = '/home/amol/tmp/extracted/'
ZIP_PATH = '/home/amol/tmp/zip/'
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


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():

  print("Got upload.")

  # Check if the post request has the file part.
  if 'zip' not in request.files:
    print('No file part')
    return redirect(request.url)
  f = request.files['zip']
  print("Got file.")

  # If no file was selected, browser may submit an empty part with no name.
  if f.filename == '':
    print('No selected file')
    return redirect(request.url)
  print("File name: ", f.filename)

  # We have the file. Load the zip and extract it.
  if not os.path.exists(ZIP_PATH):
    os.makedirs(ZIP_PATH)

  if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

  if not (f and allowed_file(f.filename)):
    print("allowed_file failed.")
    return redirect(request.url)

  print("File exists and is allowed.")
  filename = secure_filename(f.filename)

  # Make sure the file doesnt already exist. If it does, save to a diff file.
  save_path = get_untaken_file(ZIP_PATH, filename)
  print("Saving zip to path: ", save_path)
  f.save(save_path)
  print("Saved zip.")

  # Extract the file. Do the same thing by checking the path.
  extract_path = get_untaken_file(DATA_PATH, filename)
  print("Extracting zip to path: ", extract_path)
  with zipfile.ZipFile(f, 'r') as zip_ref:
    zip_ref.extractall(extract_path)
    print("Extracted zip.")

  # Get the filepaths.
  image_paths = []
  for image_type in IMAGE_TYPES:
    image_glob = os.path.join(extract_path, '**/', image_type)
    print("Path: ", image_glob)
    image_paths.extend(glob.glob(image_glob, recursive=True))

  # Get the embeddings, then cache them.
  embeddings_filepaths = embeddings_lib.get_image_embeddings(image_paths)
  embeddings_filepaths.to_csv(
    os.path.join(extract_path, 'cached_embeddings.csv'))

  # Build the networkx graph.
  # embeddings, _ = zip(*embeddings_filepaths)
  # similarities = cosine_similarity(embeddings)
  # print(similarities)
  # graph = nx.from_pandas_adjacency(similarities)

  # Return a json.

  print("Success?")
  return redirect(request.url)


def main():
  app.run(debug=True, port=5001)


# Upload images.
#   Get embeddings for each image.
#   Create graph.
#   Return graph in d3--interpretable format (streaming?).

if __name__ == '__main__':
  main()
