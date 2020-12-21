from flask import Flask, jsonify, render_template, request
app = Flask(__name__, template_folder='frontend/', static_folder='frontend/')

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

def main():
  app.run(debug=True)

if __name__ == '__main__':
  main()
