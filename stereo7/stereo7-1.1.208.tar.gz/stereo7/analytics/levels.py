import parse_csv
import diagram

caption = ''


def leaks(table):
    count = table.max('level')
    values = []
    count_survival = table.count_if('mode', '"{}"=="survival"')
    print 'Level:\tCount events'
    for level in xrange(count + 1):
        value = table.count_if('level', '{}==%s' % level)
        print '{}\t{}'.format(level, value)
        values.append(value)
    values[0] -= count_survival
    diagram.build(values, caption, 'levels_first_finish.png', total_as_max=True)


def main(argv):
    global caption
    file = 'LevelFirstFinish.csv'
    if len(argv) > 1:
        file = argv[1]
    table = parse_csv.parse(file)
    table.save('LevelFirstFinish_raw.txt')
    caption = 'Leaks on levels\n' + file
    leaks(table)

if __name__ == '__main__':
    main([])
