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


def aligned_img(data):
    data.spym.align()
    return data


def fit_plane_img(data):
    data.spym.align()
    data.spym.plane()
    return data


def fix_zero_img(data):
    data.spym.align()
    data.spym.plane()
    data.spym.fixzero(to_mean=True)
    return data


def process_img(data):
    data = aligned_img(data)
    data = fit_plane_img(data)
    return fix_zero_img(data)


def get_img(df, path, img_id):
    img = df.loc[img_id]
    date = img.Date
    fname = img.TF0_Filename
    file = img.ImageOriginalName
    data = omicronscala.to_dataset(Path(path + file))
    fwd = data.Z_Forward
    return date, fname, fwd


def get_preprocessing_data(data):
    raw = data
    aligned = aligned_img(copy.deepcopy(raw))
    fit_plane = fit_plane_img(copy.deepcopy(raw))
    fixed_zero = fix_zero_img(copy.deepcopy(raw))
    imgs = [raw, aligned, fit_plane, fixed_zero]
    titles = ['raw', 'aligned', 'fit_plane', 'fixed_zero']
    return imgs, titles


def show_preprocessing_lines(df, path, img_id, sharey=False):
    plt.ioff()
    date, fname, fwd = get_img(df, path, img_id)

    fig, axs = plt.subplots(1, 4, figsize=(24, 8), sharey=sharey)

    if not sharey:
        fig.suptitle(r"[{}] {} $\bf{{{}}}$".format(date, fname, img_id), fontsize=30)

    imgs, titles = get_preprocessing_data(fwd)

    for i in range(4):
        axs[i].plot(imgs[i])
        axs[i].grid(True, axis='x', linestyle='--')

        if sharey:
            axs[i].grid(True, axis='both', linestyle='--')
            axs[i].set_xlabel('datapoints')
            axs[i].tick_params(labelleft=True)
        else:
            axs[i].set_title(titles[i], fontsize=24)
            axs[i].tick_params(labelbottom=False)

        for item in ([axs[i].xaxis.label, axs[i].yaxis.label] + axs[i].get_xticklabels() + axs[i].get_yticklabels()):
            item.set_fontsize(18)

    axs[0].set_ylabel('Z value')

    plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    if sharey:
        fig.subplots_adjust(wspace=0.17)
        name = 'lines_bottom'
    else:
        fig.subplots_adjust(hspace=0.14)
        name = 'lines_top'
    fig.show()
    fig.savefig('img_preprocessing_analysis/{}.png'.format(name))


def show_preprocessing_heatmaps(df, path, img_id, robust=False):
    plt.ioff()
    date, fname, fwd = get_img(df, path, img_id)

    fig, axs = plt.subplots(1, 4, figsize=(24, 8), sharey=True)
    fig.suptitle(r"[{}] {} $\bf{{{}}}$".format(date, fname, img_id), fontsize=30)

    imgs, titles = get_preprocessing_data(fwd)

    for i in range(4):
        imgs[i].plot(ax=axs[i], cmap='afmhot', add_colorbar=False, robust=robust)
        set_layout(axs[i], titles[i], 24, 18)

    name = 'heatmaps'
    plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    fig.show()
    fig.savefig('img_preprocessing_analysis/{}.png'.format(name))


def show_alignment_error(df, path, img_id):
    plt.ioff()
    date, fname, fwd = get_img(df, path, img_id)
    fig, axs = plt.subplots(1, 3, figsize=(18, 8))
    fig.suptitle(r"[{}] {} $\bf{{{}}}$".format(date, fname, img_id), fontsize=30)
    raw = fwd
    fixed_zero = fix_zero_img(copy.deepcopy(fwd))
    colormap = copy.deepcopy(fixed_zero)
    imgs = [raw, fixed_zero, colormap]
    titles = ['raw', 'preprocessed', 'colormap']

    for i in range(3):
        if i == 2:
            imgs[i].plot(ax=axs[i], cmap='afmhot', add_colorbar=False)
        else:
            axs[i].set_ylabel('Z value')
            axs[i].set_xlabel('data points')
            axs[i].plot(imgs[i])
        set_layout(axs[i], titles[i], 24, 18)

    plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    name = 'alignment_error'
    fig.show()
    fig.savefig('img_preprocessing_analysis/{}.png'.format(name))


def set_layout(axs, title, title_fontsize, item_fontsize):
    axs.set_title(title, fontsize=title_fontsize)
    for item in ([axs.xaxis.label, axs.yaxis.label] + axs.get_xticklabels() + axs.get_yticklabels()):
        item.set_fontsize(item_fontsize)


def show_alignment_error_slices(df, path, img_id, cut=50):
    plt.ioff()
    date, fname, fwd = get_img(df, path, img_id)
    data = fwd
    colormap = fix_zero_img(copy.deepcopy(fwd))
    raw = np.rot90(data, -1)
    size = raw.shape[0]
    rows = size // cut

    fig, axs = plt.subplots(rows, 2, figsize=(12, 12))
    fig.suptitle(r"[{}] {} $\bf{{{}}}$".format(date, fname, img_id), fontsize=30)

    for i in range(rows):

        if i == rows - 1:
            axs[i, 0].set_xlabel('datapoints')
        else:
            axs[i, 1].set_xticks([])
            axs[i, 0].set_xticks([])
            axs[i, 1].xaxis.label.set_visible(False)
            axs[i, 1].tick_params(labelbottom=False)
            axs[i, 0].tick_params(labelbottom=False)

        img_slice = colormap[size - (i + 1) * cut:size - i * cut, :]
        img_slice.plot(ax=axs[i, 1], cmap='afmhot', add_colorbar=False)
        axs[i, 1].yaxis.label.set_visible(False)

        raw_slice = raw[:, (i * cut):(i + 1) * cut]
        axs[i, 0].plot(raw_slice, linewidth=0.5)

        for j in [0, 1]:
            for item in ([axs[i, j].xaxis.label, axs[i, j].yaxis.label] + axs[i, j].get_xticklabels() +
                         axs[i, j].get_yticklabels()):
                item.set_fontsize(10)

        if i == 0:
            axs[0, 0].set_title('raw', fontsize=24)
            axs[0, 1].set_title('colormap', fontsize=24)

    axs[rows - 1, 0].xaxis.label.set_fontsize(24)
    axs[rows - 1, 1].xaxis.label.set_fontsize(24)

    fig.text(0.03, 0.5, 'Z values', va='center', rotation='vertical', fontsize=24)
    fig.text(0.53, 0.5, 'y [nm]', va='center', rotation='vertical', fontsize=24)

    plt.tight_layout(rect=[0.06, 0.03, 1, 0.9])
    fig.subplots_adjust(hspace=0.05, wspace=0.25)
    name = 'alignment_error_slices'
    fig.show()
    fig.savefig('img_preprocessing_analysis/{}.png'.format(name))


def show_colormap_solution(df, path, list_ids):
    plt.ioff()
    fig, axs = plt.subplots(2, len(list_ids), figsize=(len(list_ids) * 7, 15))

    for i in range(len(list_ids)):
        img_id = list_ids[i]
        date, fname, fwd = get_img(df, path, img_id)
        colormap = process_img(fwd)
        colormap.plot(ax=axs[0, i], cmap='afmhot', add_colorbar=False, robust=False)
        colormap.plot(ax=axs[1, i], cmap='afmhot', add_colorbar=False, robust=True)
        axs[0, i].set_title(r"[{}] {} $\bf{{{}}}$".format(date, fname, img_id), fontsize=24)
        axs[0, i].set_xticks([])
        axs[0, i].set_yticks([])
        axs[0, i].xaxis.label.set_visible(False)
        axs[0, i].yaxis.label.set_visible(False)

        axs[0, i].tick_params(labelbottom=True)
        axs[0, i].tick_params(labelbottom=True)

        for j in [0, 1]:
            for item in ([axs[j, i].xaxis.label, axs[j, i].yaxis.label] + axs[j, i].get_xticklabels() +
                         axs[j, i].get_yticklabels()):
                item.set_fontsize(18)

    name = 'colormap_error_heatmaps'
    plt.tight_layout(rect=[0, 0.03, 1, 0.90])
    fig.show()
    fig.savefig('img_preprocessing_analysis/{}.png'.format(name))


def show_row_images(df, path, list_ids, save=False, dpi=100):
    plt.ioff()
    fig, axs = plt.subplots(1, len(list_ids), figsize=(len(list_ids) * 5, 5))

    for i in range(len(list_ids)):
        img_id = list_ids[i]
        date, fname, fwd = get_img(df, path, img_id)
        colormap = process_img(fwd)
        colormap.plot(ax=axs[i], cmap='afmhot', add_colorbar=False, robust=False)
        axs[i].axis('off')

    plt.tight_layout(rect=[0, 0.0, 1, 1])
    fig.show()
    if save:
        name = 'thesis_readme_logo'
        fig.savefig('{}.png'.format(name), dpi=dpi)
