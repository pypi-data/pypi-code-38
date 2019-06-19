__all__ = ['pdb']


class Display(object):
    ID = None


class Parasite(object):
    data = None
    flags = None
    is_persistent = None
    is_undoable = None
    name = None

    def copy(self, *args, **kwargs):
        raise NotImplementedError()

    def has_flag(self, *args, **kwargs):
        raise NotImplementedError()

    def is_type(self, *args, **kwargs):
        raise NotImplementedError()


class Item(object):
    children = None
    parent = None


class Image(object):
    ID = None
    active_channel = None
    active_drawable = None
    active_layer = None
    active_vectors = None
    base_type = None
    channels = None
    colormap = None
    dirty = None
    filename = None
    floating_sel_attached_to = None
    floating_selection = None
    height = None
    layers = None
    name = None
    resolution = None
    selection = None
    tattoo_state = None
    unit = None
    uri = None
    vectors = None
    width = None

    def add_channel(self, *args, **kwargs):
        raise NotImplementedError()

    def add_hguide(self, *args, **kwargs):
        raise NotImplementedError()

    def add_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def add_vguide(self, *args, **kwargs):
        raise NotImplementedError()

    def attach_new_parasite(self, *args, **kwargs):
        raise NotImplementedError()

    def clean_all(self, *args, **kwargs):
        raise NotImplementedError()

    def crop(self, *args, **kwargs):
        raise NotImplementedError()

    def delete_guide(self, *args, **kwargs):
        raise NotImplementedError()

    def disable_undo(self, *args, **kwargs):
        raise NotImplementedError()

    def duplicate(self, *args, **kwargs):
        raise NotImplementedError()

    def enable_undo(self, *args, **kwargs):
        raise NotImplementedError()

    def find_next_guide(self, *args, **kwargs):
        raise NotImplementedError()

    def flatten(self, *args, **kwargs):
        raise NotImplementedError()

    def free_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def get_channel_by_tattoo(self, *args, **kwargs):
        raise NotImplementedError()

    def get_component_active(self, *args, **kwargs):
        raise NotImplementedError()

    def get_component_visible(self, *args, **kwargs):
        raise NotImplementedError()

    def get_guide_orientation(self, *args, **kwargs):
        raise NotImplementedError()

    def get_guide_position(self, *args, **kwargs):
        raise NotImplementedError()

    def get_layer_by_tattoo(self, *args, **kwargs):
        raise NotImplementedError()

    def insert_channel(self, *args, **kwargs):
        raise NotImplementedError()

    def insert_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def lower_channel(self, *args, **kwargs):
        raise NotImplementedError()

    def lower_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def lower_layer_to_bottom(self, *args, **kwargs):
        raise NotImplementedError()

    def merge_down(self, *args, **kwargs):
        raise NotImplementedError()

    def merge_visible_layers(self, *args, **kwargs):
        raise NotImplementedError()

    def new_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_attach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_detach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_find(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_list(self, *args, **kwargs):
        raise NotImplementedError()

    def pick_correlate_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def raise_channel(self, *args, **kwargs):
        raise NotImplementedError()

    def raise_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def raise_layer_to_top(self, *args, **kwargs):
        raise NotImplementedError()

    def remove_channel(self, *args, **kwargs):
        raise NotImplementedError()

    def remove_layer(self, *args, **kwargs):
        raise NotImplementedError()

    def resize(self, *args, **kwargs):
        raise NotImplementedError()

    def resize_to_layers(self, *args, **kwargs):
        raise NotImplementedError()

    def scale(self, *args, **kwargs):
        raise NotImplementedError()

    def set_component_active(self, *args, **kwargs):
        raise NotImplementedError()

    def set_component_visible(self, *args, **kwargs):
        raise NotImplementedError()

    def undo_freeze(self, *args, **kwargs):
        raise NotImplementedError()

    def undo_group_end(self, *args, **kwargs):
        raise NotImplementedError()

    def undo_group_start(self, *args, **kwargs):
        raise NotImplementedError()

    def undo_is_enabled(self, *args, **kwargs):
        raise NotImplementedError()

    def undo_thaw(self, *args, **kwargs):
        raise NotImplementedError()

    def unset_active_channel(self, *args, **kwargs):
        raise NotImplementedError()


class Vectors(Item):
    ID = None
    children = None
    image = None
    linked = None
    name = None
    parent = None
    strokes = None
    tattoo = None
    visible = None

    def parasite_attach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_detach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_find(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_list(self, *args, **kwargs):
        raise NotImplementedError()

    def remove_stroke(self, *args, **kwargs):
        raise NotImplementedError()

    def to_selection(self, *args, **kwargs):
        raise NotImplementedError()


class Drawable(Item):
    ID = None
    bpp = None
    children = None
    has_alpha = None
    height = None
    image = None
    is_gray = None
    is_grey = None
    is_indexed = None
    is_layer_mask = None
    is_rgb = None
    linked = None
    mask_bounds = None
    name = None
    offsets = None
    parent = None
    tattoo = None
    type = None
    type_with_alpha = None
    visible = None
    width = None

    def attach_new_parasite(self, *args, **kwargs):
        raise NotImplementedError()

    def fill(self, *args, **kwargs):
        raise NotImplementedError()

    def flush(self, *args, **kwargs):
        raise NotImplementedError()

    def free_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel_rgn(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile2(self, *args, **kwargs):
        raise NotImplementedError()

    def mask_intersect(self, *args, **kwargs):
        raise NotImplementedError()

    def merge_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def offset(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_attach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_detach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_find(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_list(self, *args, **kwargs):
        raise NotImplementedError()

    def set_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear_default(self, *args, **kwargs):
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        raise NotImplementedError()


class Layer(Drawable):
    ID = None
    apply_mask = None
    bpp = None
    children = None
    edit_mask = None
    has_alpha = None
    height = None
    image = None
    is_floating_sel = None
    is_gray = None
    is_grey = None
    is_indexed = None
    is_layer_mask = None
    is_rgb = None
    linked = None
    lock_alpha = None
    mask = None
    mask_bounds = None
    mode = None
    name = None
    offsets = None
    opacity = None
    parent = None
    preserve_trans = None
    show_mask = None
    tattoo = None
    type = None
    type_with_alpha = None
    visible = None
    width = None

    def add_alpha(self, *args, **kwargs):
        raise NotImplementedError()

    def add_mask(self, *args, **kwargs):
        raise NotImplementedError()

    def attach_new_parasite(self, *args, **kwargs):
        raise NotImplementedError()

    def copy(self, *args, **kwargs):
        raise NotImplementedError()

    def create_mask(self, *args, **kwargs):
        raise NotImplementedError()

    def fill(self, *args, **kwargs):
        raise NotImplementedError()

    def flush(self, *args, **kwargs):
        raise NotImplementedError()

    def free_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel_rgn(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile2(self, *args, **kwargs):
        raise NotImplementedError()

    def mask_intersect(self, *args, **kwargs):
        raise NotImplementedError()

    def merge_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def offset(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_attach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_detach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_find(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_list(self, *args, **kwargs):
        raise NotImplementedError()

    def remove_mask(self, *args, **kwargs):
        raise NotImplementedError()

    def resize(self, *args, **kwargs):
        raise NotImplementedError()

    def resize_to_image_size(self, *args, **kwargs):
        raise NotImplementedError()

    def scale(self, *args, **kwargs):
        raise NotImplementedError()

    def set_offsets(self, *args, **kwargs):
        raise NotImplementedError()

    def set_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear_default(self, *args, **kwargs):
        raise NotImplementedError()

    def translate(self, *args, **kwargs):
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        raise NotImplementedError()


class Channel(Drawable):
    ID = None
    bpp = None
    children = None
    color = None
    colour = None
    has_alpha = None
    height = None
    image = None
    is_gray = None
    is_grey = None
    is_indexed = None
    is_layer_mask = None
    is_rgb = None
    linked = None
    mask_bounds = None
    name = None
    offsets = None
    opacity = None
    parent = None
    show_masked = None
    tattoo = None
    type = None
    type_with_alpha = None
    visible = None
    width = None

    def attach_new_parasite(self, *args, **kwargs):
        raise NotImplementedError()

    def combine_masks(self, *args, **kwargs):
        raise NotImplementedError()

    def copy(self, *args, **kwargs):
        raise NotImplementedError()

    def fill(self, *args, **kwargs):
        raise NotImplementedError()

    def flush(self, *args, **kwargs):
        raise NotImplementedError()

    def free_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def get_pixel_rgn(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile(self, *args, **kwargs):
        raise NotImplementedError()

    def get_tile2(self, *args, **kwargs):
        raise NotImplementedError()

    def mask_intersect(self, *args, **kwargs):
        raise NotImplementedError()

    def merge_shadow(self, *args, **kwargs):
        raise NotImplementedError()

    def offset(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_attach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_detach(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_find(self, *args, **kwargs):
        raise NotImplementedError()

    def parasite_list(self, *args, **kwargs):
        raise NotImplementedError()

    def set_pixel(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_2d_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_flip_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_matrix_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_perspective_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_rotate_simple(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_scale_default(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear(self, *args, **kwargs):
        raise NotImplementedError()

    def transform_shear_default(self, *args, **kwargs):
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        raise NotImplementedError()
