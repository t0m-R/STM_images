import pickle
from pathlib import Path
import numpy as np
import omicronscala
import spym
import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool, TapTool, OpenURL
from bokeh.models import Title
from bokeh.palettes import viridis
from bokeh.plotting import figure


def get_axis(x, y):
    axis = [x for x in [x, y] if x is not None]
    return axis


def load_stm(file):
    with open(file, 'rb') as f:
        df = pickle.load(f)
    return df


def get_chosen_metadata(df, metadata, treshold=100):
    df = df.groupby(metadata).size().reset_index(name='N imgs')
    df = df[df['N imgs'] >= treshold]
    cols = metadata
    cols.insert(0, 'N imgs')
    df = df[cols].sort_values('N imgs', ascending=False)
    return df


def filter_df_columns(df, cols, values):
    df = df.loc[(df[cols[0]] == float(values[0])) &
                (df[cols[1]] == float(values[1]))]
    columns = ['ID', 'Date', 'Categories', 'FieldXSizeinnm',
               'FieldYSizeinnm', 'ScanAngle', 'GapVoltage',
               'FeedbackSet', 'LoopGain', 'ScanSpeed', 'XOffset', 'YOffset']
    return df[columns]


def get_quantile_plot(df, axis, total):
    df['quantiles'] = pd.qcut(df[axis[1]], q=10)
    df = df.groupby(['quantiles'], as_index=False)['N imgs'].sum()
    quantiles = []
    imgs = []
    for c in df['N imgs']:
        imgs.append(c)

    for i in df['quantiles']:
        quantiles.append(str(i))

    source = ColumnDataSource(data=dict(quantiles=quantiles, imgs=imgs,
                                        color=viridis(10)))
    plot = figure(x_range=quantiles, x_axis_label='Quantiles',
                  y_axis_label='N Images', plot_width=800,
                  plot_height=600, sizing_mode='scale_width')
    plot.vbar(x='quantiles', top='imgs', width=0.9, color='color',
              legend_field="quantiles", source=source)
    plot.y_range.start = 0
    hover = HoverTool(tooltips=[('N images', '@imgs'),
                                ('Quantile', '@quantiles')])
    title = 'Quantiles of {}'.format(axis[1])
    coverage = str(round(sum(df['N imgs']) / total * 100, 2))
    plot.add_layout(Title(text='Metadata coverage: {} %'.format(coverage),
                          text_font_style="italic"), 'above')
    return plot, hover, title


def get_scatter_plot(df, axis, ip, port):
    df['colors'] = viridis(len(df[axis[0]]))
    df['radius'] = (np.sqrt(df['N imgs']) * 0.1 *
                    max(df[axis[1]]) / np.sqrt(max((df['N imgs']))))
    source = ColumnDataSource(df)
    plot = figure(x_axis_label=axis[1], y_axis_label=axis[2],
                  plot_width=800, plot_height=600,
                  sizing_mode='scale_width', tools='tap')
    plot.scatter(axis[1], axis[2], radius='radius', fill_color='colors',
                 alpha=0.8, source=source)
    hover = HoverTool(tooltips=[('N images', '@{N imgs}'),
                                (axis[1], '@' + axis[1] + '{0.00}'),
                                (axis[2], '@' + axis[2] + '{0.00}')])

    title = 'Scatter plot of {},{}'.format(axis[1], axis[2])
    url = "http://{}:{}/dashboard_stm/images?x=".format(ip, port) + axis[1] + "&xval=@" + \
          axis[1] + '{0.00}' + "&y=" + axis[2] + "&yval=@" + axis[2] + '{0.00}'
    return plot, hover, title, url


def bokeh_plot(metadata, total, ip, port):
    df = metadata
    axis = metadata.columns
    url = ''

    if len(axis) == 2:
        plot, hover, title = get_quantile_plot(df, axis, total)
    else:
        plot, hover, title, url = get_scatter_plot(df, axis, ip, port)

    plot.add_layout(Title(text='{}'.format(title), text_font_style="bold",
                          text_font_size="16pt"), 'above')
    plot.add_tools(hover)

    if url != '':
        taptool = plot.select(type=TapTool)
        taptool.callback = OpenURL(url=url)

    script, div = components(plot)
    return script, div


def get_img_by_id(df, path, img_id):
    img = df.loc[img_id]
    file = img.ImageOriginalName
    ds = omicronscala.to_dataset(Path(path + file))
    tf = ds.Z_Forward
    tf.spym.align()
    tf.spym.plane()
    tf.spym.fixzero(to_mean=True)
    return img, tf
