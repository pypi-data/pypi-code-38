import itertools


def table(entries, columns, rows):
    def one_table(entries):
        assert len(entries) == columns * rows
        width = round(100 / columns, 2)
        yield '<table>'
        for y in range(rows):
            yield '  <tr>'
            for x in range(columns):
                entry = entries[x + y * columns]
                style = '' if y else f' style="width:{width}%;"'
                yield f'    <td{style}>{entry}</td>'
            yield '  </tr>'
            if not entry:
                break

        yield '</table>'

    it = [iter(entries)] * (columns * rows)
    for group in itertools.zip_longest(*it, fillvalue=''):
        yield '\n'.join(one_table(group))


def qr_table(files, columns, rows):
    return table((f' <img src="{f}"/> ' for f in files), columns, rows)
