from io import BytesIO

from ipywidgets import interactive, IntSlider, Output, HBox
from IPython.display import clear_output, display, display_png

from imageio import imsave

from dtoolbioimage.util.array import pretty_color_array


def stack_viewer(stack):

    slider = IntSlider(min=0, max=100, step=1, continuous_update=False,
                       description='Z plane:', orientation='Vertical')

    o = Output()

    def update_viewer(change):
        with o:
            clear_output()
            display(stack[:, :, slider.value])


    slider.observe(update_viewer, 'value')
    update_viewer(None)

    return HBox([o, slider])


def simple_stack_viewer(stack):

    max_z = stack.shape[2]

    slider = IntSlider(min=0, max=max_z, step=1, description='Z plane:')

    def show_z_plane(z):
        if len(stack.shape) == 3:
            display_png(stack[:,:,z])
        else:
            display_png(stack[:,:,z,:])
    
    return interactive(show_z_plane, z=slider)


def cached_color_stack_viewer(stack):

    _, _, max_z, _ = stack.shape

    slider = IntSlider(min=0, max=max_z-1, step=1, description='Z plane:')

    png_byte_arrays = {}

    def show_z_plane(z):
        if z in png_byte_arrays:
            raw_png_rep = png_byte_arrays[z]
        else:
            b = BytesIO()
            imsave(b, stack[:,:,z,:], 'PNG', compress_level=0)
            raw_png_rep = b.getvalue()
            png_byte_arrays[z] = raw_png_rep

        display({'image/png': raw_png_rep}, raw=True)

    return interactive(show_z_plane, z=slider)


def cached_segmentation_viewer(stack):

    _, _, max_z = stack.shape

    slider = IntSlider(min=0, max=max_z-1, step=1, description='Z plane:')

    png_byte_arrays = {}

    def show_z_plane(z):
        if z in png_byte_arrays:
            raw_png_rep = png_byte_arrays[z]
        else:
            b = BytesIO()
            imsave(b, pretty_color_array(
                stack[:, :, z]), 'PNG', compress_level=0)
            raw_png_rep = b.getvalue()
            png_byte_arrays[z] = raw_png_rep

        display({'image/png': raw_png_rep}, raw=True)

    return interactive(show_z_plane, z=slider)
