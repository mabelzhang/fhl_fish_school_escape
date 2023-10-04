#!/usr/bin/env python

# Reads output files from TRex ( https://trex.run )
# Usage:
#   $ python3 read_trex_output.py
# Dependencies:
#   $ pip3 install pycircular

import csv
import math
import os

import numpy as np

import matplotlib.pyplot as plt


# Each instance is one tracked fish's files (csv and npz) outputted from TRex
#class Fish:

#  def __init__(self):




# Functions for plotting
class Plotter:

  def __init__(self):

    # Input args
    # Change this to read a different file
    self.timestamp = 'cy_s_trial1_sch2_stim5_2023-08-04-14-08'
    self.fish_i = '0'

    self.in_dir = 'in/trexOut_cy_trial1_sch2_stim5'
    self.out_dir = os.path.join('out', os.path.basename(self.in_dir))
    if not os.path.exists(self.out_dir):
      os.mkdir(self.out_dir)

    # For plots
    self.defaultSize = None

    # Indicates that the csv file has been read into data
    self.csv_done = False
    self.px = []
    self.py = []
    self.vx = []
    self.vy = []
    self.ax = []
    self.ay = []
    self.angles = []

    # Write to file. If files already exist, set to False to avoid overwrite
    self.SAVE_FIGS = True

    self.PLOT_BG_COLOR = 'black'


  # Load and plot positional data from csv file exported by TRex
  def read_csv(self):

    # CSV contains positional data
    # Data for 1 fish
    # Each row is for one point in time
    self.in_base = self.timestamp + '_fish' + self.fish_i + '.csv'
    self.in_base_prefix = os.path.splitext(self.in_base)[0]

    self.in_full = os.path.join(self.in_dir, self.in_base)
    self.out_prefix = os.path.join(self.out_dir, self.in_base_prefix)

    #####
    # Fields in csv as defined in TRex documentation
    # https://trex.run/docs/formats.html
 
    fieldnames = None
 
    MISSING_FD = 'missing'
    MISSING_VAL_0 = '0.00'
    MISSING_VAL_1 = '1.00'
 
    # May not start at frame 0, and do not have to contain all frames
    # from 0 to n.
    # Use frame because TRex may not have the correct frame rate from our video
    # format. Calculate timing ourselves based on known recording fps.
    FRAME_FD = 'frame'
 
    # Origin is in top-left corner. Make sure cm_per_pixel() is calibrated
    # Actual field is 'X (cm)'
    X_FD = 'X (cm)'
    # Actual field is 'Y (cm)'
    Y_FD = 'Y (cm)'
 
    VX_FD = 'VX (cm/s)'
    VY_FD = 'VY (cm/s)'
 
    AX_FD = 'AX'
    AY_FD = 'AY'
 
    # The absolute angle in radians with respect to the X-axis of the
    # image (e.g. 0 rad indicates the individual is horizontal,
    # looking to the right). You can convert this to degrees using
    # ANGLE/pi*180.
    ANGLE_FD = 'ANGLE'
 
    #####
    # Data vectors
 
    n_valid_rows = 0
 
    # Wipe all data
    frames = []
    self.px = []
    self.py = []
    self.vx = []
    self.vy = []
    self.ax = []
    self.ay = []
    self.angles = []
 
    #####
    # Read csv output file from TRex
    print('Loading %s' % self.in_full)
    with open(self.in_full, 'r') as f:
      reader = csv.DictReader(f)
      fieldnames = reader.fieldnames
 
      # TRex documentation for fields:
      for row in reader:
        # Skip invalid row
        if row[MISSING_FD] == MISSING_VAL_1:
          print('frame %s invalid' % (row[FRAME_FD]))
          continue
 
        frames.append(int(float(row[FRAME_FD])))
 
        # Populate vars with data
        self.px.append(float(row[X_FD]))
        self.py.append(float(row[Y_FD]))
 
        self.vx.append(float(row[VX_FD]))
        self.vy.append(float(row[VY_FD]))
 
        self.ax.append(float(row[AX_FD]))
        self.ay.append(float(row[AY_FD]))
 
        self.angles.append(float(row[ANGLE_FD]))
 
        print('frame %d, px %g, py %g, vx %g, vy %g, ax %g, ay %g, angle %g' % (
          frames[n_valid_rows], self.px[n_valid_rows], self.py[n_valid_rows],
          self.vx[n_valid_rows], self.vy[n_valid_rows],
          self.ax[n_valid_rows], self.ay[n_valid_rows],
          self.angles[n_valid_rows]))
 
        n_valid_rows += 1

    self.csv_done = True


  def plot_positional(self):

    if not self.csv_done:
      self.read_csv()
 
    fig, axes = plt.subplots()
    self.set_dpi(fig, 2)
 
    plt.subplot(321)
    plt.plot(frames, vx)
    plt.title('vx')
 
    plt.subplot(322)
    plt.plot(frames, vy)
    plt.title('vy')
 
    plt.subplot(323)
    plt.plot(frames, ax)
    plt.title('ax')
 
    plt.subplot(324)
    plt.plot(frames, ay)
    plt.title('ay')
 
    plt.subplot(325)
    plt.plot(frames, np.array(self.angles) * 180 / np.pi)
    plt.title('absolute angle')
 
    # Eliminate white spaces before saving
    plt.tight_layout()
    # TODO: Title too low, move higher
    #plt.suptitle(self.in_base)
    if self.SAVE_FIGS:
      plt.savefig(self.out_prefix + '.eps', bbox_inches='tight')
      plt.savefig(self.out_prefix + '.png', bbox_inches='tight')

    plt.show()


  def plot_angles(self):

    if not self.csv_done:
      self.read_csv()
 
    # Polar plot of absolute angles
    self.plot_hist(self.angles, self.out_prefix + '_angles', self.in_base,
      2, {'projection': 'polar'})


  # TODO: Need to load multiple files for this
  def plot_nnd(self, px, py):

    # Plot histogram of nearest neighbor distance

    # Tile for matrix parallelization
    # Tile (y, 1) shape along x
    px_tiled = np.repeat(np.reshape(px, (len(px), 1)), len(px), axis=1)
    # Transpose and tile (1, y) shape along y
    py_tiled = np.repeat(np.reshape(py, (1, len(py))), len(py), axis=0)

    print(px_tiled.shape)
    print(py_tiled.shape)

    dists = np.sqrt(np.multiply(px_tiled, px_tiled) + np.multiply(
      py_tiled, py_tiled))

    # Linear histogram
    self.plot_hist(dists, self.out_prefix + 'nnd', self.in_base, 2)


  # Load and plot posture data from NumPy npz file exported by TRex
  def plot_posture(self):

    # NPZ contains posture data
    # Data for 1 fish
    self.npz_in_base = self.timestamp + '_posture_fish' + self.fish_i + '.npz'
    self.npz_in_full = os.path.join(self.in_dir, self.npz_in_base)

    self.npz_in_base_prefix = os.path.splitext(self.npz_in_base)[0]

    self.npz_in_full = os.path.join(self.in_dir, self.npz_in_base)
    self.npz_out_prefix = os.path.join(self.out_dir, self.npz_in_base_prefix)

    print('Loading %s' % self.npz_in_full)
    postures = np.load(self.npz_in_full)

    #frames = postures['frames']

    # TRex: "Angle (rad) of a line from head-position (first midline segment)
    # through the midline segment at a fraction of midline_stiff_percentage()
    # of the midline - approximating the heading of the individual."
    # https://trex.run/docs/formats.html#posture-data
    # Default midline_stiff_percentage is 0.15
    midline_angles = postures['midline_angle']

    self.plot_hist(midline_angles,
      self.npz_out_prefix + 'midline_angles', self.npz_in_base, 2,
      {'projection': 'polar'})
 

  # Plot histogram, linear or polar.
  # For polar plot, pass in arg {'projection': 'polar'}
  def plot_hist(self, angles, out_pref, title, multiplier=1,
    subplot_kw={}):

    figp, axesp = plt.subplots(subplot_kw=subplot_kw)
    if self.defaultSize is None:
      self.set_dpi(figp, multiplier)

    if self.PLOT_BG_COLOR == 'black':
      self.black_background(False, subplot_kw)

    # Font size
    # Title size
    plt.rcParams.update({'font.size': 32})
    # Tick label size
    plt.tick_params (axis='x', labelsize=30)
    plt.tick_params (axis='y', labelsize=24)

    # Take histogram
    n_bins = int(math.ceil(360 / 5.0))
    angles_hist, angles_bin_edges = np.histogram(angles, bins=n_bins)

    # Get the midpoint between bin edges
    angles_bin_pts = angles_bin_edges + 0.5 * (
      angles_bin_edges[0] + angles_bin_edges[1])
    angles_bin_pts = angles_bin_pts[:n_bins]

    # Plot histogram
    hist_width = 2 * np.pi / n_bins
    hist_colors = plt.cm.viridis(angles_hist)
    axesp.bar(angles_bin_pts, angles_hist, width=hist_width,
      bottom=0.0, color=hist_colors, alpha=0.5)

    # Save figure
    figp.set_size_inches(self.defaultSize[0] * 2, self.defaultSize[0] * 2)
    Size = figp.get_size_inches()
    # Eliminate white spaces before saving
    plt.tight_layout()
    plt.title(title)
    if self.SAVE_FIGS:
      if self.PLOT_BG_COLOR == 'black':
        plt.savefig(out_pref + '_black.eps', bbox_inches='tight',
          dpi=self.dpi * multiplier, facecolor=figp.get_facecolor(),
          edgecolor='none')
        plt.savefig(out_pref + '_black.png', bbox_inches='tight',
          dpi=self.dpi * multiplier, facecolor=figp.get_facecolor(),
          edgecolor='none')
      else:
        plt.savefig(out_pref + '.eps', bbox_inches='tight',
          dpi=self.dpi * multiplier)
        plt.savefig(out_pref + '.png', bbox_inches='tight',
          dpi=self.dpi * multiplier)


  # multiplier: this many times default. Larger means higher resolution, but
  #   font size may look smaller
  def set_dpi(self, fig, multiplier=1):

    # Set resolution of figure for saving
    self.dpi = fig.get_dpi()
    print("DPI:")
    print(self.dpi)
    self.defaultSize = fig.get_size_inches()
    print("Default size in Inches", self.defaultSize)
    print("Which should result in a %i x %i Image" % (
      self.dpi * self.defaultSize[0], self.dpi * self.defaultSize[1]))

    fig.set_size_inches(self.defaultSize[0] * multiplier,
      self.defaultSize[0] * multiplier)
    Size = fig.get_size_inches()
    print("Size in Inches:")
    print(Size)


  # Set plot parameters to plot on black background
  def black_background(self, have_legend=False, subplot_kw={}):

    # Set background color black
    ax = plt.gca ()
    ax.set_facecolor('black')
    fig = plt.gcf ()
    fig.set_facecolor ('black')

    # Font color
    plt.rcParams['axes.titlecolor'] = 'white'

    # See all rc params
    print(plt.rcParams.keys())
 
    # Make axes labels white
    # Doesn't work for polar plots
    if 'projection' in subplot_kw.keys() and \
        subplot_kw['projection'] != 'polar':
      ax.spines ['bottom'].set_color ('white')
      ax.spines ['top'].set_color ('white')
      ax.spines ['left'].set_color ('white')
      ax.spines ['right'].set_color ('white')

    ax.xaxis.label.set_color ('white')
    ax.tick_params (axis='x', colors='white')

    ax.yaxis.label.set_color ('white')
    ax.tick_params (axis='y', colors='white')

    if have_legend:
      # Set legend to be white on black
      legend = plt.legend (loc=0, fontsize=10)

      # Set legend background color
      legend.get_frame ().set_facecolor (self.PLOT_BG_COLOR)
      # If background is black, set white text color
      if self.PLOT_BG_COLOR == 'black':
        legend.get_frame ().set_edgecolor ('white')
        for text in legend.get_texts ():
          text.set_color ('white')


def main():

  plotter = Plotter()

  #plotter.plot_positional()

  plotter.plot_angles()

  # The midline_angle in npz is exactly the same as the absolute angles in the
  # csv, pointless to replot.
  #plotter.plot_posture()
 
  plt.show()


if __name__ == '__main__':
  main()
