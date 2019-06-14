import parse_csv
import diagram


def interstials(file):
    table = parse_csv.parse(file)
    table.save('AdsInterstitial_raw.txt')
    caption = 'Ads interstitial\n' + file

    count_yes = table.count_if('ad_availabled', '"{}"=="yes"')
    count_no = table.count_if('ad_availabled', '"{}"=="no"')
    count_no_inet = table.count_if('internet', '"{}"=="no"')
    count_no_inet = min(count_no_inet, count_no)
    fillrate = round(100.0 * count_yes / (count_yes + count_no - count_no_inet), 1)
    fillrate2 = round(100.0 * count_yes / (count_yes + count_no), 1)

    count_normal = table.count_if('level_mode', '"{}"=="normal"')
    count_survival = table.count_if('level_mode', '"{}"=="survival"')
    normal = round(100.0 * count_normal / (count_normal + count_survival), 1)
    survival = round(100.0 * count_survival / (count_normal + count_survival), 1)

    count = table.max('level_index')
    values = []
    print 'Level:\tImpressions'
    for level in xrange(count + 1):
        value = table.count_if('level_index', '{}==%s' % level)
        print '{}\t{}'.format(level, value)
        values.append(value)
    values[0] -= count_survival
    diagram.build(values, caption, 'ads_interstitial.png', add_text='''
        Fillrate with internet: {}%
        Fillrate total: {}%
        Impresions on levels: {}%
        Impresions on survival: {}%
        '''.format(fillrate, fillrate2, normal, survival))


def main(argv):
    file = 'AdsInterstitial.csv'
    if len(argv) > 0:
        file = argv[0]
    interstials(file)

if __name__ == '__main__':
    main([])
