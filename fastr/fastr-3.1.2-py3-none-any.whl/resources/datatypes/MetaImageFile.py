import os.path
import re
import fastr
from fastr.data import url
from fastr.datatypes import URLType
from fastr.helpers.checksum import md5_checksum, hashsum


class MetaImageFile(URLType):
    description = 'Meta Image file format'
    extension = 'mhd'

    def _validate(value):
        value = value.value

        try:
            if url.isurl(value):
                value = url.get_path_from_url(value)
            fastr.log.debug('Check if {} exists...'.format(value))
            return os.path.exists(value)
        except ValueError:
            return False

    def __eq__(self, other):
        if not isinstance(other, MetaImageFile):
            return NotImplemented

        self_header = self._parse()
        other_header = other._parse()

        self_raw = url.normurl(url.join(os.path.dirname(self.parsed_value), self_header['ElementDataFile']))
        other_raw = url.normurl(url.join(os.path.dirname(other.parsed_value), other_header['ElementDataFile']))

        # These are allowed to be different as long as their content is the same
        del self_header['ElementDataFile']
        del other_header['ElementDataFile']

        if self_header != other_header:
            return False

        if md5_checksum(self_raw) != md5_checksum(other_raw):
            return False

        return True

    def checksum(self):
        """
        Return the checksum of this MetaImageFile

        :return: checksum string
        :rtype: str
        """
        header = self._parse()
        raw = url.normurl(url.join(os.path.dirname(self.parsed_value), header['ElementDataFile']))

        del header['ElementDataFile']

        with open(raw, 'rb') as fh_in:
            result = hashsum([header, fh_in])

        return result

    def _parse(self):
        data = {}
        with open(self.parsed_value) as header_file:
            for line in header_file:
                if line.strip()[0] == '#':
                    continue

                key, value = line.split('=', 1)
                data[key.strip()] = value.strip()
        return data

    @classmethod
    def content(cls, invalue, outvalue=None):
        fastr.log.debug('Determining content of MetaImageFile from invalue "{}" and outvalue "{}"'.format(invalue, outvalue))
        if url.isurl(invalue):
            if outvalue is None or url.isurl(outvalue):
                raise ValueError('Either invalue or outvalue should be a path')

            value = outvalue
            invalue_dir = url.dirurl(invalue)
        else:
            value = invalue
            invalue_dir = os.path.dirname(invalue)

        if outvalue is not None:
            if url.isurl(outvalue):
                outvalue_dir = url.dirurl(outvalue)
            else:
                outvalue_dir = os.path.dirname(outvalue)

            contents = [(invalue, outvalue)]
        else:
            contents = [invalue]

        try:
            fastr.log.debug('Trying to open header file: {}'.format(value))
            with open(value, 'r') as fin:
                # This is dangerous for large files, but mhd headers should be
                # small so we should be fine (we can change to loop over lines)
                data = fin.read()

                # Find datafile using a multiline regexp
                match = re.search(r'^ElementDataFile\s+=\s+(.*)$', data, re.MULTILINE)

                # Get filename and make absolute
                datafile = match.group(1)
                if datafile[0] in '/\\':
                    message = 'Fastr does not support MetaImageFiles with absolute paths!'
                    fastr.log.critical(message)
                    raise ValueError(message)

                if outvalue is not None:
                    contents.append((url.normurl(url.join(invalue_dir, datafile)),
                                     url.normurl(url.join(outvalue_dir, datafile))))
                else:
                    contents.append(url.normurl(url.join(invalue_dir, datafile)))
        except Exception:
            message = 'Cannot determine ElementDataFile for {}'.format(value)
            fastr.log.critical(message)
            raise ValueError(message)

        return contents
