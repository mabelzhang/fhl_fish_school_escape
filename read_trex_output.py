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


def main():

  in_dir = 'in/trexOut_cy_trial1_sch2_stim5'
  out_dir = os.path.join('out', os.path.basename(in_dir))

  # CSV contains positional data. NPZ contains posture data
  # Data for 1 fish
  # Each row is for one point in time
  in_base = 'cy_s_trial1_sch2_stim5_2023-08-04-14-08_fish4.csv'
  out_base = os.path.splitext(in_base)[0]

  in_full = os.path.join(in_dir, in_base)
  out_prefix = os.path.join(out_dir, out_base)

  if not os.path.exists(out_dir):
    os.mkdir(out_dir)

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

  frames = []
  px = []
  py = []
  vx = []
  vy = []
  ax = []
  ay = []
  angles = []

  #####
  # Read csv output file from TRex
  with open(in_full, 'r') as f:
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
      px.append(float(row[X_FD]))
      py.append(float(row[Y_FD]))

      vx.append(float(row[VX_FD]))
      vy.append(float(row[VY_FD]))

      ax.append(float(row[AX_FD]))
      ay.append(float(row[AY_FD]))

      angles.append(float(row[ANGLE_FD]))

      print('frame %d, px %g, py %g, vx %g, vy %g, ax %g, ay %g, angle %g' % (
        frames[n_valid_rows], px[n_valid_rows], py[n_valid_rows],
        vx[n_valid_rows], vy[n_valid_rows],
        ax[n_valid_rows], ay[n_valid_rows],
        angles[n_valid_rows]))

      n_valid_rows += 1

  fig, axes = plt.subplots()

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
  plt.plot(frames, np.array(angles) * 180 / np.pi)
  plt.title('absolute angle')

  # Set resolution of figure for saving
  DPI = fig.get_dpi()
  print("DPI:")
  print(DPI)
  defaultSize = fig.get_size_inches()
  print("Default size in Inches", defaultSize)
  print("Which should result in a %i x %i Image" % (
    DPI * defaultSize[0], DPI * defaultSize[1]))
  fig.set_size_inches(defaultSize[0] * 2, defaultSize[0] * 2)
  Size = fig.get_size_inches()
  print("Size in Inches:")
  print(Size)

  # Eliminate white spaces before saving
  plt.tight_layout()
  plt.title(in_base)
  plt.savefig(out_prefix + '.eps', bbox_inches='tight')
  plt.savefig(out_prefix + '.png', bbox_inches='tight')

  #plt.show()


  # Polar plot of absolute angles

  r = [1.0] * len(angles)
  figp, axesp = plt.subplots(subplot_kw={'projection': 'polar'})

  # This looks even more wrong
  # Crappy hack because TRex tracking kept switching 180 degrees. Take abs val
  # just to get an idea. Need to do this a better way - only swap angles if
  # delta between frames is exactly 180 degrees, don't swap otherwise, because
  # there may be small angles that are genuinely going from say -10 to 10 in a
  # fraction of a second
  #angles = np.abs(angles)

  # Raw line plot through time
  #axesp.plot(angles, r)


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
  axesp.bar(angles_bin_pts, angles_hist, width=hist_width, bottom=0.0,
    color=hist_colors, alpha=0.5)

  # Save figure
  figp.set_size_inches(defaultSize[0] * 2, defaultSize[0] * 2)
  Size = figp.get_size_inches()
  # Eliminate white spaces before saving
  plt.tight_layout()
  plt.title(in_base)
  plt.savefig(out_prefix + '_angles.eps', bbox_inches='tight')
  plt.savefig(out_prefix + '_angles.png', bbox_inches='tight')

  plt.show()


if __name__ == '__main__':
  main()
