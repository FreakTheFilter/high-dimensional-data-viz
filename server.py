from flask import Flask, jsonify, render_template, request

UPLOAD_FOLDER = '~/tmp/'

app = Flask(__name__, template_folder='frontend/', static_folder='frontend/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
  # Handle file loading here. For now, just return the base path with all of
  # the data.
  pass


def main():
  app.run(debug=True)


# Upload images.
#   Get embeddings for each image.
#   Create graph.
#   Return graph in d3--interpretable format (streaming?).

if __name__ == '__main__':
  main()
