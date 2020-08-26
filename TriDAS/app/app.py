import io

from flask import Flask, make_response
from flask import render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import utils

app = Flask(__name__)
stm = utils.load_stm("static/stm_metadata.pkl")
path = 'path_to_stm_images'
ip = "IP_ADDRESS"
port = "PORT"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard_stm/', methods=['GET', 'POST'])
def show_dashboard():
    total = len(stm)
    x_ax = request.form.get('X')
    y_ax = request.form.get('Y')
    plots = []
    if x_ax == y_ax:
        y_ax = None
    axis = utils.get_axis(x_ax, y_ax)
    if not axis:
        return render_template('dashboard_stm.html', plots=plots)
    metadata = utils.get_chosen_metadata(stm, axis)
    plot = utils.bokeh_plot(metadata, total, ip, port)
    plots.append(plot)
    return render_template('dashboard_stm.html', plots=plots)


@app.route('/dashboard_stm/images/', methods=['GET', 'POST'])
def show_metadata_table():
    x = request.args.get('x')
    y = request.args.get('y')
    xval = request.args.get('xval')
    yval = request.args.get('yval')
    cols = [x, y]
    values = [xval, yval]
    imgs = utils.filter_df_columns(stm, cols, values).sort_values('Date')
    if len(imgs) > 1000:
        imgs = imgs.sample(1000)
    return render_template(
        'stm_images.html',
        tables=[imgs.to_html(table_id="STM",
                             index=False, bold_rows=False,
                             classes='table table-bordered table-striped',
                             header="true")])


@app.route('/dashboard_stm/show_image/', methods=['GET', 'POST'])
def show_image():
    img_id = request.args.get('ID')
    row, img = utils.get_img_by_id(stm, path, int(img_id))
    fig = Figure(figsize=(8, 8))
    axis = fig.add_subplot(1, 1, 1)
    date = row.Date
    fname = row.TF0_Filename
    img.plot(ax=axis, cmap='afmhot', add_colorbar=False)
    axis.set_title("[{}] {}".format(date, fname), fontsize=16)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == "__main__":
    app.run(host=ip, port=port, debug=True)
