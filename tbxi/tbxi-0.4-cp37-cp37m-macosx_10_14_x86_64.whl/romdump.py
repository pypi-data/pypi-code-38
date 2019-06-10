from .lowlevel import SuperMarioHeader, ResHeader, ResEntry, FakeMMHeader, COMBO_FIELDS


PAD = b'kc' * 100


def strip_checksum(binary):
    binary = bytearray(binary)

    header = SuperMarioHeader.unpack_from(binary)
    modified_header = header._asdict()

    for k in list(modified_header):
        if k.startswith('CheckSum'): modified_header[k] = 0

    SuperMarioHeader.pack_into(binary, 0, **modified_header)

    return bytes(binary)


def confirm_supermario(binary):
    return (PAD in binary)


def extract_decldata(binary):
    return binary[binary.rfind(PAD) + len(PAD):]


def extract_resource_offsets(binary):
    # chase the linked list around
    offsets = []

    reshead = SuperMarioHeader.unpack_from(binary).RomRsrc
    link = ResHeader.unpack_from(binary, reshead).offsetToFirst
    while link:
        offsets.append(link)
        link = ResEntry.unpack_from(binary, link).offsetToNext

    offsets.reverse()
    return offsets


def dump(binary, dest_dir):
    if not confirm_supermario(binary):
        raise ValueError('not a SuperMario ROM')

    header = SuperMarioHeader.unpack_from(binary)
    binary = strip_checksum(binary)
    main_code = binary[:header.RomRsrc]
    decldata = extract_decldata(binary)

    combo_field_pad = max(len(v) for v in COMBO_FIELDS.values())

    # now for the tricky bit: resources :(
    for offset in extract_resource_offsets(binary):
        entry = ResEntry.unpack_from(binary, offset)
        mmhead = FakeMMHeader.unpack_from(binary, entry.offsetToData - FakeMMHeader.size)

        # assert entry.
        assert mmhead.MagicKurt == b'Kurt'
        assert mmhead.MagicC0A00000 == 0xC0A00000
        
        # Now, just need to dream up a data format
        report_combo_field = COMBO_FIELDS.get(entry.combo, '0x%2X' % entry.combo)
        print(entry.rsrcType, str(entry.rsrcID).rjust(6), report_combo_field.rjust(combo_field_pad), entry.rsrcName.decode('mac_roman'))
