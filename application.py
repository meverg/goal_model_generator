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
  converter = US2SMT.US2SMT(request.files['us_file'], parser, request.form.get('opt'))
  smt, dot, dictn = converter.get_smt_input()
  oms_out = US2SMT.get_oms_out()

  for line in oms_out.splitlines():
    if line.strip():
      line = line.replace("(", " ")
      line = line.lstrip()
      word = line.split()
      if word[0] in dictn:
          if word[1] == "true)":
              dot.node(word[0], color="limegreen", fillcolor = "palegreen1",style='filled')
          else:
              dot.node(word[0], color="red3", fillcolor = "red",style='filled')

  dot.render(view=True)
  return render_template('index.html')


if __name__ == '__main__':
  app.run(debug=True)
