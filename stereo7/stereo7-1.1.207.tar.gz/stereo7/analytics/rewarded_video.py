import parse_csv
import diagram


def collect(deck, upgrader):
    table_deck = parse_csv.parse(deck)
    table_upgrader = parse_csv.parse(upgrader)
    table_deck.save('AdsVideoResult_deck_raw.txt')
    table_upgrader.save('AdsVideoResult_upgrader_raw.txt')
    caption_deck = 'Ads Video Result (Deck Selector + Cards Upgrader)\n' + deck + '\n' + upgrader

    count_yes = table_deck.count_if('result_reward', '"{}"=="yes"')
    count_no = table_deck.count_if('result_reward', '"{}"=="no"')
    count_no_inet = table_deck.count_if('internet', '"{}"=="no"')
    count_no_inet = min(count_no_inet, count_no)
    fillrate = round(100.0 * count_yes / (count_yes + count_no - count_no_inet), 1)
    fillrate2 = round(100.0 * count_yes / (count_yes + count_no), 1)

    total = len(table_deck.rows) + len(table_upgrader.rows)
    play_deck = round(100.0 * len(table_deck.rows) / total, 1)
    play_upgr = round(100.0 * len(table_upgrader.rows) / total, 1)

    count = max(table_deck.max('player_progress'), table_upgrader.max('player_level'))
    values = []
    values2 = []
    print 'Level:\tImpressions'
    for level in xrange(count + 1):
        value = table_deck.count_if('player_progress', '{}==%s' % level)
        value2 = table_upgrader.count_if('player_level', '{}==%s' % level)
        values.append(value)
        values2.append(value2)
    diagram.build(values, caption_deck, 'ads_rewarded_video.png',
                  values2=values2,
                  add_to_index=0,
                  add_text='''
        Fillrate with internet: {}%
        Fillrate total: {}%
        Impressions on deck selector: {}%
        Impressions on cards upgrader: {}%
        Total impresions count: {}
        '''.format(fillrate, fillrate2, play_deck, play_upgr, count_yes + len(table_upgrader.rows)))


def main(argv):
    deck = 'AdsVideoResult.csv'
    upgrader = 'ShowVideoCardsUpgrader.csv'
    if len(argv) > 1:
        deck = argv[0]
        upgrader = argv[1]
    collect(deck, upgrader)

if __name__ == '__main__':
    main([])
