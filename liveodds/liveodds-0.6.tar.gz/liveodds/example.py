#!/usr/bin/env python3

import liveodds

race = liveodds.race(liveodds.list_race_times()[0])

print(race.runners())