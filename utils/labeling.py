import copy
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import omicronscala
import spym
import xarray
import os
from pathlib import Path


def get_months(df):
    df['months'] = [x[:7] for x in df['Date']]
    df = df.sort_values(by='months')
    months = df['months'].unique()
    return months


def get_month_imgs(df, month):
    imgs = df[df['months'] == month][:]
    print('[{}/{}] Plotting {} - {} images '.format(h, len(months), month, len(imgs)))

    if not len(imgs) < 2:
        print('\tSkip {} : only {} images'.format(month, len(images)))
        return None

    return imgs


def plot_img(ax, img_data, img_meta, fig_size):
    img_data.plot(ax=ax, cmap='afmhot', add_colorbar=False)
    ax.set_title(r"[{}] {} $\bf{{{}}}$".format(img_meta['Date'], img_meta['TF0_Filename'], img_meta['ID']), fontsize=20)
    for item in ([ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(fig_size * 2)


def plot_months_samples(df, path, fig_size=8, dpi=40):
    plt.ioff()
    months = get_months(df)
    for h, month in enumerate(months):
        rows, cols = 10, 10
        imgs = get_month_imgs(df, month)
        if imgs is None:
            continue

        try:
            samples = imgs.sample(rows * cols)
        except:
            samples = imgs

        category = imgs.iloc[0][:].Categories
        samples = samples.sort_values(by='Date')
        images = []

        for _, image in samples.iterrows():
            try:
                images.append(show_img(path, image))
            except Exception as e:
                print(e)
                print(image['ID'])
                pass

        if cols > len(images):
            cols = len(images)
            rows = 1
        else:
            rows = len(images) // cols

        print('images: {} cols: {}, rows: {}'.format(len(images), cols, rows))

        fig, axs = plt.subplots(rows, cols, figsize=((fsize * cols), (fsize * rows)))
        c = 0
        if rows > 1:
            for i in range(rows):
                for j in range(cols):
                    plot_img(ax=axs[i, j], img_data=images[c][1], img_meta=images[c][0], fig_size=fig_size)
                    c += 1
        else:
            for j in range(cols):
                plot_img(ax=axs[j], img_data=images[c][1], img_meta=images[c][0], fig_size=fig_size)
                c += 1
        plt.tight_layout()
        plt.draw()

        Path('months/{}'.format(category)).mkdir(parents=True, exist_ok=True)
        plt.savefig('months/{}/{}.png'.format(category, month), dpi=dpi)
        plt.close(fig)


def plot_months(df, path, fig_size=8, dpi=40):
    sample_errors = []
    img_errors = []
    plt.ioff()
    months = get_months(df)
    for h, month in enumerate(months):
        rows, cols = 10, 10
        imgs = get_month_imgs(df, month)
        if imgs is None:
            continue

        n = rows * cols

        f = len(imgs) % n
        p = len(imgs) // n

        for r in range(1, p + 1):
            try:
                samples = imgs[(r - 1) * n:r * n]
            except:
                sample_errors.append('{}_{}-{}'.format(month, int((r - 1) * n), r * n))
                continue

            samples = samples.sort_values(by=['Date', 'Time'])
            images = []

            for _, image in samples.iterrows():
                try:
                    images.append(show_img(path, image))
                except:
                    img_errors.append(image['ID'])
                    pass

            filename = '{}_{}.png'.format(int((r - 1) * n), r * n)
            save_month_plot(month, images, cols, fig_size, filename, dpi)

        if f != 0:
            try:
                samples = imgs[p * n:]
            except:
                sample_errors.append('{}_{}-{}'.format(month, int(p * n), len(imgs)))
                continue

            samples = samples.sort_values(by=['Date', 'Time'])
            images = []

            for _, image in samples.iterrows():
                try:
                    images.append(show_img(path, image))
                except:
                    img_errors.append(image['ID'])
                    pass

            filename = '{}_{}.png'.format(p * n, len(imgs))
            save_month_plot(month, images, cols, fig_size, filename, dpi)

    return sample_errors, img_errors


def save_month_plot(month, images, cols, fig_size, filename, dpi):
    if cols > len(images):
        cols = len(images)
        rows = 1
    else:
        rows = len(images) // cols
        if len(images) % cols != 0:
            rows += 1

    print('images: {} cols: {}, rows: {}'.format(len(images), cols, rows))

    fig, axs = plt.subplots(rows, cols, figsize=((fig_size * cols), (fig_size * rows)))
    c = 0
    if rows > 1:
        for i in range(rows):
            for j in range(cols):
                try:
                    plot_img(ax=axs[i, j], img_data=images[c][1], img_meta=images[c][0], fig_size=fig_size)
                except:
                    axs[i, j].axis('off')
                    pass
                c += 1
    else:
        for j in range(cols):
            try:
                plot_img(ax=axs[j], img_data=images[c][1], img_meta=images[c][0], fig_size=fig_size)
            except:
                axs[j].axis('off')
                pass
            c += 1
    plt.tight_layout()
    plt.draw()
    Path('months/{}'.format(month)).mkdir(parents=True, exist_ok=True)
    plt.savefig('months/{}/{}.png'.format(month, filename, dpi=dpi))
    plt.close(fig)
