import random, math

def rrange(start, stop=None, step=None):
  '''
  Return a randomized range of integers using a linear congruential
  pseudo-random number generator.
  '''
  # Couresty of Thomas Lux: http://bit.ly/2FcrJKY

  # Set a default values the same way "range" does.
  if (stop == None):
    start, stop = 0, start
  if (step == None):
    step = 1
  # Use a mapping to convert a standard range into the desired range.
  mapping = lambda i: (i*step) + start
  # Compute the number of numbers in this range.
  maximum = (stop - start) // step
  # Seed range with a random integer.
  value = random.randint(0, maximum)
  # Construct an offset, multiplier, and modulus for a linear
  # congruential generator. These generators are cyclic and
  # non-repeating when they maintain the properties:
  #
  #   1) "modulus" and "offset" are relatively prime.
  #   2) ["multiplier" - 1] is divisible by all prime factors of "modulus".
  #   3) ["multiplier" - 1] is divisible by 4 if "modulus" is divisible by 4.
  #
  # Pick a random odd-valued offset.
  offset = random.randint(0,maximum) * 2 + 1
  # Pick a multiplier 1 greater than a multiple of 4.
  multiplier = 4*(maximum//4) + 1
  # Pick a modulus just big enough to generate all numbers (power of 2).
  modulus = int(2**math.ceil(math.log2(maximum)))
  # Track how many random numbers have been returned.
  found = 0
  while found < maximum:
    # If this is a valid value, yield it in generator fashion.
    if value < maximum:
      found += 1
      yield mapping(value)
    # Calculate the next value in the sequence.
    value = (value*multiplier + offset) % modulus
