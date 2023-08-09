#!/usr/bin/env python3

import math

# Usage:
#   Change args and constants as needed, then run:
#   $ python3 calc_fish_eye_to_partition.py

# Unit: SI units
#   Meters (converted to cm for printouts)
#   Radians

# From http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# ANSI colors https://gist.github.com/chrisopedia/8754917
#   These ones here fall into the "High Intensity" category
class ansi_colors:
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'  # green
  WARNING = '\033[93m'  # yellow
  FAIL = '\033[91m'  # red

  ENDC = '\033[0m'


class CalcExperimentSetup:

  def __init__(self):

    # Print inputs only once
    self.input_printed = False


  # Solves for d_p, without Snell's law of refraction.
  # Parameters:
  #   h_f: Height of fish eye from tank bottom. Estimated constant
  #   h_p_prime: Height of partition from tank bottom. Measured
  #   h_b_prime: Height of ball bottom from tank bottom. Measured
  #   beta: Angle between ball and fish eye. Default 0, fish is at shortest
  #     distance from ball, orthogonally in front of panel.
  def calc_fish_eye_to_partition_no_Snell(self, h_f, h_p_prime, h_b_prime,
    beta=0):

    # d_b: Horizontal distance between partition and ball. Measured
    d_b = 0.185
    # d_b_beta: Hypotenuse distance between ball and panel, at angle beta
    # If beta == pi/2 or -pi/2, will have division by zero
    if abs(beta - math.pi * 0.5) < 1e-6 or \
       abs(beta + math.pi * 0.5) < 1e-6:
      print('%sWARN: Angle beta is pi/2. Division by zero%s' %(
        ansi_colors.WARNING, ansi_colors.ENDC))

    d_b_beta = d_b / math.cos(beta)

    # h_p: Height of partition from fish eye height
    h_p = h_p_prime - h_f
    # h_b: Height of ball bottom from fish eye height
    h_b = h_b_prime - h_f

    # d_p: Distance between fish eye and partition
    #   Unknown, solve for. Aim for <= 4 cm
    d_p = (h_p * d_b_beta) / (h_b - h_p)

    if not self.input_printed:
      print('Input constants:')
      print('  h_f (fish eye level from tank bottom): %g' % h_f)
      print('  h_p_prime                            : %g' % h_p_prime)
      print('  h_b_prime                            : %g' % h_b_prime)
      print('  d_b                                  : %g' % d_b)

    # Debug output
    #print('Intermediate calculations:')
    #print('  d_b_beta : %g' % d_b_beta)

    print("WITHOUT Snell's law, distance from fish eye to "
      "partition before fish can see stimulus is approximately %.1f cm" % (
      d_p * 100))

    return d_p, h_p


  # Solves for d_p_2, taking Snell's law of refraction into consideration.
  # Parameters:
  #   h_f: Height of fish eye from tank bottom. Estimated constant
  #   h_p_prime: Height of partition from tank bottom. Measured
  #   h_b_prime: Height of ball bottom from tank bottom. Measured
  #   h_w_prime: Height of water. May be different at different areas of tank
  #     because uneven bottom (in order to drain).
  #   beta: Angle between ball and fish eye. Default 0, fish is at shortest
  #     distance from ball, orthogonally in front of panel.
  def calc_fish_eye_to_partition(self, h_f, h_p_prime, h_b_prime, h_w_prime,
    beta=0):

    # Without Snell's law
    d_p_1, h_p = self.calc_fish_eye_to_partition_no_Snell(
      h_f, h_p_prime, h_b_prime, beta)

    # h_w: Height of water from fish eye height
    h_w = h_w_prime - h_f
    if h_w <= 0.0:
      print('%sERROR: h_w (%f, height of water above fish eye) <= 0, invalid, '
        'fish would be out of water. Check your h_w_prime and h_f inputs.%s' %(
        ansi_colors.FAIL, h_w, ansi_colors.ENDC))

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

    # d_p_2_beta: Horizontal distance between fish eye and panel, taking into
    #   account Snell's law of refraction. If beta != pi/2, then this is the
    #   hypotenuse distance, not the orthogonal.
    d_p_2_beta = d_p_1 - (h_w / math.tan(theta0)) + d_s

    # d_p_2: Orthogonal distance between fish and panel
    d_p_2 = d_p_2_beta * math.sin(0.5 * math.pi - beta)

    if not self.input_printed:
      print('  h_w     : %g' % h_w)
      self.input_printed = True
    print("WITH Snell's law, distance from fish eye to "
      "partition before fish can see stimulus is approximately %.1f cm" % (
      d_p_2 * 100))

    return d_p_2


def main():

  calc = CalcExperimentSetup()

  # Args to set before running script

  # Small fish

  # h_f_small: For small fish, height of fish eye from tank bottom. Estimated
  #   constant. 2-3 cm
  h_f_small = 0.02

  # Measured quantities
  # h_p_prime: Height of partition from tank bottom. Measured
  h_p_prime_small = 0.075 # 0.075 before trials, 0.055 after trials
  # h_b_prime: Height of ball bottom from tank bottom. Measured
  h_b_prime_small = 0.20
  # h_w_prime_small: For small fish, height of water from tank bottom.
  h_w_prime_small = 0.07 # 0.07 before trials, 0.03 after trials

  print('For small Cymatogaster:')

  # beta: Angle between ball and fish eye. Default 0, fish is at shortest
  #   distance from ball, orthogonally in front of panel.
  # -90 to 90 degrees with 10 degree increments. Note at -90 and 90 will have
  #   division by zero. Ignore outputs.
  for beta_degs in range(-90, 100, 10):
    beta = beta_degs / 180.0 * math.pi
    print('  beta_degs                            : %g' % beta_degs)
    dist = calc.calc_fish_eye_to_partition(
      h_f=h_f_small,
      h_p_prime=h_p_prime_small,
      h_b_prime=h_b_prime_small,
      h_w_prime=h_w_prime_small,
      beta=beta)

  # Large fish

  # Estimated
  h_f_large = 0.03

  # Measured
  h_p_prime_large = 0.1
  h_b_prime_large = 0.23
  h_w_prime_large = 0.08

  print('For large Cymatogaster:')

  for beta_degs in range(-90, 100, 10):
    beta = beta_degs / 180.0 * math.pi
    print('  beta_degs                            : %g' % beta_degs)
    dist = calc.calc_fish_eye_to_partition(
      h_f=h_f_large,
      h_p_prime=h_p_prime_large,
      h_b_prime=h_b_prime_large,
      h_w_prime=h_w_prime_large,
      beta=beta)

if __name__ == '__main__':
  main()
