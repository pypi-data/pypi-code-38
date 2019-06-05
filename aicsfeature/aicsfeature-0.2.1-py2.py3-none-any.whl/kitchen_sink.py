from .extractor import cell, cell_nuc, dna, structure


def kitchen_sink(
    im_cell,
    im_nuc,
    im_structures,
    seg_cell=None,
    seg_nuc=None,
    seg_structures=None,
    structure_names=None,
    extra_features=["io_intensity", "bright_spots", "intensity", "skeleton", "texture"],
):
    if seg_cell is not None:
        im_cell[seg_cell == 0] = 0

    if seg_nuc is not None:
        im_nuc[seg_nuc == 0] = 0

    if seg_structures is not None:
        for i in range(len(im_structures)):
            im_structures[i][seg_structures[i] == 0] = 0

    nuc_feats = dna.get_features(im_nuc, extra_features=extra_features)
    cell_feats = cell.get_features(im_cell, extra_features=extra_features)

    structure_feats = [
        structure.get_features(im_structure, extra_features=extra_features)
        for im_structure in im_structures
    ]

    polarity_feats = [
        cell_nuc.get_features(im_nuc > 0, im_cell, im_structure)
        for im_structure in im_structures
    ]

    return nuc_feats, cell_feats, structure_feats, polarity_feats
