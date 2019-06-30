import sys
import purchases
import interstitials
import levels
import rewarded_video
import spent_gems


def analytics(command, arg_parser):
    command
    files = sys.argv[2:]
    if command == 'an_purchases':
        purchases.main(files)
    elif command == 'an_interstitial':
        interstitials.main(files)
    elif command == 'an_levels':
        levels.main(files)
    elif command == 'an_video':
        rewarded_video.main(files)
    elif command == 'an_gems':
        spent_gems.main(files)
