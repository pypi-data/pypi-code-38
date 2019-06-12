#!/usr/bin/env python

"""
problem for fixed number of axes:
  given a set R of i ranges (rmin_i, rmax_i) where rmin_i <= rmax_i,
  for a given n, find a set A of n ranges (amin_i, amax_i) where amin_i <= amax_i,
    and a map m from R i -> A j such that amin_j <= rmin_i and rmax_i <= amax_j
  that minimises the function
    sum( 1 / ((rmax_i - rmin_i) / (amax_j - amin_j)) for i in R where j = m(i) )

  Note: m is easy to find once you have the set A:
    for each i, m[i] is the j that maximises (rmax_i - rmin_i) / (amax_j - amin_j)
  Note: A will not always be a subset of R. but Amin is a subset of Rmin and Amax is a subset of Rmax

  Current solution:
    construct the set of all possible rmin_i, rmax_j where rmin_i <= rmax_j
    do a depth first search of all the possible maps m,
      discarding when m produces an A that is larger than n
      calculate the function
      and return the best set found
    heuristic speed up that may miss the best solution:
      inside the search, cut down the number of options returned

problem for variable number of axes:
  given a set R of i ranges (rmin_i, rmax_i) where rmin_i <= rmax_i,
  for any n <= i, find a set A of n ranges (amin_i, amax_i) where amin_i <= amax_i,
    and a map m from R i -> A j such that amin_j <= rmin_i and rmax_i <= amax_j
  that minimises the function
    sum( n / ((rmax_i - rmin_i) / (amax_j - amin_j)) for i in R where j = m(i) )

  Note: this assumes that there is a balance between the number of axes and the variability
    It's basically trying to maximise the visible area that each range maps to
  Note: the above notes apply
  Note: This is very much a geometric mean.

  Possible solution:
    Do a breadth-first search
      try map each i -> j in order of the decreasing value of (rmax_i - rmin_i) / (amax_j - amin_j)

  Better idea:
    The more we can describe mathematically, the more we can cut out of the search
    AM-GM inequality may be appropriate
    Try and prove some commutivity property: then any increase is worth it, continue till we can't any more

  Idea:
    See it as partitions of the set R. Then A and m can be logically deduced
    Counting the number of partitions may help
    Finding a way to order the partitions may help

  Containability:
    For any j, amin_j = min(rmin_i) where m(i) = j and amax_j = max(rmax_i) where m(i) = j
    This means that we just need find the best set of subsets (as in Idea above)
    Find a set S of disjoint subsets S_j of R that minimises the function
      sum( n * ((rmax_i - rmin_i) / (smax_j - smin_j)) for i in R where j is the subset of S that i belongs to

  Hope:
    The solution set S can be find by choosing the best improvements in order
"""

import math

def tagmaptoaxismap(tagmap):
  """converts a tag: (score, axis) dict to a axis: [tag, tag, tag...] dict"""
  axismap = {}
  for tag, (score, axis) in tagmap.items():
    if axis in axismap:
      axismap[axis].append(tag)
    else:
      axismap[axis] = [tag]
  if not axismap:
    axismap[(0,100)] = []
  return axismap

def sortaxes(axes):
  """returns the list of axes sorted in increasing order by range"""
  axisranges = [(amax-amin, (amin, amax)) for amin, amax in axes]
  axisranges.sort()
  return [axis for axisrange, axis in axisranges]

def score(ranges, tagmap):
  """we want to maximise this: the GM of the areas covered"""
  score = 0
  if not tagmap:
    return 0
  for tag, (rmin, rmax) in ranges.items():
    amin, amax = tagmap[tag]
    try:
      score += 1 / ((rmax - rmin) / float(amax - amin))
    except ZeroDivisionError:
      score += 1
  numaxes = len(dict.fromkeys(list(tagmap.values())))
  wastedspace = (numaxes - 1) * 5
  return ((100 - wastedspace) / score) / numaxes

def calculateaxes(ranges):
  """flagrantly override the previous method"""
  for tagname, (rmin, rmax) in list(ranges.items()):
    ranges[tagname] = math.floor(rmin),math.ceil(rmax)
  # print 'ranges', ranges
  def groups2tagmap(groups):
    tagmap = {}
    for group, range in groups.items():
      for tag in group:
        tagmap[tag] = range
    return tagmap
  groups = dict([((tag,), (rmin, rmax)) for tag, (rmin, rmax) in ranges.items()])
  tagmap = groups2tagmap(groups)
  bestscore = score(ranges, tagmap)
  bestgroups = groups
  foundimprovement = True
  numaxes = len(groups)
  while foundimprovement and numaxes > 1:
    thisbestscore = bestscore
    thisbestgroups = bestgroups
    foundimprovement = False
    # print "trying for improvement at", numaxes
    for group1, (a1_min, a1_max) in bestgroups.items():
      for group2, (a2_min, a2_max) in bestgroups.items():
        # don't need to try both ways or on the same tag
        if group1 <= group2: continue
        if (a1_min, a1_max) == (a2_min, a2_max): continue
        a_min = min(a1_min, a2_min)
        a_max = max(a1_max, a2_max)
        groups = bestgroups.copy()
        del groups[group1]
        del groups[group2]
        groups[group1+group2] = (a_min, a_max)
        tagmap = groups2tagmap(groups)
        thisscore = score(ranges, tagmap)
        # print thisscore, ", ".join(["%s: %r..%r" % (tag, rmin, rmax) for tag, (rmin, rmax) in tagmap.iteritems()])
        if thisscore > thisbestscore:
          thisbestscore, thisbestgroups = thisscore, groups
          foundimprovement = True
    if foundimprovement:
      bestscore, bestgroups = thisbestscore, thisbestgroups
      numaxes = len(bestgroups)
      # print "best at", numaxes, bestscore, bestgroups
  bestmap = groups2tagmap(bestgroups)
  for tag1, (r1_min, r1_max) in list(bestmap.items()):
    bestmap[tag1] = (0, (r1_min, r1_max))
  return bestmap

