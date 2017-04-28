import numpy as np
from matplotlib import pyplot as plt, cm
from matplotlib.colors import colorConverter
import matplotlib as mpl


def hist(data, nb_bins=256, data_range=(0, 255), show=True, save=False, prefix='data', density=False):
    '''Histogram of a data array.

    Compute and plot the gray level histogram of the provided data array.

    *Parameters*

    **data**: the data array to analyse.

    **nb_bins**: the number of bins in the histogram.

    **data_range**: the data range to use in the histogram, (0,255) by default.

    **show**: boolean to display the figure using pyplot (defalut True).

    **save**: boolean to save the figure using pyplot (defalut False).

    **prefix**: a string to use in the file name when saving the histogram
    as an image (defaut 'data').

    **density**: a boolean to control wether the histogram is plotted
    using the probability density function, see numpy histogram function
    for more details (default False).

    .. figure:: _static/HDPE_0001-2_512x512x512_uint8_hist.png
        :width: 600 px
        :height: 400 px
        :alt: HDPE_0001-2_512x512x512_uint8_hist.png
        :align: center

        Gray level histogram computed on a 512x512x512 8 bits image.
    '''
    print 'computing gray level histogram'
    hist, bin_edges = np.histogram(data, bins=nb_bins, range=data_range, density=density)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    plt.figure(figsize=(6, 4))
    if density:
        plt.bar(bin_centers, 100 * hist, width=1, fill=True, color='g', edgecolor='g')
        plt.ylabel('Probability (%)')
    else:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        plt.bar(bin_centers, hist, width=1, fill=True, color='g', edgecolor='g')
        plt.ylabel('Counts')
    plt.xlim(data_range)
    plt.xlabel('Gray level value')
    if save: plt.savefig(prefix + '_hist.png', format='png')
    if show: plt.show()


def flat(img, ref, dark):
    '''Apply flat field correction to an image.

    :param np.array img: A 2D array representing the image to correct.
    :param np.array ref: The reference image (without the sample), same shape as the image to correct.
    :param np.array dark: A 2D numpy array representing the dark image (thermal noise of the camera).
    :returns np.array float: the flat field corrected image (between 0 and 1) as a float32 numpy array.
    '''
    flat = (img - dark).astype(np.float32) / (ref - dark).astype(np.float32)
    return flat


def auto_min_max(data, cut=0.0002, nb_bins=256, verbose=False):
    '''Compute the min and max values in a numpy data array.

    The min and max values are calculated based on the histogram of the
    array which is limited at both end by the cut parameter (0.0002 by
    default). This means 99.98% of the values are within the [min, max]
    range.

    :param data: the data array to analyse.
    :param float cut: the cut off value to use on the histogram (0.0002 by default).
    :param int nb_bins: number of bins to use in the histogram (256 by default).
    :param bool verbose: activate verbose mode (False by default).
    :returns tuple (min, max): a tuple containing the min and max values.
    '''
    n, bins = np.histogram(data, bins=nb_bins, density=False)
    min = 0.0
    max = 0.0
    total = np.sum(n)
    p = np.cumsum(n)
    for i in range(nb_bins):
        if p[i] > total * cut:
            min = bins[i]
            if verbose:
                print('min = %f (i=%d)' % (min, i))
            break
    for i in range(nb_bins):
        if total - p[nb_bins - 1 - i] > total * cut:
            max = bins[nb_bins - 1 - i]
            if verbose:
                print('max = %f' % max)
            break
    return min, max


def recad(data, min, max):
    '''Cast a numpy array into 8 bit data type.

    This function change the data type of a numpy array into 8 bit. The
    data values are interpolated from [min, max] to [0, 255]. Both min
    and max values may be chosen manually or computed by the function
    `find_min_max`.

    :param data: the data array to cast to uint8.
    :param float min: value to use as the minimum (will be 0 in the casted array).
    :param float max: value to use as the maximum (will be 255 in the casted array).
    :returns data_uint8: the data array casted to uint8.
    '''
    low_values_indices = data < min
    data[low_values_indices] = min
    large_values_indices = data > max
    data[large_values_indices] = max
    data_uint8 = (255 * (data - min) / (max - min)).astype(np.uint8)
    return data_uint8


def alpha_cmap(color='red', opacity=1.0):
    '''Creating a particular colormap with transparency.

    Only values equal to 255 will have a non zero alpha channel.
    This is typically used to overlay a binary result on initial data.

    :param color: the color to use for non transparent values (ie. 255).
    :param float opacity: opacity value to use for visible pixels.
    :returns mycmap: a fully transparent colormap except for 255 values.
    '''
    color1 = colorConverter.to_rgba('white')
    color2 = colorConverter.to_rgba(color)
    mycmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap', [color1, color2], 256)
    mycmap._init()
    alphas = np.zeros(mycmap.N + 3)
    alphas[255:] = opacity  # show only values at 255
    mycmap._lut[:, -1] = alphas
    return mycmap


class AxShowPixelValue:
    '''A simple class that wraps a pyplot ax and modify its coordinate
    formatter to show the pixel value.'''

    def __init__(self, ax):
        '''Create a new AxShowPixelValue instance with a reference to the
        given pyplot ax.'''
        self.ax = ax
        self.ax.format_coord = self.format_coord

    def imshow(self, array, **kwargs):
        '''Wraps pyplot imshow function for the ax selected and modify
        the coordinate formatter to show the pixel value as well.
        All the usual parameters can be passed to imshow.
        '''
        self.array = array
        self.ax.imshow(self.array, **kwargs)

    def format_coord(self, x, y):
        '''A function to modify the coordinate formatter of pyplot to
        display the pixel value. This is usually called when moving the
        mouse above the plotted image.
        '''
        n_rows, n_cols = self.array.shape
        col = int(x + 0.5)
        row = int(y + 0.5)
        if col >= 0 and col < n_cols and row >= 0 and row < n_rows:
            z = self.array[row, col]
            return 'x=%1.1f, y=%1.1f, z=%1.1f' % (x, y, z)
        else:
            return 'x=%1.1f, y=%1.1f' % (x, y)
