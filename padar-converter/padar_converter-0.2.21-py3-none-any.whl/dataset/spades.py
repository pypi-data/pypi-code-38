import numpy as np
import pandas as pd


def to_inlab_activity_labels(annotation_labels, pid, st, et):
    label = annotation_labels.lower().replace(
        'wear on', '').replace('wearon', '').strip()

    # special cases
    if pid == 'SPADES_26':
        if 'biking' in label and st.hour == 11 and st.minute > 26:
            return "Stationary cycle ergometry"
    elif pid == 'SPADES_19':
        if '3 mph' in label and 'arms on desk' in label and 'treadmill' in label:
            return "Level treadmill walking at 3 mph with arms on desk"

    if 'stairs' in label and 'up' in label:
        return 'Walking upstairs'
    elif 'stairs' in label and 'down' in label:
        return 'Walking downstairs'
    if 'mbta' in label or 'city' in label or 'outdoor' in label:
        return 'Unknown'
    if "sitting" in label and 'writing' in label:
        return 'Sitting and writing'
    elif 'stand' in label and 'writ' in label:
        return 'Standing and writing at a table'
    elif 'sit' in label and ('web' in label or 'typ' in label):
        return 'Sitting and typing on a keyboard'
    elif 'reclin' in label and ('text' in label or 'web' in label):
        return 'Reclining and using phone'
    elif 'sit' in label and 'story' in label and ('city' not in label and 'outdoor' not in label):
        return "Sitting and talking"
    elif "reclin" in label and 'story' in label:
        return 'Reclining and talking'
    elif "stand" in label and ('web' in label or 'typ' in label):
        return "Standing and typing on a keyboard"
    elif 'bik' in label and ('stationary' in label or '300' in label):
        return "Stationary cycle ergometry"
    elif ('treadmill' in label or 'walk' in label) and '1' in label:
        return "Level treadmill walking at 1 mph with arms on desk"
    elif ('treadmill' in label or 'walk' in label) and '2' in label:
        return "Level treadmill walking at 2 mph with arms on desk"
    elif 'treadmill' in label and 'phone' in label:
        return "Level treadmill walking at 3-3.5 mph while holding a phone to the ear and talking"
    elif 'treadmill' in label and 'bag' in label:
        return "Level treadmill walking at 3-3.5 mph and carrying a bag"
    elif 'treadmill' in label and 'story' in label:
        return "Level treadmill walking at 3-3.5 mph while talking"
    elif ('treadmill' in label or 'walk' in label) and 'drink' in label:
        return 'Level treadmill walking at 3-3.5 mph and carrying a drink'
    elif ('treadmill' in label or 'walk' in label) and ('3.5' in label or '3' in label):
        return 'Level treadmill walking at 3-3.5 mph'
    elif '5.5' in label or 'jog' in label or 'run' in label:
        return 'Treadmill running at 5.5 mph & 5% grade'
    elif 'laundry' in label:
        return 'Standing and folding towels'
    elif 'sweep' in label:
        return 'Standing and sweeping'
    elif 'shelf' in label and 'load' in label:
        return 'Standing loading/unloading shelf'
    elif 'lying' in label:
        return "Lying on the back"
    elif label == 'sitting' or ('sit' in label and 'still' in label):
        return "Sitting still"
    elif label == "still" or 'standing' == label or label == 'standing still':
        return "Self-selected free standing"
    else:
        return 'Unknown'
