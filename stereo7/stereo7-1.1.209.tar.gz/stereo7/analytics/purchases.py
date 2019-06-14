import parse_csv
import diagram

caption = ''


def remove_fakes(table):
    uids = table.select('uid')
    percent = 0.0
    for i, uid in enumerate(uids):
        if(uid == ''):
            continue
        count = table.count_if('uid', '"{}"=="%s"' % uid)
        if count > 2:
            table.remove_if('uid', '"{}"=="%s"' % uid)
        percent_ = round(float(i) / len(uids) * 100, 0)
        if percent_ > percent:
            percent = percent_
            print '{}%, rows={}'.format(percent, len(table.rows))


def purchases_by_level(table):
    count = table.max('level')
    values = []
    print 'Level:\tCount Purchases'
    for level in xrange(count + 1):
        value = table.count_if('level', '{}==%s' % level)
        print '{}\t{}'.format(level, value)
        values.append(value)
    diagram.build(values, caption, 'purchases_by_levels.png')


def main(argv):
    file = 'PurchaseSuccessful.csv'
    if len(argv) > 0:
        file = argv[0]

    global caption
    table = parse_csv.parse(file)
    remove_fakes(table)
    table.save('PurchaseSuccessful_raw.txt')
    caption = 'Purchases on levels\n' + file
    purchases_by_level(table)


if __name__ == '__main__':
    main([])
