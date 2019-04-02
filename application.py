from flask import Flask, request, render_template
import US2SMT
import Parser

app = Flask(__name__)
parser = Parser.Parser()


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/solve_us', methods=['POST'])
def solve_us():
  converter = US2SMT.US2SMT(request.files['us_file'], parser)
  smt, goal_set = converter.get_smt_input()
  oms_out = US2SMT.get_oms_out()
  return render_template('result.html', smt=smt, goal_set=goal_set, oms_out=oms_out)


if __name__ == '__main__':
  app.run(debug=True)
