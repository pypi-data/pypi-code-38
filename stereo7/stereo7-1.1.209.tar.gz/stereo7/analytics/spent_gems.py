import parse_csv
import diagram


def digit(value):
    value = str(int(value))
    result = ''
    for i in xrange(len(value)):
        if i > 0 and i % 3 == 0:
            result = '\'' + result
        result = value[len(value) - i - 1] + result
    return result


def main(argv):
    file = 'SpentGold.csv'
    if len(argv) > 0:
        file = argv[0]

    table = parse_csv.parse(file)
    table.save('SpentGems_raw.txt')

    count = {}
    sum = 0.0
    index_place = table.columns.index('where')
    index_count = table.columns.index('count')
    for row in table.rows:
        place = row[index_place]
        if place not in count:
            count[place] = 0
        count[place] += int(row[index_count])
        sum += int(row[index_count])

    description = 'Total: ' + digit(sum)
    for place in count:
        gems = digit(count[place])
        percent = round(count[place] / sum * 100, 1)
        description += '\n{}: {} ({}%)'.format(place, gems, percent)

    diagram.build([], 'Spend gems\n%s' % file, 'spend_gems.png',
                  add_text=description)

if __name__ == '__main__':
    main([])
