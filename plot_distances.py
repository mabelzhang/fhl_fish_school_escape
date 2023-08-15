#!/usr/bin/env python3

# Usage:
#   First, calculate distances and generate csv file:
#   $ python3 calc_fish_eye_to_partition.py <small|large>
#   Output: distances_<fish_size>.csv
#
#   Then plot from csv file:
#   $ python3 plot_distances.py
#   Input: distances_<fish_size>.csv
#   Output:
#     distances_<fish_size>_from_panel.eps
#     distances_<fish_size>_from_panel.png

import csv
import math
import sys

import numpy as np

import matplotlib.pyplot as plt

# fish_size: 'small' or 'large', substring for input and output file names
def main(fish_size):

  # Constant from calc_fish_eye_to_partition.py
  # d_b: Horizontal distance between partition and ball. Measured. Meters
  d_b = 0.185
  d_b_cm = d_b * 100

  beta_degs_field = 'beta(degs)'
  distance_field = 'distance(m)'
  fieldnames = [beta_degs_field, distance_field]

  beta_degs = []
  beta_rads = []
  dists = []

  # For plotting
  x_along_panel = []

  fieldnames = None
  with open('distances_' + fish_size + '.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    print('%s\t%s\tx along panel(m)' % (beta_degs_field, distance_field))

    for row in reader:
      # Degrees only for printing for human readability
      beta_deg = float(row[beta_degs_field])
      beta_degs.append(beta_deg)

      # Radians for all real calculations
      beta_rad = beta_deg * math.pi / 180.0
      beta_rads.append(beta_rad)

      # Since angle beta is from the ball stimulus, to plot correctly, x=0
      # needs to be position of ball, not of panel. So the triangle needs to be
      # measured from the ball. So need to add the offset from the panel, d_b.
      dist = float(row[distance_field]) + d_b
      dists.append(dist)

      # Calculate x for plotting
      curr_x = dist * math.tan(beta_rad)
      x_along_panel.append(curr_x)

      print('%g\t\t%g\t%g' % (beta_deg, float(row[distance_field]), curr_x)),


  w, h = plt.figaspect(0.3)
  fig, ax = plt.subplots(figsize=(w, h))

  # Dists vs x along panel
  x_along_panel_cm = np.array(x_along_panel) * 100
  dists_cm = np.array(dists) * 100

  # Shift all the points by -d_b in y, so that we get the distance from the
  # panel, not from the ball. (Though the distances need to be calculated from
  # the ball because beta angle starts at the ball.)
  ys = dists_cm - d_b_cm
  bar_hdl = ax.bar(x_along_panel_cm, ys, color='g')

  bar_lbls = []
  for i in range(len(ys)):
    bar_lbls.append('%.1f\n%d$^\circ$' % (ys[i], beta_degs[i]))
  ax.bar_label(bar_hdl, labels=bar_lbls)

  plt.title('Distance from panel at various angles from stimulus '
    'located at (0, -%g)' % (d_b_cm))
  plt.xlabel('x along panel (cm), panel width 76 cm')
  plt.ylabel('Distance from panel (cm)')
  plt.ylim([0, np.max(ys) + 2])

  # Eliminate white spaces before saving
  plt.tight_layout()
  plt.savefig('distances_' + fish_size + '_from_panel.eps', bbox_inches='tight')
  plt.savefig('distances_' + fish_size + '_from_panel.png', bbox_inches='tight')

  plt.show()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('No arg specified.')
    print('Usage: python3 calc_fish_eye_to_partition.py <small|large>')
    sys.exit(1)

  if sys.argv[1] != 'small' and sys.argv[1] != 'large':
    print('Undefined arg for fish size.')
    print('Usage: python3 calc_fish_eye_to_partition.py <small|large>')
    sys.exit(1)

  print('Plotting for fish size: %s' % sys.argv[1])
  main(sys.argv[1])
