import os
import dummy
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/start', methods = ['POST'])
def start():
  if request.method == 'POST':
    return render_template("survey.html")

@app.route('/submit', methods = ['POST'])
def submit():
  if request.method == 'POST':
    return render_template("thanks.html")

@app.route('/get', methods = ['GET', 'POST'])
def survey():
  answers = {}
  if request.method =='POST':
    try:
      answers['q1'] = request.form['q1']
      answers['q2'] = request.form['q2']
      answers['q3'] = request.form['q3']
      answers['q4'] = request.form['q4']
      answers['q5'] = request.form['q5']
      answers['q6'] = request.form['q6']
      answers['q7'] = request.form['q7']
      answers['q8'] = request.form['q8']
      dummy.read(list(answers.values()))
      return render_template("thanks.html")
    except:
        return render_template("survey.html", message = "Oops, you forgot to fill in all of the questions!")

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
