#!/usr/bin/env python3

import math

# Usage:
#   Change args and constants as needed, then run:
#   $ python3 calc_fish_eye_to_partition.py

# Unit: SI units
#   Meters (converted to cm for printouts)
#   Radians

# Solves for d_p
# Parameters:
#   h_f: Height of fish eye from tank bottom. Estimated constant
def calc_fish_eye_to_partition_wo_Snell(h_f):

  # Measured quantities
  # h_p_prime: Height of partition from tank bottom. Measured
  h_p_prime = 0.075
  # h_b_prime: Height of ball bottom from tank bottom. Measured
  h_b_prime = 0.20
  # d_b: Horizontal distance between partition and ball. Measured
  d_b = 0.185

  # h_p: Height of partition from fish eye height
  h_p = h_p_prime - h_f
  # h_b: Height of ball bottom from fish eye height
  h_b = h_b_prime - h_f

  # d_p: Distance between fish eye and partition
  #   Unknown, solve for. Aim for <= 4 cm
  d_p = (h_p * d_b) / (h_b - h_p)

  print("WITHOUT Snell's law, distance from fish eye to "
    "partition before fish can see stimulus is approximately %f cm" % (
    d_p * 100))

  return d_p, h_p


# Solves for d_p_2
# Take Snell's law of refraction into consideration
# Parameters:
#   h_f: Height of fish eye from tank bottom. Estimated constant
#   h_w_prime: Height of water. May be different at different areas of tank
#     because uneven bottom (in order to drain).
def calc_fish_eye_to_partition(h_f, h_w_prime):

  # Without Snell's law
  d_p_1, h_p = calc_fish_eye_to_partition_wo_Snell(h_f)

  # h_w: Height of water from fish eye height
  h_w = h_w_prime - h_f

  # Angle from horizontal, of ray of fish eye to ball, without Snell's law
  theta0 = math.atan2(h_p, d_p_1)

  # Constant. Refractive index of water wrt air
  n21 = 1.33
  # Incident angle of Snell's law
  theta1 = 0.5 * math.pi - theta0
  # Refraction angle of Snell's law
  theta2 = math.asin(math.sin(theta1) / n21)

  # d_s: Horizontal distance between fish eye and the point of incident, where
  #   the eyesight ray of bottom of ball enters water to end up at fish eye.
  d_s = h_w * math.tan(theta2)

  # d_p_2: Horizontal distance between fish eye and panel, taking into account
  #   Snell's law of refraction.
  d_p_2 = d_p_1 - (h_w / math.tan(theta0)) + d_s

  print("WITH Snell's law, distance from fish eye to "
    "partition before fish can see stimulus is approximately %f cm" % (
    d_p_2 * 100))

  return d_p_2


if __name__ == '__main__':

  # Args to set each time

  # h_f_small: For small fish, height of fish eye from tank bottom. Estimated
  #   constant
  h_f_small = 0.02
  # h_w_prime_small: For small fish, height of water from tank bottom.
  h_w_prime_small = 0.07

  # Small fish
  print("For small fish:")
  dist = calc_fish_eye_to_partition(h_f=h_f_small, h_w_prime=h_w_prime_small)

  # Large fish
  #h_f_large = 
  #h_w_prime_large
  #calc_fish_eye_to_partition(h_f=h_f_large, h_w_prime=h_w_prime_large)
