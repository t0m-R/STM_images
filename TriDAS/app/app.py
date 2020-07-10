import sys
import pickle
from flask import Flask, render_template, request, session
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import components, file_html
from utils import *
import io
from flask import Flask, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)
stm = load_stm()
path = 'path_to_images/STM'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard_stm/', methods=['GET','POST'])

def show_dashboard():
    total = len(stm)
    x_ax = request.form.get('X')
    y_ax = request.form.get('Y')
    plots = []
    if x_ax == y_ax:
        y_ax = None
    axis = get_axis(x_ax,y_ax)
    if axis == []:
        return render_template('dashboard_stm.html', plots=plots)
    metadata = get_columns(stm, axis)
    plot = df_plot(metadata, total)
    plots.append(plot)
    return render_template('dashboard_stm.html', plots=plots)

@app.route('/dashboard_stm/images/', methods=['GET','POST'])

def images():
    x = request.args.get('x')
    y = request.args.get('y')
    xval = request.args.get('xval')
    yval = request.args.get('yval')
    cols = [x, y]
    values = [xval, yval]
    imgs = df_images(stm, cols, values).sort_values('Date')
    if len(imgs) > 1000:
        imgs = imgs.sample(1000)
    return render_template('stm_images.html',
                            tables=[imgs.to_html(table_id="STM",
                            index=False, bold_rows=False,
                            classes='table table-bordered table-striped',
                            header="true")])

@app.route('/dashboard_stm/plot_image/', methods=['GET', 'POST'])

def plot_image():
    id = request.args.get('ID')
    row, img = imgID(stm, path, int(id))
    fig = Figure(figsize=(8,8))
    axis = fig.add_subplot(1, 1, 1)
    category = row.Categories.item()
    fname = row.TF0_Filename.item()
    img.plot(ax=axis, cmap='afmhot', add_colorbar=False)
    axis.set_title("[{}] {}".format(category, fname), fontsize=16)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(host='IP_ADDR', port='PORT', debug=True)
