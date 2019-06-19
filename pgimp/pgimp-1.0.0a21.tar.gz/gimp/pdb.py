from typing import List, Tuple
from gimp import Item, Display, Image, Layer, Channel, Drawable, Vectors, Parasite, Color, Selection, ColorArray, Status


def extension_gimp_help(num_domain_names: int, domain_names: List[str], num_domain_uris: int, domain_uris: List[str]):
    """
    :param num_domain_names: 
    :param domain_names: 
    :param num_domain_uris: 
    :param domain_uris: 
    """
    raise NotImplementedError()


def extension_script_fu():
    """
    A scheme interpreter for scripting GIMP operations

    More help here later
    """
    raise NotImplementedError()


def file_bmp_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files of Windows BMP file format

    Loads files of Windows BMP file format

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_bmp_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves files in Windows BMP file format

    Saves files in Windows BMP file format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_bz2_load(filename: str, raw_filename: str) -> Image:
    """
    loads files compressed with bzip2

    This procedure loads files in the bzip2 compressed format.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_bz2_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    saves files compressed with bzip2

    This procedure saves files in the bzip2 compressed format.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_cel_load(filename: str, raw_filename: str, palette_filename: str) -> Image:
    """
    Loads files in KISS CEL file format

    This plug-in loads individual KISS cell files.

    :param filename: Filename to load image from
    :param raw_filename: Name entered
    :param palette_filename: Filename to load palette from
    :return: image
    """
    raise NotImplementedError()


def file_cel_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, palette_filename: str):
    """
    Saves files in KISS CEL file format

    This plug-in saves individual KISS cell files.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: Filename to save image to
    :param raw_filename: Name entered
    :param palette_filename: Filename to save palette to
    """
    raise NotImplementedError()


def file_colorxhtml_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, source: str, characters: str, font_size: int, separate: int):
    """
    Save as colored XHTML

    Saves the image as colored XHTML text (based on Perl version by Marc Lehmann)

    :param image: Input image
    :param drawable: Input drawable
    :param filename: The name of the file
    :param raw_filename: The name of the file
    :param source: Character source
    :param characters: File to read or characters to use
    :param font_size: Font size in pixels
    :param separate: Write a separate CSS file
    """
    raise NotImplementedError()


def file_csource_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Dump image data in RGB(A) format for C source

    CSource cannot be run non-interactively.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_desktop_link_load(filename: str, raw_filename: str) -> Image:
    """
    Follows a link to an image in a .desktop file

    Opens a .desktop file and if it is a link, it asks GIMP to open the file the link points to.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_dicom_load(filename: str, raw_filename: str) -> Image:
    """
    loads files of the dicom file format

    Load a file in the DICOM standard format.The standard is defined at http://medical.nema.org/. The plug-in currently only supports reading images with uncompressed pixel sections.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_dicom_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Save file in the DICOM file format

    Save an image in the medical standard DICOM image formats. The standard is defined at http://medical.nema.org/. The file format is defined in section 10 of the standard. The files are saved uncompressed and the compulsory DICOM tags are filled with default dummy values.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save
    :param raw_filename: The name of the file to save
    """
    raise NotImplementedError()


def file_eps_load(filename: str, raw_filename: str) -> Image:
    """
    load Encapsulated PostScript images

    load Encapsulated PostScript images

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_eps_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, width: float, height: float, x_offset: float, y_offset: float, unit: int, keep_ratio: int, rotation: int, eps_flag: int, preview: int, level: int):
    """
    save image as Encapsulated PostScript image

    PostScript saving handles all image types except those with alpha channels.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param width: Width of the image in PostScript file (0: use input image size)
    :param height: Height of image in PostScript file (0: use input image size)
    :param x_offset: X-offset to image from lower left corner
    :param y_offset: Y-offset to image from lower left corner
    :param unit: Unit for width/height/offset. 0: inches, 1: millimeters
    :param keep_ratio: 0: use width/height, 1: keep aspect ratio
    :param rotation: 0, 90, 180, 270
    :param eps_flag: 0: PostScript, 1: Encapsulated PostScript
    :param preview: 0: no preview, >0: max. size of preview
    :param level: 1: PostScript Level 1, 2: PostScript Level 2
    """
    raise NotImplementedError()


def file_faxg3_load(filename: str, raw_filename: str) -> Image:
    """
    loads g3 fax files

    This plug-in loads Fax G3 Image files.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_fits_load(filename: str, raw_filename: str) -> Image:
    """
    load file of the FITS file format

    load file of the FITS file format (Flexible Image Transport System)

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_fits_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    save file in the FITS file format

    FITS saving handles all image types except those with alpha channels.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_fli_info(filename: str) -> Tuple[int, int, int]:
    """
    Get information about a Fli movie

    This is a experimantal plug-in to handle FLI movies

    :param filename: The name of the file to get info
    :return: width, height, frames
    """
    raise NotImplementedError()


def file_fli_load(filename: str, raw_filename: str) -> Image:
    """
    load FLI-movies

    This is an experimantal plug-in to handle FLI movies

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_fli_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, from_frame: int, to_frame: int):
    """
    save FLI-movies

    This is an experimantal plug-in to handle FLI movies

    :param image: Input image
    :param drawable: Input drawable (unused)
    :param filename: The name of the file to save
    :param raw_filename: The name entered
    :param from_frame: Save beginning from this frame
    :param to_frame: End saving with this frame
    """
    raise NotImplementedError()


def file_gbr_load(filename: str, raw_filename: str) -> Image:
    """
    Loads GIMP brushes

    Loads GIMP brushes (1 or 4 bpp and old .gpb format)

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_gbr_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, spacing: int, description: str):
    """
    Saves files in the GIMP brush file format

    Saves files in the GIMP brush file format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param spacing: Spacing of the brush
    :param description: Short description of the brush
    """
    raise NotImplementedError()


def file_gif_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files of Compuserve GIF file format

    FIXME: write help for gif_load

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_gif_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Loads only the first frame of a GIF image, to be used as a thumbnail


    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_gif_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, interlace: int, loop: int, default_delay: int, default_dispose: int):
    """
    saves files in Compuserve GIF file format

    Save a file in Compuserve GIF format, with possible animation, transparency, and comment.  To save an animation, operate on a multi-layer file.  The plug-in will intrepret <50% alpha as transparent.  When run non-interactively, the value for the comment is taken from the 'gimp-comment' parasite.  

    :param image: Image to save
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    :param interlace: Try to save as interlaced
    :param loop: (animated gif) loop infinitely
    :param default_delay: (animated gif) Default delay between framese in milliseconds
    :param default_dispose: (animated gif) Default disposal type (0=`don't care`, 1=combine, 2=replace)
    """
    raise NotImplementedError()


def file_gih_load(filename: str, raw_filename: str) -> Image:
    """
    loads images in GIMP brush pipe format

    This plug-in loads a GIMP brush pipe as an image.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_gih_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, spacing: int, description: str, cell_width: int, cell_height: int, display_cols: int, display_rows: int, dimension: int, rank: List[int], sel: List[str]):
    """
    saves images in GIMP brush pipe format

    This plug-in saves an image in the GIMP brush pipe format. For a colored brush pipe, RGBA layers are used, otherwise the layers should be grayscale masks. The image can be multi-layered, and additionally the layers can be divided into a rectangular array of brushes.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the brush pipe in
    :param raw_filename: The name of the file to save the brush pipe in
    :param spacing: Spacing of the brush
    :param description: Short description of the brush pipe
    :param cell_width: Width of the brush cells
    :param cell_height: Width of the brush cells
    :param display_cols: Display column number
    :param display_rows: Display row number
    :param dimension: Dimension (again)
    :param rank: Ranks of the dimensions
    :param sel: Selection modes
    """
    raise NotImplementedError()


def file_glob(pattern: str, encoding: int) -> Tuple[int, List[str]]:
    """
    Returns a list of matching filenames

    This can be useful in scripts and other plugins (e.g., batch-conversion). See the glob(7) manpage for more info. Note however that this isn't a full-featured glob implementation. It only handles simple patterns like "/home/foo/bar/*.jpg".

    :param pattern: The glob pattern (in UTF-8 encoding)
    :param encoding: Encoding of the returned names: { UTF-8 (0), filename encoding (1) }
    :return: num_files, files
    """
    raise NotImplementedError()


def file_gtm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    GIMP Table Magic

    Allows you to draw an HTML table in GIMP. See help for more info.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_gz_load(filename: str, raw_filename: str) -> Image:
    """
    loads files compressed with gzip

    This procedure loads files in the gzip compressed format.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_gz_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    saves files compressed with gzip

    This procedure saves files in the gzip compressed format.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_header_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    saves files as C unsigned character array

    FIXME: write help

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_ico_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files of Windows ICO file format

    Loads files of Windows ICO file format

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_ico_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Loads a preview from an Windows ICO file


    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_ico_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves files in Windows ICO file format

    Saves files in Windows ICO file format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_jp2_load(filename: str, raw_filename: str) -> Image:
    """
    Loads JPEG 2000 images.

    The JPEG 2000 image loader.

    :param filename: The name of the file to load.
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_jpeg_load(filename: str, raw_filename: str) -> Image:
    """
    loads files in the JPEG file format

    loads files in the JPEG file format

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_jpeg_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Loads a thumbnail from a JPEG image

    Loads a thumbnail from a JPEG image (only if it exists)

    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_jpeg_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, quality: float, smoothing: float, optimize: int, progressive: int, comment: str, subsmp: int, baseline: int, restart: int, dct: int):
    """
    saves files in the JPEG file format

    saves files in the lossy, widely supported JPEG format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param quality: Quality of saved image (0 <= quality <= 1)
    :param smoothing: Smoothing factor for saved image (0 <= smoothing <= 1)
    :param optimize: Use optimized tables during Huffman coding (0/1)
    :param progressive: Create progressive JPEG images (0/1)
    :param comment: Image comment
    :param subsmp: Sub-sampling type { 0, 1, 2, 3 } 0 == 4:2:0 (chroma quartered), 1 == 4:2:2 Horizontal (chroma halved), 2 == 4:4:4 (best quality), 3 == 4:2:2 Vertical (chroma halved)
    :param baseline: Force creation of a baseline JPEG (non-baseline JPEGs can't be read by all decoders) (0/1)
    :param restart: Interval of restart markers (in MCU rows, 0 = no restart markers)
    :param dct: DCT method to use { INTEGER (0), FIXED (1), FLOAT (2) }
    """
    raise NotImplementedError()


def file_mng_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, interlace: int, compression: int, quality: float, smoothing: float, loop: int, default_delay: int, default_chunks: int, default_dispose: int, bkgd: int, gama: int, phys: int, time: int):
    """
    Saves images in the MNG file format

    This plug-in saves images in the Multiple-image Network Graphics (MNG) format which can be used as a replacement for animated GIFs, and more.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param interlace: Use interlacing
    :param compression: PNG deflate compression level (0 - 9)
    :param quality: JPEG quality factor (0.00 - 1.00)
    :param smoothing: JPEG smoothing factor (0.00 - 1.00)
    :param loop: (ANIMATED MNG) Loop infinitely
    :param default_delay: (ANIMATED MNG) Default delay between frames in milliseconds
    :param default_chunks: (ANIMATED MNG) Default chunks type (0 = PNG + Delta PNG; 1 = JNG + Delta PNG; 2 = All PNG; 3 = All JNG)
    :param default_dispose: (ANIMATED MNG) Default dispose type (0 = combine; 1 = replace)
    :param bkgd: Write bKGD (background color) chunk
    :param gama: Write gAMA (gamma) chunk
    :param phys: Write pHYs (image resolution) chunk
    :param time: Write tIME (creation time) chunk
    """
    raise NotImplementedError()


def file_openraster_load(filename: str, raw_filename: str) -> Image:
    """
    load an OpenRaster (.ora) file

    load an OpenRaster (.ora) file

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_openraster_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    loads a thumbnail from an OpenRaster (.ora) file

    loads a thumbnail from an OpenRaster (.ora) file

    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_openraster_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    save an OpenRaster (.ora) file

    save an OpenRaster (.ora) file

    :param image: Input image
    :param drawable: Input drawable
    :param filename: The name of the file
    :param raw_filename: The name of the file
    """
    raise NotImplementedError()


def file_pat_load(filename: str, raw_filename: str) -> Image:
    """
    Loads Gimp's .PAT pattern files

    The images in the pattern dialog can be loaded directly with this plug-in

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_pat_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, description: str):
    """
    Saves Gimp pattern file (.PAT)

    New Gimp patterns can be created by saving them in the appropriate place with this plug-in.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param description: Short description of the pattern
    """
    raise NotImplementedError()


def file_pbm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, raw: int):
    """
    Saves files in the PBM file format

    PBM saving produces mono images without transparency.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param raw: Specify non-zero for raw output, zero for ascii output
    """
    raise NotImplementedError()


def file_pcx_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files in Zsoft PCX file format

    FIXME: write help for pcx_load

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_pcx_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves files in ZSoft PCX file format

    FIXME: write help for pcx_save

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_pdf_load(filename: str, raw_filename: str) -> Image:
    """
    Load file in PDF format

    Loads files in Adobe's Portable Document Format. PDF is designed to be easily processed by a variety of different platforms, and is a distant cousin of PostScript.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_pdf_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int, int, int]:
    """
    Loads a preview from a PDF file.

    Loads a small preview of the first page of the PDF format file. Uses the embedded thumbnail if present.

    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height, image_type, num_layers
    """
    raise NotImplementedError()


def file_pdf_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, vectorize: int, ignore_hidden: int, apply_masks: int):
    """
    Save files in PDF format

    Saves files in Adobe's Portable Document Format. PDF is designed to be easily processed by a variety of different platforms, and is a distant cousin of PostScript.

    :param image: Input image
    :param drawable: Input drawable
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param vectorize: Convert bitmaps to vector graphics where possible. TRUE or FALSE
    :param ignore_hidden: Omit hidden layers and layers with zero opacity. TRUE or FALSE
    :param apply_masks: Apply layer masks before saving. TRUE or FALSE (Keeping them will not change the output)
    """
    raise NotImplementedError()


def file_pdf_save_multi(images: List[int], count: int, vectorize: int, ignore_hidden: int, apply_masks: int, filename: str, raw_filename: str):
    """
    Save files in PDF format

    Saves files in Adobe's Portable Document Format. PDF is designed to be easily processed by a variety of different platforms, and is a distant cousin of PostScript.

    :param images: Input image for each page (An image can appear more than once)
    :param count: The amount of images entered (This will be the amount of pages). 1 <= count <= MAX_PAGE_COUNT
    :param vectorize: Convert bitmaps to vector graphics where possible. TRUE or FALSE
    :param ignore_hidden: Omit hidden layers and layers with zero opacity. TRUE or FALSE
    :param apply_masks: Apply layer masks before saving. TRUE or FALSE (Keeping them will not change the output)
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_pgm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, raw: int):
    """
    Saves files in the PGM file format

    PGM saving produces grayscale images without transparency.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param raw: Specify non-zero for raw output, zero for ascii output
    """
    raise NotImplementedError()


def file_pix_load(filename: str, raw_filename: str) -> Image:
    """
    loads files of the Alias|Wavefront Pix file format

    loads files of the Alias|Wavefront Pix file format

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_pix_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    save file in the Alias|Wavefront pix/matte file format

    save file in the Alias|Wavefront pix/matte file format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_png_get_defaults() -> Tuple[int, int, int, int, int, int, int, int, int]:
    """
    Get the current set of defaults used by the PNG file save plug-in

    This procedure returns the current set of defaults stored as a parasite for the PNG save plug-in. These defaults are used to seed the UI, by the file_png_save_defaults procedure, and by gimp_file_save when it detects to use PNG.
    :return: interlace, compression, bkgd, gama, offs, phys, time, comment, svtrans
    """
    raise NotImplementedError()


def file_png_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files in PNG file format

    This plug-in loads Portable Network Graphics (PNG) files.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_png_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, interlace: int, compression: int, bkgd: int, gama: int, offs: int, phys: int, time: int):
    """
    Saves files in PNG file format

    This plug-in saves Portable Network Graphics (PNG) files.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param interlace: Use Adam7 interlacing?
    :param compression: Deflate Compression factor (0--9)
    :param bkgd: Write bKGD chunk?
    :param gama: Write gAMA chunk?
    :param offs: Write oFFs chunk?
    :param phys: Write pHYs chunk?
    :param time: Write tIME chunk?
    """
    raise NotImplementedError()


def file_png_save_defaults(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves files in PNG file format

    This plug-in saves Portable Network Graphics (PNG) files, using the default settings stored as a parasite.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_png_save2(image: Image, drawable: Drawable, filename: str, raw_filename: str, interlace: int, compression: int, bkgd: int, gama: int, offs: int, phys: int, time: int, comment: int, svtrans: int):
    """
    Saves files in PNG file format

    This plug-in saves Portable Network Graphics (PNG) files. This procedure adds 2 extra parameters to file-png-save that allows to control whether image comments are saved and whether transparent pixels are saved or nullified.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param interlace: Use Adam7 interlacing?
    :param compression: Deflate Compression factor (0--9)
    :param bkgd: Write bKGD chunk?
    :param gama: Write gAMA chunk?
    :param offs: Write oFFs chunk?
    :param phys: Write pHYs chunk?
    :param time: Write tIME chunk?
    :param comment: Write comment?
    :param svtrans: Preserve color of transparent pixels?
    """
    raise NotImplementedError()


def file_png_set_defaults(interlace: int, compression: int, bkgd: int, gama: int, offs: int, phys: int, time: int, comment: int, svtrans: int):
    """
    Set the current set of defaults used by the PNG file save plug-in

    This procedure set the current set of defaults stored as a parasite for the PNG save plug-in. These defaults are used to seed the UI, by the file_png_save_defaults procedure, and by gimp_file_save when it detects to use PNG.

    :param interlace: Use Adam7 interlacing?
    :param compression: Deflate Compression factor (0--9)
    :param bkgd: Write bKGD chunk?
    :param gama: Write gAMA chunk?
    :param offs: Write oFFs chunk?
    :param phys: Write pHYs chunk?
    :param time: Write tIME chunk?
    :param comment: Write comment?
    :param svtrans: Preserve color of transparent pixels?
    """
    raise NotImplementedError()


def file_pnm_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files in the PNM file format

    This plug-in loads files in the various Netpbm portable file formats.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_pnm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, raw: int):
    """
    Saves files in the PNM file format

    PNM saving handles all image types without transparency.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param raw: Specify non-zero for raw output, zero for ascii output
    """
    raise NotImplementedError()


def file_ppm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, raw: int):
    """
    Saves files in the PPM file format

    PPM saving handles RGB images without transparency.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param raw: Specify non-zero for raw output, zero for ascii output
    """
    raise NotImplementedError()


def file_print_gtk(image: Image):
    """
    Print the image

    Print the image using the GTK+ Print API.

    :param image: Image to print
    """
    raise NotImplementedError()


def file_ps_load(filename: str, raw_filename: str) -> Image:
    """
    load PostScript documents

    load PostScript documents

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_ps_load_setargs(resolution: int, width: int, height: int, check_bbox: int, pages: str, coloring: int, text_alpha_bits: int, graphic_alpha_bits: int):
    """
    set additional parameters for procedure file-ps-load

    set additional parameters for procedure file-ps-load

    :param resolution: Resolution to interprete image (dpi)
    :param width: Desired width
    :param height: Desired height
    :param check_bbox: 0: Use width/height, 1: Use BoundingBox
    :param pages: Pages to load (e.g.: 1,3,5-7)
    :param coloring: 4: b/w, 5: grey, 6: colour image, 7: automatic
    :param text_alpha_bits: 1, 2, or 4
    :param graphic_alpha_bits: 1, 2, or 4
    """
    raise NotImplementedError()


def file_ps_load_thumb(filename: str, thumb_size: int) -> Image:
    """
    Loads a small preview from a PostScript or PDF document


    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image
    """
    raise NotImplementedError()


def file_ps_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, width: float, height: float, x_offset: float, y_offset: float, unit: int, keep_ratio: int, rotation: int, eps_flag: int, preview: int, level: int):
    """
    save image as PostScript docuement

    PostScript saving handles all image types except those with alpha channels.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param width: Width of the image in PostScript file (0: use input image size)
    :param height: Height of image in PostScript file (0: use input image size)
    :param x_offset: X-offset to image from lower left corner
    :param y_offset: Y-offset to image from lower left corner
    :param unit: Unit for width/height/offset. 0: inches, 1: millimeters
    :param keep_ratio: 0: use width/height, 1: keep aspect ratio
    :param rotation: 0, 90, 180, 270
    :param eps_flag: 0: PostScript, 1: Encapsulated PostScript
    :param preview: 0: no preview, >0: max. size of preview
    :param level: 1: PostScript Level 1, 2: PostScript Level 2
    """
    raise NotImplementedError()


def file_psd_load(filename: str, raw_filename: str) -> Image:
    """
    Loads images from the Photoshop PSD file format

    This plug-in loads images in Adobe Photoshop (TM) native PSD format.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_psd_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Loads thumbnails from the Photoshop PSD file format

    This plug-in loads thumnail images from Adobe Photoshop (TM) native PSD format files.

    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_psd_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, compression: int, fill_order: int):
    """
    saves files in the Photoshop(tm) PSD file format

    This filter saves files of Adobe Photoshop(tm) native PSD format.  These files may be of any image type supported by GIMP, with or without layers, layer masks, aux channels and guides.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param compression: Compression type: { NONE (0), LZW (1), PACKBITS (2)
    :param fill_order: Fill Order: { MSB to LSB (0), LSB to MSB (1)
    """
    raise NotImplementedError()


def file_psp_load(filename: str, raw_filename: str) -> Image:
    """
    loads images from the Paint Shop Pro PSP file format

    This plug-in loads and saves images in Paint Shop Pro's native PSP format. Vector layers aren't handled. Saving isn't yet implemented.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_raw_load(filename: str, raw_filename: str) -> Image:
    """
    Load raw images, specifying image information

    Load raw images, specifying image information

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_raw_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Dump images to disk in raw format

    Dump images to disk in raw format

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    """
    raise NotImplementedError()


def file_sgi_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files in SGI image file format

    This plug-in loads SGI image files.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_sgi_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, compression: int):
    """
    Saves files in SGI image file format

    This plug-in saves SGI image files.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param compression: Compression level (0 = none, 1 = RLE, 2 = ARLE)
    """
    raise NotImplementedError()


def file_sunras_load(filename: str, raw_filename: str) -> Image:
    """
    load file of the SunRaster file format

    load file of the SunRaster file format

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_sunras_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, rle: int):
    """
    save file in the SunRaster file format

    SUNRAS saving handles all image types except those with alpha channels.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param rle: Specify non-zero for rle output, zero for standard output
    """
    raise NotImplementedError()


def file_svg_load(filename: str, raw_filename: str, resolution: float, width: int, height: int, paths: int) -> Image:
    """
    Loads files in the SVG file format

    Renders SVG files to raster graphics using librsvg.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :param resolution: Resolution to use for rendering the SVG (defaults to 90 dpi)
    :param width: Width (in pixels) to load the SVG in. (0 for original width, a negative width to specify a maximum width)
    :param height: Height (in pixels) to load the SVG in. (0 for original height, a negative width to specify a maximum height)
    :param paths: Whether to not import paths (0), import paths individually (1) or merge all imported paths (2)
    :return: image
    """
    raise NotImplementedError()


def file_svg_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Generates a thumbnail of an SVG image

    Renders a thumbnail of an SVG file using librsvg.

    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_tga_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files of Targa file format

    FIXME: write help for tga_load

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_tga_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, rle: int, origin: int):
    """
    saves files in the Targa file format

    FIXME: write help for tga_save

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param rle: Use RLE compression
    :param origin: Image origin (0 = top-left, 1 = bottom-left)
    """
    raise NotImplementedError()


def file_tiff_load(filename: str, raw_filename: str) -> Image:
    """
    loads files of the tiff file format

    FIXME: write help for tiff_load

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_tiff_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, compression: int):
    """
    saves files in the tiff file format

    Saves files in the Tagged Image File Format.  The value for the saved comment is taken from the 'gimp-comment' parasite.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param compression: Compression type: { NONE (0), LZW (1), PACKBITS (2), DEFLATE (3), JPEG (4), CCITT G3 Fax (5), CCITT G4 Fax (6) }
    """
    raise NotImplementedError()


def file_tiff_save2(image: Image, drawable: Drawable, filename: str, raw_filename: str, compression: int, save_transp_pixels: int):
    """
    saves files in the tiff file format

    Saves files in the Tagged Image File Format.  The value for the saved comment is taken from the 'gimp-comment' parasite.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param compression: Compression type: { NONE (0), LZW (1), PACKBITS (2), DEFLATE (3), JPEG (4), CCITT G3 Fax (5), CCITT G4 Fax (6) }
    :param save_transp_pixels: Keep the color data masked by an alpha channel intact
    """
    raise NotImplementedError()


def file_uri_load(filename: str, raw_filename: str) -> Image:
    """
    loads files given an URI

    Loads a file using the GIO Virtual File System

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_uri_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    saves files given an URI

    Saves a file using the GIO Virtual File System

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def file_wmf_load(filename: str, raw_filename: str, resolution: float, width: int, height: int) -> Image:
    """
    Loads files in the WMF file format

    Loads files in the WMF file format

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :param resolution: Resolution to use for rendering the WMF (defaults to 72 dpi
    :param width: Width (in pixels) to load the WMF in, 0 for original width
    :param height: Height (in pixels) to load the WMF in, 0 for original height
    :return: image
    """
    raise NotImplementedError()


def file_wmf_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int]:
    """
    Loads a small preview from a WMF image


    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height
    """
    raise NotImplementedError()


def file_xbm_load(filename: str, raw_filename: str) -> Image:
    """
    Load a file in X10 or X11 bitmap (XBM) file format

    Load a file in X10 or X11 bitmap (XBM) file format.  XBM is a lossless format for flat black-and-white (two color indexed) images.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_xbm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, comment: str, x10: int, x_hot: int, y_hot: int, prefix: str, write_mask: int, mask_extension: str):
    """
    Save a file in X10 or X11 bitmap (XBM) file format

    Save a file in X10 or X11 bitmap (XBM) file format.  XBM is a lossless format for flat black-and-white (two color indexed) images.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save
    :param raw_filename: The name entered
    :param comment: Image description (maximum 72 bytes)
    :param x10: Save in X10 format
    :param x_hot: X coordinate of hotspot
    :param y_hot: Y coordinate of hotspot
    :param prefix: Identifier prefix [determined from filename]
    :param write_mask: (0 = ignore, 1 = save as extra file)
    :param mask_extension: Extension of the mask file
    """
    raise NotImplementedError()


def file_xjt_load(filename: str, raw_filename: str) -> Image:
    """
    loads files of the jpeg-tar file format

    loads files of the jpeg-tar file format

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_xmc_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files of X11 Mouse Cursor file format

    This plug-in loads X11 Mouse Cursor (XMC) files.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_xmc_load_thumb(filename: str, thumb_size: int) -> Tuple[Image, int, int, int, int]:
    """
    Loads only first frame of X11 Mouse Cursor's animation sequence which nominal size is the closest of thumb-size to be used as a thumbnail


    :param filename: The name of the file to load
    :param thumb_size: Preferred thumbnail size
    :return: image, image_width, image_height, image_type, image_num_layers
    """
    raise NotImplementedError()


def file_xmc_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, x_hot: int, y_hot: int, crop: int, size: int, size_replace: int, delay: int, delay_replace: int, copyright: str, license: str, other: str):
    """
    Saves files of X11 cursor file

    This plug-in saves X11 Mouse Cursor (XMC) files

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name entered
    :param x_hot: X-coordinate of hot spot
    :param y_hot: Y-coordinate of hot spot
    Use (-1, -1) to keep original hot spot.
    :param crop: Auto-crop or not
    :param size: Default nominal size
    :param size_replace: Replace existent size or not.
    :param delay: Default delay
    :param delay_replace: Replace existent delay or not.
    :param copyright: Copyright information.
    :param license: License information.
    :param other: Other comment.(taken from "gimp-comment" parasite)
    """
    raise NotImplementedError()


def file_xpm_load(filename: str, raw_filename: str) -> Image:
    """
    Load files in XPM (X11 Pixmap) format.

    Load files in XPM (X11 Pixmap) format. XPM is a portable image format designed to be included in C source code. XLib provides utility functions to read this format. Newer code should however be using gdk-pixbuf-csource instead. XPM supports colored images, unlike the XBM format which XPM was designed to replace.

    :param filename: The name of the file to load
    :param raw_filename: The name entered
    :return: image
    """
    raise NotImplementedError()


def file_xpm_save(image: Image, drawable: Drawable, filename: str, raw_filename: str, threshold: int):
    """
    Save files in XPM (X11 Pixmap) format.

    Save files in XPM (X11 Pixmap) format. XPM is a portable image format designed to be included in C source code. XLib provides utility functions to read this format. Newer code should however be using gdk-pixbuf-csource instead. XPM supports colored images, unlike the XBM format which XPM was designed to replace.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    :param threshold: Alpha threshold (0-255)
    """
    raise NotImplementedError()


def file_xwd_load(filename: str, raw_filename: str) -> Image:
    """
    Loads files in the XWD (X Window Dump) format

    Loads files in the XWD (X Window Dump) format. XWD image files are produced by the program xwd. Xwd is an X Window System window dumping utility.

    :param filename: The name of the file to load
    :param raw_filename: The name of the file to load
    :return: image
    """
    raise NotImplementedError()


def file_xwd_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves files in the XWD (X Window Dump) format

    XWD saving handles all image types except those with alpha channels.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name of the file to save the image in
    """
    raise NotImplementedError()


def gimp_airbrush(drawable: Drawable, pressure: float, num_strokes: int, strokes: List[float]):
    """
    Paint in the current brush with varying pressure. Paint application is time-dependent.

    This tool simulates the use of an airbrush. Paint pressure represents the relative intensity of the paint application. High pressure results in a thicker layer of paint while low pressure results in a thinner layer.

    :param drawable: The affected drawable
    :param pressure: The pressure of the airbrush strokes (0 <= pressure <= 100)
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_airbrush_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Paint in the current brush with varying pressure. Paint application is time-dependent.

    This tool simulates the use of an airbrush. It is similar to 'gimp-airbrush' except that the pressure is derived from the airbrush tools options box. It the option has not been set the default for the option will be used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_attach_parasite(parasite: Parasite):
    """
    Add a global parasite.

    This procedure attaches a global parasite. It has no return values.

    :param parasite: The parasite to attach
    """
    raise NotImplementedError()


def gimp_blend(drawable: Drawable, blend_mode: int, paint_mode: int, gradient_type: int, opacity: float, offset: float, repeat: int, reverse: int, supersample: int, max_depth: int, threshold: float, dither: int, x1: float, y1: float, x2: float, y2: float):
    """
    This procedure is deprecated! Use 'gimp-edit-blend' instead.

    This procedure is deprecated! Use 'gimp-edit-blend' instead.

    :param drawable: The affected drawable
    :param blend_mode: The type of blend { FG-BG-RGB-MODE (0), FG-BG-HSV-MODE (1), FG-TRANSPARENT-MODE (2), CUSTOM-MODE (3) }
    :param paint_mode: The paint application mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :param gradient_type: The type of gradient { GRADIENT-LINEAR (0), GRADIENT-BILINEAR (1), GRADIENT-RADIAL (2), GRADIENT-SQUARE (3), GRADIENT-CONICAL-SYMMETRIC (4), GRADIENT-CONICAL-ASYMMETRIC (5), GRADIENT-SHAPEBURST-ANGULAR (6), GRADIENT-SHAPEBURST-SPHERICAL (7), GRADIENT-SHAPEBURST-DIMPLED (8), GRADIENT-SPIRAL-CLOCKWISE (9), GRADIENT-SPIRAL-ANTICLOCKWISE (10) }
    :param opacity: The opacity of the final blend (0 <= opacity <= 100)
    :param offset: Offset relates to the starting and ending coordinates specified for the blend. This parameter is mode dependent. (offset >= 0)
    :param repeat: Repeat mode { REPEAT-NONE (0), REPEAT-SAWTOOTH (1), REPEAT-TRIANGULAR (2) }
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :param supersample: Do adaptive supersampling (TRUE or FALSE)
    :param max_depth: Maximum recursion levels for supersampling (1 <= max-depth <= 9)
    :param threshold: Supersampling threshold (0 <= threshold <= 4)
    :param dither: Use dithering to reduce banding (TRUE or FALSE)
    :param x1: The x coordinate of this blend's starting point
    :param y1: The y coordinate of this blend's starting point
    :param x2: The x coordinate of this blend's ending point
    :param y2: The y coordinate of this blend's ending point
    """
    raise NotImplementedError()


def gimp_brightness_contrast(drawable: Drawable, brightness: int, contrast: int):
    """
    Modify brightness/contrast in the specified drawable.

    This procedures allows the brightness and contrast of the specified drawable to be modified. Both 'brightness' and 'contrast' parameters are defined between -127 and 127.

    :param drawable: The drawable
    :param brightness: Brightness adjustment (-127 <= brightness <= 127)
    :param contrast: Contrast adjustment (-127 <= contrast <= 127)
    """
    raise NotImplementedError()


def gimp_brush_delete(name: str):
    """
    Deletes a brush

    This procedure deletes a brush

    :param name: The brush name
    """
    raise NotImplementedError()


def gimp_brush_duplicate(name: str) -> str:
    """
    Duplicates a brush

    This procedure creates an identical brush by a different name

    :param name: The brush name
    :return: copy_name
    """
    raise NotImplementedError()


def gimp_brush_get_angle(name: str) -> float:
    """
    Get the rotation angle of a generated brush.

    This procedure gets the angle of rotation for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :return: angle
    """
    raise NotImplementedError()


def gimp_brush_get_aspect_ratio(name: str) -> float:
    """
    Get the aspect ratio of a generated brush.

    This procedure gets the aspect ratio of a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :return: aspect_ratio
    """
    raise NotImplementedError()


def gimp_brush_get_hardness(name: str) -> float:
    """
    Get the hardness of a generated brush.

    This procedure gets the hardness of a generated brush. The hardness of a brush is the amount its intensity fades at the outside edge. If called for any other type of brush, the function does not succeed.

    :param name: The brush name
    :return: hardness
    """
    raise NotImplementedError()


def gimp_brush_get_info(name: str) -> Tuple[int, int, int, int]:
    """
    Retrieve information about the specified brush.

    This procedure retrieves information about the specified brush. This includes the brush name, and the brush extents (width and height).

    :param name: The brush name
    :return: width, height, mask_bpp, color_bpp
    """
    raise NotImplementedError()


def gimp_brush_get_pixels(name: str) -> Tuple[int, int, int, int, List[int], int, int, List[int]]:
    """
    Retrieve information about the specified brush.

    This procedure retrieves information about the specified brush. This includes the brush extents (width and height) and its pixels data.

    :param name: The brush name
    :return: width, height, mask_bpp, num_mask_bytes, mask_bytes, color_bpp, num_color_bytes, color_bytes
    """
    raise NotImplementedError()


def gimp_brush_get_radius(name: str) -> float:
    """
    Get the radius of a generated brush.

    This procedure gets the radius value for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :return: radius
    """
    raise NotImplementedError()


def gimp_brush_get_shape(name: str) -> int:
    """
    Get the shape of a generated brush.

    This procedure gets the shape value for a generated brush. If called for any other type of brush, it does not succeed. The current possibilities are Circle (GIMP_BRUSH_GENERATED_CIRCLE), Square (GIMP_BRUSH_GENERATED_SQUARE), and Diamond (GIMP_BRUSH_GENERATED_DIAMOND). Other shapes are likely to be added in the future.

    :param name: The brush name
    :return: shape
    """
    raise NotImplementedError()


def gimp_brush_get_spacing(name: str) -> int:
    """
    Get the brush spacing.

    This procedure returns the spacing setting for the specified brush. The return value is an integer between 0 and 1000 which represents percentage of the maximum of the width and height of the mask.

    :param name: The brush name
    :return: spacing
    """
    raise NotImplementedError()


def gimp_brush_get_spikes(name: str) -> int:
    """
    Get the number of spikes for a generated brush.

    This procedure gets the number of spikes for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :return: spikes
    """
    raise NotImplementedError()


def gimp_brush_is_editable(name: str) -> int:
    """
    Tests if brush can be edited

    Returns TRUE if you have permission to change the brush

    :param name: The brush name
    :return: editable
    """
    raise NotImplementedError()


def gimp_brush_is_generated(name: str) -> int:
    """
    Tests if brush is generated

    Returns TRUE if this brush is parametric, FALSE for other types

    :param name: The brush name
    :return: generated
    """
    raise NotImplementedError()


def gimp_brush_new(name: str) -> str:
    """
    Creates a new brush

    This procedure creates a new, uninitialized brush

    :param name: The requested name of the new brush
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_brush_rename(name: str, new_name: str) -> str:
    """
    Rename a brush

    This procedure renames a brush

    :param name: The brush name
    :param new_name: The new name of the brush
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_brush_set_angle(name: str, angle_in: float) -> float:
    """
    Set the rotation angle of a generated brush.

    This procedure sets the rotation angle for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :param angle_in: The desired brush rotation angle
    :return: angle_out
    """
    raise NotImplementedError()


def gimp_brush_set_aspect_ratio(name: str, aspect_ratio_in: float) -> float:
    """
    Set the aspect ratio of a generated brush.

    This procedure sets the aspect ratio for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :param aspect_ratio_in: The desired brush aspect ratio
    :return: aspect_ratio_out
    """
    raise NotImplementedError()


def gimp_brush_set_hardness(name: str, hardness_in: float) -> float:
    """
    Set the hardness of a generated brush.

    This procedure sets the hardness for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :param hardness_in: The desired brush hardness
    :return: hardness_out
    """
    raise NotImplementedError()


def gimp_brush_set_radius(name: str, radius_in: float) -> float:
    """
    Set the radius of a generated brush.

    This procedure sets the radius for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :param radius_in: The desired brush radius
    :return: radius_out
    """
    raise NotImplementedError()


def gimp_brush_set_shape(name: str, shape_in: int) -> int:
    """
    Set the shape of a generated brush.

    This procedure sets the shape value for a generated brush. If called for any other type of brush, it does not succeed. The current possibilities are Circle (GIMP_BRUSH_GENERATED_CIRCLE), Square (GIMP_BRUSH_GENERATED_SQUARE), and Diamond (GIMP_BRUSH_GENERATED_DIAMOND). Other shapes are likely to be added in the future.

    :param name: The brush name
    :param shape_in: The brush shape { BRUSH-GENERATED-CIRCLE (0), BRUSH-GENERATED-SQUARE (1), BRUSH-GENERATED-DIAMOND (2) }
    :return: shape_out
    """
    raise NotImplementedError()


def gimp_brush_set_spacing(name: str, spacing: int):
    """
    Set the brush spacing.

    This procedure modifies the spacing setting for the specified brush. The value should be a integer between 0 and 1000.

    :param name: The brush name
    :param spacing: The brush spacing (0 <= spacing <= 1000)
    """
    raise NotImplementedError()


def gimp_brush_set_spikes(name: str, spikes_in: int) -> int:
    """
    Set the number of spikes for a generated brush.

    This procedure sets the number of spikes for a generated brush. If called for any other type of brush, it does not succeed.

    :param name: The brush name
    :param spikes_in: The desired number of spikes
    :return: spikes_out
    """
    raise NotImplementedError()


def gimp_brushes_close_popup(brush_callback: str):
    """
    Close the brush selection dialog.

    This procedure closes an opened brush selection dialog.

    :param brush_callback: The name of the callback registered for this pop-up
    """
    raise NotImplementedError()


def gimp_brushes_get_brush() -> Tuple[str, int, int, int]:
    """
    Deprecated: Use 'gimp-context-get-brush' instead.

    Deprecated: Use 'gimp-context-get-brush' instead.
    :return: name, width, height, spacing
    """
    raise NotImplementedError()


def gimp_brushes_get_brush_data(name: str) -> Tuple[str, float, int, int, int, int, int, List[int]]:
    """
    Deprecated: Use 'gimp-brush-get-pixels' instead.

    Deprecated: Use 'gimp-brush-get-pixels' instead.

    :param name: The brush name ("" means current active brush)
    :return: actual_name, opacity, spacing, paint_mode, width, height, length, mask_data
    """
    raise NotImplementedError()


def gimp_brushes_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve a complete listing of the available brushes.

    This procedure returns a complete listing of available GIMP brushes. Each name returned can be used as input to the 'gimp-context-set-brush' procedure.

    :param filter: An optional regular expression used to filter the list
    :return: num_brushes, brush_list
    """
    raise NotImplementedError()


def gimp_brushes_get_opacity() -> float:
    """
    This procedure is deprecated! Use 'gimp-context-get-opacity' instead.

    This procedure is deprecated! Use 'gimp-context-get-opacity' instead.
    :return: opacity
    """
    raise NotImplementedError()


def gimp_brushes_get_paint_mode() -> int:
    """
    This procedure is deprecated! Use 'gimp-context-get-paint-mode' instead.

    This procedure is deprecated! Use 'gimp-context-get-paint-mode' instead.
    :return: paint_mode
    """
    raise NotImplementedError()


def gimp_brushes_get_spacing() -> int:
    """
    Deprecated: Use 'gimp-brush-get-spacing' instead.

    Deprecated: Use 'gimp-brush-get-spacing' instead.
    :return: spacing
    """
    raise NotImplementedError()


def gimp_brushes_list(filter: str) -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-brushes-get-list' instead.

    This procedure is deprecated! Use 'gimp-brushes-get-list' instead.

    :param filter: An optional regular expression used to filter the list
    :return: num_brushes, brush_list
    """
    raise NotImplementedError()


def gimp_brushes_popup(brush_callback: str, popup_title: str, initial_brush: str, opacity: float, spacing: int, paint_mode: int):
    """
    Invokes the Gimp brush selection.

    This procedure opens the brush selection dialog.

    :param brush_callback: The callback PDB proc to call when brush selection is made
    :param popup_title: Title of the brush selection dialog
    :param initial_brush: The name of the brush to set as the first selected
    :param opacity: The initial opacity of the brush (0 <= opacity <= 100)
    :param spacing: The initial spacing of the brush (if < 0 then use brush default spacing) (spacing <= 1000)
    :param paint_mode: The initial paint mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    """
    raise NotImplementedError()


def gimp_brushes_refresh():
    """
    Refresh current brushes. This function always succeeds.

    This procedure retrieves all brushes currently in the user's brush path and updates the brush dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_brushes_set_brush(name: str):
    """
    This procedure is deprecated! Use 'gimp-context-set-brush' instead.

    This procedure is deprecated! Use 'gimp-context-set-brush' instead.

    :param name: The name of the brush
    """
    raise NotImplementedError()


def gimp_brushes_set_opacity(opacity: float):
    """
    This procedure is deprecated! Use 'gimp-context-set-opacity' instead.

    This procedure is deprecated! Use 'gimp-context-set-opacity' instead.

    :param opacity: The opacity (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_brushes_set_paint_mode(paint_mode: int):
    """
    This procedure is deprecated! Use 'gimp-context-set-paint-mode' instead.

    This procedure is deprecated! Use 'gimp-context-set-paint-mode' instead.

    :param paint_mode: The paint mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    """
    raise NotImplementedError()


def gimp_brushes_set_popup(brush_callback: str, brush_name: str, opacity: float, spacing: int, paint_mode: int):
    """
    Sets the current brush in a brush selection dialog.

    Sets the current brush in a brush selection dialog.

    :param brush_callback: The name of the callback registered for this pop-up
    :param brush_name: The name of the brush to set as selected
    :param opacity: The initial opacity of the brush (0 <= opacity <= 100)
    :param spacing: The initial spacing of the brush (if < 0 then use brush default spacing) (spacing <= 1000)
    :param paint_mode: The initial paint mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    """
    raise NotImplementedError()


def gimp_brushes_set_spacing(spacing: int):
    """
    Deprecated: Use 'gimp-brush-set-spacing' instead.

    Deprecated: Use 'gimp-brush-set-spacing' instead.

    :param spacing: The brush spacing (0 <= spacing <= 1000)
    """
    raise NotImplementedError()


def gimp_bucket_fill(drawable: Drawable, fill_mode: int, paint_mode: int, opacity: float, threshold: float, sample_merged: int, x: float, y: float):
    """
    This procedure is deprecated! Use 'gimp-edit-bucket-fill' instead.

    This procedure is deprecated! Use 'gimp-edit-bucket-fill' instead.

    :param drawable: The affected drawable
    :param fill_mode: The type of fill { FG-BUCKET-FILL (0), BG-BUCKET-FILL (1), PATTERN-BUCKET-FILL (2) }
    :param paint_mode: The paint application mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :param opacity: The opacity of the final bucket fill (0 <= opacity <= 100)
    :param threshold: The threshold determines how extensive the seed fill will be. It's value is specified in terms of intensity levels. This parameter is only valid when there is no selection in the specified image. (0 <= threshold <= 255)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param x: The x coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    :param y: The y coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    """
    raise NotImplementedError()


def gimp_buffer_delete(buffer_name: str):
    """
    Deletes a named buffer.

    This procedure deletes a named buffer.

    :param buffer_name: The buffer name
    """
    raise NotImplementedError()


def gimp_buffer_get_bytes(buffer_name: str) -> int:
    """
    Retrieves the specified buffer's bytes.

    This procedure retrieves the specified named buffer's bytes.

    :param buffer_name: The buffer name
    :return: bytes
    """
    raise NotImplementedError()


def gimp_buffer_get_height(buffer_name: str) -> int:
    """
    Retrieves the specified buffer's height.

    This procedure retrieves the specified named buffer's height.

    :param buffer_name: The buffer name
    :return: height
    """
    raise NotImplementedError()


def gimp_buffer_get_image_type(buffer_name: str) -> int:
    """
    Retrieves the specified buffer's image type.

    This procedure retrieves the specified named buffer's image type.

    :param buffer_name: The buffer name
    :return: image_type
    """
    raise NotImplementedError()


def gimp_buffer_get_width(buffer_name: str) -> int:
    """
    Retrieves the specified buffer's width.

    This procedure retrieves the specified named buffer's width.

    :param buffer_name: The buffer name
    :return: width
    """
    raise NotImplementedError()


def gimp_buffer_rename(buffer_name: str, new_name: str) -> str:
    """
    Renames a named buffer.

    This procedure renames a named buffer.

    :param buffer_name: The buffer name
    :param new_name: The buffer's new name
    :return: real_name
    """
    raise NotImplementedError()


def gimp_buffers_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve a complete listing of the available buffers.

    This procedure returns a complete listing of available named buffers.

    :param filter: An optional regular expression used to filter the list
    :return: num_buffers, buffer_list
    """
    raise NotImplementedError()


def gimp_by_color_select(drawable: Drawable, color: Color, threshold: int, operation: int, antialias: int, feather: int, feather_radius: float, sample_merged: int):
    """
    Deprecated: Use 'gimp-image-select-color' instead.

    Deprecated: Use 'gimp-image-select-color' instead.

    :param drawable: The affected drawable
    :param color: The color to select
    :param threshold: Threshold in intensity levels (0 <= threshold <= 255)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius: Radius for feather operation (feather-radius >= 0)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_by_color_select_full(drawable: Drawable, color: Color, threshold: int, operation: int, antialias: int, feather: int, feather_radius_x: float, feather_radius_y: float, sample_merged: int, select_transparent: int, select_criterion: int):
    """
    Deprecated: Use 'gimp-image-select-color' instead.

    Deprecated: Use 'gimp-image-select-color' instead.

    :param drawable: The affected drawable
    :param color: The color to select
    :param threshold: Threshold in intensity levels (0 <= threshold <= 255)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius_x: Radius for feather operation in X direction (feather-radius-x >= 0)
    :param feather_radius_y: Radius for feather operation in Y direction (feather-radius-y >= 0)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param select_transparent: Whether to consider transparent pixels for selection. If TRUE, transparency is considered as a unique selectable color. (TRUE or FALSE)
    :param select_criterion: The criterion used to determine color similarity. SELECT_CRITERION_COMPOSITE is the standard choice. { SELECT-CRITERION-COMPOSITE (0), SELECT-CRITERION-R (1), SELECT-CRITERION-G (2), SELECT-CRITERION-B (3), SELECT-CRITERION-H (4), SELECT-CRITERION-S (5), SELECT-CRITERION-V (6) }
    """
    raise NotImplementedError()


def gimp_channel_combine_masks(channel1: Channel, channel2: Channel, operation: int, offx: int, offy: int):
    """
    Combine two channel masks.

    This procedure combines two channel masks. The result is stored in the first channel.

    :param channel1: The channel1
    :param channel2: The channel2
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param offx: x offset between upper left corner of channels: (second - first)
    :param offy: y offset between upper left corner of channels: (second - first)
    """
    raise NotImplementedError()


def gimp_channel_copy(channel: Channel) -> Channel:
    """
    Copy a channel.

    This procedure copies the specified channel and returns the copy.

    :param channel: The channel to copy
    :return: channel_copy
    """
    raise NotImplementedError()


def gimp_channel_delete(item: Item):
    """
    This procedure is deprecated! Use 'gimp-item-delete' instead.

    This procedure is deprecated! Use 'gimp-item-delete' instead.

    :param item: The item to delete
    """
    raise NotImplementedError()


def gimp_channel_get_color(channel: Channel) -> Color:
    """
    Get the compositing color of the specified channel.

    This procedure returns the specified channel's compositing color.

    :param channel: The channel
    :return: color
    """
    raise NotImplementedError()


def gimp_channel_get_name(item: Item) -> str:
    """
    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    :param item: The item
    :return: name
    """
    raise NotImplementedError()


def gimp_channel_get_opacity(channel: Channel) -> float:
    """
    Get the opacity of the specified channel.

    This procedure returns the specified channel's opacity.

    :param channel: The channel
    :return: opacity
    """
    raise NotImplementedError()


def gimp_channel_get_show_masked(channel: Channel) -> int:
    """
    Get the composite method of the specified channel.

    This procedure returns the specified channel's composite method. If it is TRUE, then the channel is composited with the image so that masked regions are shown. Otherwise, selected regions are shown.

    :param channel: The channel
    :return: show_masked
    """
    raise NotImplementedError()


def gimp_channel_get_tattoo(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    :param item: The item
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_channel_get_visible(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    :param item: The item
    :return: visible
    """
    raise NotImplementedError()


def gimp_channel_new(image: Image, width: int, height: int, name: str, opacity: float, color: Color) -> Channel:
    """
    Create a new channel.

    This procedure creates a new channel with the specified width and height. Name, opacity, and color are also supplied parameters. The new channel still needs to be added to the image, as this is not automatic. Add the new channel with the 'gimp-image-insert-channel' command. Other attributes such as channel show masked, should be set with explicit procedure calls. The channel's contents are undefined initially.

    :param image: The image to which to add the channel
    :param width: The channel width (1 <= width <= 262144)
    :param height: The channel height (1 <= height <= 262144)
    :param name: The channel name
    :param opacity: The channel opacity (0 <= opacity <= 100)
    :param color: The channel compositing color
    :return: channel
    """
    raise NotImplementedError()


def gimp_channel_new_from_component(image: Image, component: int, name: str) -> Channel:
    """
    Create a new channel from a color component

    This procedure creates a new channel from a color component.

    :param image: The image to which to add the channel
    :param component: The image component { RED-CHANNEL (0), GREEN-CHANNEL (1), BLUE-CHANNEL (2), GRAY-CHANNEL (3), INDEXED-CHANNEL (4), ALPHA-CHANNEL (5) }
    :param name: The channel name
    :return: channel
    """
    raise NotImplementedError()


def gimp_channel_ops_duplicate(image: Image) -> Image:
    """
    This procedure is deprecated! Use 'gimp-image-duplicate' instead.

    This procedure is deprecated! Use 'gimp-image-duplicate' instead.

    :param image: The image
    :return: new_image
    """
    raise NotImplementedError()


def gimp_channel_ops_offset(drawable: Drawable, wrap_around: int, fill_type: int, offset_x: int, offset_y: int):
    """
    This procedure is deprecated! Use 'gimp-drawable-offset' instead.

    This procedure is deprecated! Use 'gimp-drawable-offset' instead.

    :param drawable: The drawable to offset
    :param wrap_around: wrap image around or fill vacated regions (TRUE or FALSE)
    :param fill_type: fill vacated regions of drawable with background or transparent { OFFSET-BACKGROUND (0), OFFSET-TRANSPARENT (1) }
    :param offset_x: offset by this amount in X direction
    :param offset_y: offset by this amount in Y direction
    """
    raise NotImplementedError()


def gimp_channel_set_color(channel: Channel, color: Color):
    """
    Set the compositing color of the specified channel.

    This procedure sets the specified channel's compositing color.

    :param channel: The channel
    :param color: The new channel compositing color
    """
    raise NotImplementedError()


def gimp_channel_set_name(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    :param item: The item
    :param name: The new item name
    """
    raise NotImplementedError()


def gimp_channel_set_opacity(channel: Channel, opacity: float):
    """
    Set the opacity of the specified channel.

    This procedure sets the specified channel's opacity.

    :param channel: The channel
    :param opacity: The new channel opacity (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_channel_set_show_masked(channel: Channel, show_masked: int):
    """
    Set the composite method of the specified channel.

    This procedure sets the specified channel's composite method. If it is TRUE, then the channel is composited with the image so that masked regions are shown. Otherwise, selected regions are shown.

    :param channel: The channel
    :param show_masked: The new channel composite method (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_channel_set_tattoo(item: Item, tattoo: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    :param item: The item
    :param tattoo: The new item tattoo
    """
    raise NotImplementedError()


def gimp_channel_set_visible(item: Item, visible: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    :param item: The item
    :param visible: The new item visibility (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_clone(drawable: Drawable, src_drawable: Drawable, clone_type: int, src_x: float, src_y: float, num_strokes: int, strokes: List[float]):
    """
    Clone from the source to the dest drawable using the current brush

    This tool clones (copies) from the source drawable starting at the specified source coordinates to the dest drawable. If the "clone_type" argument is set to PATTERN-CLONE, then the current pattern is used as the source and the "src_drawable" argument is ignored. Pattern cloning assumes a tileable pattern and mods the sum of the src coordinates and subsequent stroke offsets with the width and height of the pattern. For image cloning, if the sum of the src coordinates and subsequent stroke offsets exceeds the extents of the src drawable, then no paint is transferred. The clone tool is capable of transforming between any image types including RGB->Indexed--although converting from any type to indexed is significantly slower.

    :param drawable: The affected drawable
    :param src_drawable: The source drawable
    :param clone_type: The type of clone { IMAGE-CLONE (0), PATTERN-CLONE (1) }
    :param src_x: The x coordinate in the source image
    :param src_y: The y coordinate in the source image
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_clone_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Clone from the source to the dest drawable using the current brush

    This tool clones (copies) from the source drawable starting at the specified source coordinates to the dest drawable. This function performs exactly the same as the 'gimp-clone' function except that the tools arguments are obtained from the clones option dialog. It this dialog has not been activated then the dialogs default values will be used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_color_balance(drawable: Drawable, transfer_mode: int, preserve_lum: int, cyan_red: float, magenta_green: float, yellow_blue: float):
    """
    Modify the color balance of the specified drawable.

    Modify the color balance of the specified drawable. There are three axis which can be modified: cyan-red, magenta-green, and yellow-blue. Negative values increase the amount of the former, positive values increase the amount of the latter. Color balance can be controlled with the 'transfer_mode' setting, which allows shadows, mid-tones, and highlights in an image to be affected differently. The 'preserve-lum' parameter, if TRUE, ensures that the luminosity of each pixel remains fixed.

    :param drawable: The drawable
    :param transfer_mode: Transfer mode { SHADOWS (0), MIDTONES (1), HIGHLIGHTS (2) }
    :param preserve_lum: Preserve luminosity values at each pixel (TRUE or FALSE)
    :param cyan_red: Cyan-Red color balance (-100 <= cyan-red <= 100)
    :param magenta_green: Magenta-Green color balance (-100 <= magenta-green <= 100)
    :param yellow_blue: Yellow-Blue color balance (-100 <= yellow-blue <= 100)
    """
    raise NotImplementedError()


def gimp_color_picker(image: Image, drawable: Drawable, x: float, y: float, sample_merged: int, sample_average: int, average_radius: float) -> Color:
    """
    This procedure is deprecated! Use 'gimp-image-pick-color' instead.

    This procedure is deprecated! Use 'gimp-image-pick-color' instead.

    :param image: The image
    :param drawable: The drawable to pick from
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param sample_average: Average the color of all the pixels in a specified radius (TRUE or FALSE)
    :param average_radius: The radius of pixels to average (average-radius >= 0)
    :return: color
    """
    raise NotImplementedError()


def gimp_colorize(drawable: Drawable, hue: float, saturation: float, lightness: float):
    """
    Render the drawable as a grayscale image seen through a colored glass.

    Desaturates the drawable, then tints it with the specified color. This tool is only valid on RGB color images. It will not operate on grayscale or indexed drawables.

    :param drawable: The drawable
    :param hue: Hue in degrees (0 <= hue <= 360)
    :param saturation: Saturation in percent (0 <= saturation <= 100)
    :param lightness: Lightness in percent (-100 <= lightness <= 100)
    """
    raise NotImplementedError()


def gimp_context_get_antialias() -> int:
    """
    Get the antialias setting.

    This procedure returns the antialias setting.
    :return: antialias
    """
    raise NotImplementedError()


def gimp_context_get_background() -> Color:
    """
    Get the current GIMP background color.

    This procedure returns the current GIMP background color. The background color is used in a variety of tools such as blending, erasing (with non-alpha images), and image filling.
    :return: background
    """
    raise NotImplementedError()


def gimp_context_get_brush() -> str:
    """
    Retrieve the currently active brush.

    This procedure returns the name of the currently active brush. All paint operations and stroke operations use this brush to control the application of paint to the image.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_brush_angle() -> float:
    """
    Get brush angle in degrees.

    Set the angle in degrees for brush based paint tools.
    :return: angle
    """
    raise NotImplementedError()


def gimp_context_get_brush_aspect_ratio() -> float:
    """
    Get brush aspect ratio.

    Set the aspect ratio for brush based paint tools.
    :return: aspect
    """
    raise NotImplementedError()


def gimp_context_get_brush_size() -> float:
    """
    Get brush size in pixels.

    Get the brush size in pixels for brush based paint tools.
    :return: size
    """
    raise NotImplementedError()


def gimp_context_get_dynamics() -> str:
    """
    Retrieve the currently active paint dynamics.

    This procedure returns the name of the currently active paint dynamics. All paint operations and stroke operations use this paint dynamics to control the application of paint to the image.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_feather() -> int:
    """
    Get the feather setting.

    This procedure returns the feather setting.
    :return: feather
    """
    raise NotImplementedError()


def gimp_context_get_feather_radius() -> Tuple[float, float]:
    """
    Get the feather radius setting.

    This procedure returns the feather radius setting.
    :return: feather_radius_x, feather_radius_y
    """
    raise NotImplementedError()


def gimp_context_get_font() -> str:
    """
    Retrieve the currently active font.

    This procedure returns the name of the currently active font.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_foreground() -> Color:
    """
    Get the current GIMP foreground color.

    This procedure returns the current GIMP foreground color. The foreground color is used in a variety of tools such as paint tools, blending, and bucket fill.
    :return: foreground
    """
    raise NotImplementedError()


def gimp_context_get_gradient() -> str:
    """
    Retrieve the currently active gradient.

    This procedure returns the name of the currently active gradient.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_ink_angle() -> float:
    """
    Get ink angle in degrees.

    Get the ink angle in degrees for ink tool.
    :return: angle
    """
    raise NotImplementedError()


def gimp_context_get_ink_blob_angle() -> float:
    """
    Get ink blob angle in degrees.

    Get the ink blob angle in degrees for ink tool.
    :return: angle
    """
    raise NotImplementedError()


def gimp_context_get_ink_blob_aspect_ratio() -> float:
    """
    Get ink blob aspect ratio.

    Get the ink blob aspect ratio for ink tool.
    :return: aspect
    """
    raise NotImplementedError()


def gimp_context_get_ink_blob_type() -> int:
    """
    Get ink blob type.

    Get the ink blob type for ink tool.
    :return: type
    """
    raise NotImplementedError()


def gimp_context_get_ink_size() -> float:
    """
    Get ink blob size in pixels.

    Get the ink blob size in pixels for ink tool.
    :return: size
    """
    raise NotImplementedError()


def gimp_context_get_ink_size_sensitivity() -> float:
    """
    Get ink size sensitivity.

    Get the ink size sensitivity for ink tool.
    :return: size
    """
    raise NotImplementedError()


def gimp_context_get_ink_speed_sensitivity() -> float:
    """
    Get ink speed sensitivity.

    Get the ink speed sensitivity for ink tool.
    :return: speed
    """
    raise NotImplementedError()


def gimp_context_get_ink_tilt_sensitivity() -> float:
    """
    Get ink tilt sensitivity.

    Get the ink tilt sensitivity for ink tool.
    :return: tilt
    """
    raise NotImplementedError()


def gimp_context_get_interpolation() -> int:
    """
    Get the interpolation type.

    This procedure returns the interpolation setting. The return value is an integer which corresponds to the values listed in the argument description. If the interpolation has not been set explicitly by 'gimp-context-set-interpolation', the default interpolation set in gimprc will be used.
    :return: interpolation
    """
    raise NotImplementedError()


def gimp_context_get_opacity() -> float:
    """
    Get the opacity.

    This procedure returns the opacity setting. The return value is a floating point number between 0 and 100.
    :return: opacity
    """
    raise NotImplementedError()


def gimp_context_get_paint_method() -> str:
    """
    Retrieve the currently active paint method.

    This procedure returns the name of the currently active paint method.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_paint_mode() -> int:
    """
    Get the paint mode.

    This procedure returns the paint-mode setting. The return value is an integer which corresponds to the values listed in the argument description.
    :return: paint_mode
    """
    raise NotImplementedError()


def gimp_context_get_palette() -> str:
    """
    Retrieve the currently active palette.

    This procedure returns the name of the the currently active palette.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_pattern() -> str:
    """
    Retrieve the currently active pattern.

    This procedure returns name of the the currently active pattern. All clone and bucket-fill operations with patterns will use this pattern to control the application of paint to the image.
    :return: name
    """
    raise NotImplementedError()


def gimp_context_get_sample_criterion() -> int:
    """
    Get the sample criterion setting.

    This procedure returns the sample criterion setting.
    :return: sample_criterion
    """
    raise NotImplementedError()


def gimp_context_get_sample_merged() -> int:
    """
    Get the sample merged setting.

    This procedure returns the sample merged setting.
    :return: sample_merged
    """
    raise NotImplementedError()


def gimp_context_get_sample_threshold() -> float:
    """
    Get the sample threshold setting.

    This procedure returns the sample threshold setting.
    :return: sample_threshold
    """
    raise NotImplementedError()


def gimp_context_get_sample_threshold_int() -> int:
    """
    Get the sample threshold setting as an integer value.

    This procedure returns the sample threshold setting as an integer value. See 'gimp-context-get-sample-threshold'.
    :return: sample_threshold
    """
    raise NotImplementedError()


def gimp_context_get_sample_transparent() -> int:
    """
    Get the sample transparent setting.

    This procedure returns the sample transparent setting.
    :return: sample_transparent
    """
    raise NotImplementedError()


def gimp_context_get_transform_direction() -> int:
    """
    Get the transform direction.

    This procedure returns the transform direction. The return value is an integer which corresponds to the values listed in the argument description.
    :return: transform_direction
    """
    raise NotImplementedError()


def gimp_context_get_transform_recursion() -> int:
    """
    Get the transform supersampling recursion.

    This procedure returns the transform supersampling recursion level.
    :return: transform_recursion
    """
    raise NotImplementedError()


def gimp_context_get_transform_resize() -> int:
    """
    Get the transform resize type.

    This procedure returns the transform resize setting. The return value is an integer which corresponds to the values listed in the argument description.
    :return: transform_resize
    """
    raise NotImplementedError()


def gimp_context_list_paint_methods() -> Tuple[int, List[str]]:
    """
    Lists the available paint methods.

    This procedure lists the names of the available paint methods. Any of the results can be used for 'gimp-context-set-paint-method'.
    :return: num_paint_methods, paint_methods
    """
    raise NotImplementedError()


def gimp_context_pop():
    """
    Pops the topmost context from the plug-in's context stack.

    This procedure removes the topmost context from the plug-in's context stack. The context that was active before the corresponding call to 'gimp-context-push' becomes the new current context of the plug-in.
    """
    raise NotImplementedError()


def gimp_context_push():
    """
    Pushes a context to the top of the plug-in's context stack.

    This procedure creates a new context by copying the current context. This copy becomes the new current context for the calling plug-in until it is popped again using 'gimp-context-pop'.
    """
    raise NotImplementedError()


def gimp_context_set_antialias(antialias: int):
    """
    Set the antialias setting.

    This procedure modifies the antialias setting. If antialiasing is turned on, the edges of selected region will contain intermediate values which give the appearance of a sharper, less pixelized edge. This should be set as TRUE most of the time unless a binary-only selection is wanted. This settings affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color', 'gimp-image-select-round-rectangle', 'gimp-image-select-ellipse', 'gimp-image-select-polygon', 'gimp-image-select-item'.

    :param antialias: The antialias setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_context_set_background(background: Color):
    """
    Set the current GIMP background color.

    This procedure sets the current GIMP background color. After this is set, operations which use background such as blending, filling images, clearing, and erasing (in non-alpha images) will use the new value.

    :param background: The background color
    """
    raise NotImplementedError()


def gimp_context_set_brush(name: str):
    """
    Set the specified brush as the active brush.

    This procedure allows the active brush to be set by specifying its name. The name is simply a string which corresponds to one of the names of the installed brushes. If there is no matching brush found, this procedure will return an error. Otherwise, the specified brush becomes active and will be used in all subsequent paint operations.

    :param name: The name of the brush
    """
    raise NotImplementedError()


def gimp_context_set_brush_angle(angle: float):
    """
    Set brush angle in degrees.

    Set the angle in degrees for brush based paint tools.

    :param angle: angle in degrees (-180 <= angle <= 180)
    """
    raise NotImplementedError()


def gimp_context_set_brush_aspect_ratio(aspect: float):
    """
    Set brush aspect ratio.

    Set the aspect ratio for brush based paint tools.

    :param aspect: aspect ratio (-20 <= aspect <= 20)
    """
    raise NotImplementedError()


def gimp_context_set_brush_default_size():
    """
    Set brush size to its default.

    Set the brush size to the default (max of width and height) for paintbrush, airbrush, or pencil tools.
    """
    raise NotImplementedError()


def gimp_context_set_brush_size(size: float):
    """
    Set brush size in pixels.

    Set the brush size in pixels for brush based paint tools.

    :param size: brush size in pixels (size >= 0)
    """
    raise NotImplementedError()


def gimp_context_set_default_colors():
    """
    Set the current GIMP foreground and background colors to black and white.

    This procedure sets the current GIMP foreground and background colors to their initial default values, black and white.
    """
    raise NotImplementedError()


def gimp_context_set_defaults():
    """
    Reset context settings to their default values.

    This procedure resets context settings used by various procedures to their default value. This procedure will usually be called after a context push so that a script which calls procedures affected by context settings will not be affected by changes in the global context.
    """
    raise NotImplementedError()


def gimp_context_set_dynamics(name: str):
    """
    Set the specified paint dynamics as the active paint dynamics.

    This procedure allows the active paint dynamics to be set by specifying its name. The name is simply a string which corresponds to one of the names of the installed paint dynamics. If there is no matching paint dynamics found, this procedure will return an error. Otherwise, the specified paint dynamics becomes active and will be used in all subsequent paint operations.

    :param name: The name of the paint dynamics
    """
    raise NotImplementedError()


def gimp_context_set_feather(feather: int):
    """
    Set the feather setting.

    This procedure modifies the feather setting. If the feather option is enabled, selections will be blurred before combining. The blur is a gaussian blur; its radii can be controlled using 'gimp-context-set-feather-radius'. This setting affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color', 'gimp-image-select-rectangle', 'gimp-image-select-round-rectangle', 'gimp-image-select-ellipse', 'gimp-image-select-polygon', 'gimp-image-select-item'.

    :param feather: The feather setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_context_set_feather_radius(feather_radius_x: float, feather_radius_y: float):
    """
    Set the feather radius setting.

    This procedure modifies the feather radius setting. This setting affects all procedures that are affected by 'gimp-context-set-feather'.

    :param feather_radius_x: The horizontal feather radius (0 <= feather-radius-x <= 1000)
    :param feather_radius_y: The vertical feather radius (0 <= feather-radius-y <= 1000)
    """
    raise NotImplementedError()


def gimp_context_set_font(name: str):
    """
    Set the specified font as the active font.

    This procedure allows the active font to be set by specifying its name. The name is simply a string which corresponds to one of the names of the installed fonts. If no matching font is found, this procedure will return an error. Otherwise, the specified font becomes active and will be used in all subsequent font operations.

    :param name: The name of the font
    """
    raise NotImplementedError()


def gimp_context_set_foreground(foreground: Color):
    """
    Set the current GIMP foreground color.

    This procedure sets the current GIMP foreground color. After this is set, operations which use foreground such as paint tools, blending, and bucket fill will use the new value.

    :param foreground: The foreground color
    """
    raise NotImplementedError()


def gimp_context_set_gradient(name: str):
    """
    Sets the specified gradient as the active gradient.

    This procedure lets you set the specified gradient as the active or "current" one. The name is simply a string which corresponds to one of the loaded gradients. If no matching gradient is found, this procedure will return an error. Otherwise, the specified gradient will become active and will be used for subsequent custom gradient operations.

    :param name: The name of the gradient
    """
    raise NotImplementedError()


def gimp_context_set_ink_angle(angle: float):
    """
    Set ink angle in degrees.

    Set the ink angle in degrees for ink tool.

    :param angle: ink angle in degrees (-90 <= angle <= 90)
    """
    raise NotImplementedError()


def gimp_context_set_ink_blob_angle(angle: float):
    """
    Set ink blob angle in degrees.

    Set the ink blob angle in degrees for ink tool.

    :param angle: ink blob angle in degrees (-180 <= angle <= 180)
    """
    raise NotImplementedError()


def gimp_context_set_ink_blob_aspect_ratio(aspect: float):
    """
    Set ink blob aspect ratio.

    Set the ink blob aspect ratio for ink tool.

    :param aspect: ink blob aspect ratio (1 <= aspect <= 10)
    """
    raise NotImplementedError()


def gimp_context_set_ink_blob_type(type: int):
    """
    Set ink blob type.

    Set the ink blob type for ink tool.

    :param type: Ink blob type { INK-BLOB-TYPE-CIRCLE (0), INK-BLOB-TYPE-SQUARE (1), INK-BLOB-TYPE-DIAMOND (2) }
    """
    raise NotImplementedError()


def gimp_context_set_ink_size(size: float):
    """
    Set ink blob size in pixels.

    Set the ink blob size in pixels for ink tool.

    :param size: ink blob size in pixels (0 <= size <= 200)
    """
    raise NotImplementedError()


def gimp_context_set_ink_size_sensitivity(size: float):
    """
    Set ink size sensitivity.

    Set the ink size sensitivity for ink tool.

    :param size: ink size sensitivity (0 <= size <= 1)
    """
    raise NotImplementedError()


def gimp_context_set_ink_speed_sensitivity(speed: float):
    """
    Set ink speed sensitivity.

    Set the ink speed sensitivity for ink tool.

    :param speed: ink speed sensitivity (0 <= speed <= 1)
    """
    raise NotImplementedError()


def gimp_context_set_ink_tilt_sensitivity(tilt: float):
    """
    Set ink tilt sensitivity.

    Set the ink tilt sensitivity for ink tool.

    :param tilt: ink tilt sensitivity (0 <= tilt <= 1)
    """
    raise NotImplementedError()


def gimp_context_set_interpolation(interpolation: int):
    """
    Set the interpolation type.

    This procedure modifies the interpolation setting. This setting affects affects the following procedures: 'gimp-item-transform-flip', 'gimp-item-transform-perspective', 'gimp-item-transform-rotate', 'gimp-item-transform-scale', 'gimp-item-transform-shear', 'gimp-item-transform-2d', 'gimp-item-transform-matrix', 'gimp-image-scale', 'gimp-layer-scale'.

    :param interpolation: The interpolation type { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    """
    raise NotImplementedError()


def gimp_context_set_opacity(opacity: float):
    """
    Set the opacity.

    This procedure modifies the opacity setting. The value should be a floating point number between 0 and 100.

    :param opacity: The opacity (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_context_set_paint_method(name: str):
    """
    Set the specified paint method as the active paint method.

    This procedure allows the active paint method to be set by specifying its name. The name is simply a string which corresponds to one of the names of the available paint methods. If there is no matching method found, this procedure will return an error. Otherwise, the specified method becomes active and will be used in all subsequent paint operations.

    :param name: The name of the paint method
    """
    raise NotImplementedError()


def gimp_context_set_paint_mode(paint_mode: int):
    """
    Set the paint mode.

    This procedure modifies the paint_mode setting.

    :param paint_mode: The paint mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    """
    raise NotImplementedError()


def gimp_context_set_palette(name: str):
    """
    Set the specified palette as the active palette.

    This procedure allows the active palette to be set by specifying its name. The name is simply a string which corresponds to one of the names of the installed palettes. If no matching palette is found, this procedure will return an error. Otherwise, the specified palette becomes active and will be used in all subsequent palette operations.

    :param name: The name of the palette
    """
    raise NotImplementedError()


def gimp_context_set_pattern(name: str):
    """
    Set the specified pattern as the active pattern.

    This procedure allows the active pattern to be set by specifying its name. The name is simply a string which corresponds to one of the names of the installed patterns. If there is no matching pattern found, this procedure will return an error. Otherwise, the specified pattern becomes active and will be used in all subsequent paint operations.

    :param name: The name of the pattern
    """
    raise NotImplementedError()


def gimp_context_set_sample_criterion(sample_criterion: int):
    """
    Set the sample criterion setting.

    This procedure modifies the sample criterion setting. If an operation depends on the colors of the pixels present in a drawable, like when doing a seed fill, this setting controls how color similarity is determined. SELECT_CRITERION_COMPOSITE is the default value. This setting affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color'.

    :param sample_criterion: The sample criterion setting { SELECT-CRITERION-COMPOSITE (0), SELECT-CRITERION-R (1), SELECT-CRITERION-G (2), SELECT-CRITERION-B (3), SELECT-CRITERION-H (4), SELECT-CRITERION-S (5), SELECT-CRITERION-V (6) }
    """
    raise NotImplementedError()


def gimp_context_set_sample_merged(sample_merged: int):
    """
    Set the sample merged setting.

    This procedure modifies the sample merged setting. If an operation depends on the colors of the pixels present in a drawable, like when doing a seed fill, this setting controls whether the pixel data from the specified drawable is used ('sample-merged' is FALSE), or the pixel data from the composite image ('sample-merged' is TRUE. This is equivalent to sampling for colors after merging all visible layers). This setting affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color'.

    :param sample_merged: The sample merged setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_context_set_sample_threshold(sample_threshold: float):
    """
    Set the sample threshold setting.

    This procedure modifies the sample threshold setting. If an operation depends on the colors of the pixels present in a drawable, like when doing a seed fill, this setting controls what is "sufficiently close" to be considered a similar color. If the sample threshold has not been set explicitly, the default threshold set in gimprc will be used. This setting affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color'.

    :param sample_threshold: The sample threshold setting (0 <= sample-threshold <= 1)
    """
    raise NotImplementedError()


def gimp_context_set_sample_threshold_int(sample_threshold: int):
    """
    Set the sample threshold setting as an integer value.

    This procedure modifies the sample threshold setting as an integer value. See 'gimp-context-set-sample-threshold'.

    :param sample_threshold: The sample threshold setting (0 <= sample-threshold <= 255)
    """
    raise NotImplementedError()


def gimp_context_set_sample_transparent(sample_transparent: int):
    """
    Set the sample transparent setting.

    This procedure modifies the sample transparent setting. If an operation depends on the colors of the pixels present in a drawable, like when doing a seed fill, this setting controls whether transparency is considered to be a unique selectable color. When this setting is TRUE, transparent areas can be selected or filled. This setting affects the following procedures: 'gimp-image-select-color', 'gimp-image-select-contiguous-color'.

    :param sample_transparent: The sample transparent setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_context_set_transform_direction(transform_direction: int):
    """
    Set the transform direction.

    This procedure modifies the transform direction setting. This setting affects affects the following procedures: 'gimp-item-transform-flip', 'gimp-item-transform-perspective', 'gimp-item-transform-rotate', 'gimp-item-transform-scale', 'gimp-item-transform-shear', 'gimp-item-transform-2d', 'gimp-item-transform-matrix'.

    :param transform_direction: The transform direction { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    """
    raise NotImplementedError()


def gimp_context_set_transform_recursion(transform_recursion: int):
    """
    Set the transform supersampling recursion.

    This procedure modifies the transform supersampling recursion level setting. Whether or not a transformation does supersampling is determined by the interplolation type. The recursion level defaults to 3, which is a nice default value. This setting affects affects the following procedures: 'gimp-item-transform-flip', 'gimp-item-transform-perspective', 'gimp-item-transform-rotate', 'gimp-item-transform-scale', 'gimp-item-transform-shear', 'gimp-item-transform-2d', 'gimp-item-transform-matrix'.

    :param transform_recursion: The transform recursion level (transform-recursion >= 1)
    """
    raise NotImplementedError()


def gimp_context_set_transform_resize(transform_resize: int):
    """
    Set the transform resize type.

    This procedure modifies the transform resize setting. When transforming pixels, if the result of a transform operation has a different size than the original area, this setting determines how the resulting area is sized. This setting affects affects the following procedures: 'gimp-item-transform-flip', 'gimp-item-transform-flip-simple', 'gimp-item-transform-perspective', 'gimp-item-transform-rotate', 'gimp-item-transform-rotate-simple', 'gimp-item-transform-scale', 'gimp-item-transform-shear', 'gimp-item-transform-2d', 'gimp-item-transform-matrix'.

    :param transform_resize: The transform resize type { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    """
    raise NotImplementedError()


def gimp_context_swap_colors():
    """
    Swap the current GIMP foreground and background colors.

    This procedure swaps the current GIMP foreground and background colors, so that the new foreground color becomes the old background color and vice versa.
    """
    raise NotImplementedError()


def gimp_convert_grayscale(image: Image):
    """
    This procedure is deprecated! Use 'gimp-image-convert-grayscale' instead.

    This procedure is deprecated! Use 'gimp-image-convert-grayscale' instead.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_convert_indexed(image: Image, dither_type: int, palette_type: int, num_cols: int, alpha_dither: int, remove_unused: int, palette: str):
    """
    This procedure is deprecated! Use 'gimp-image-convert-indexed' instead.

    This procedure is deprecated! Use 'gimp-image-convert-indexed' instead.

    :param image: The image
    :param dither_type: The dither type to use { NO-DITHER (0), FS-DITHER (1), FSLOWBLEED-DITHER (2), FIXED-DITHER (3) }
    :param palette_type: The type of palette to use { MAKE-PALETTE (0), WEB-PALETTE (2), MONO-PALETTE (3), CUSTOM-PALETTE (4) }
    :param num_cols: The number of colors to quantize to, ignored unless (palette_type == GIMP_MAKE_PALETTE)
    :param alpha_dither: Dither transparency to fake partial opacity (TRUE or FALSE)
    :param remove_unused: Remove unused or duplicate color entries from final palette, ignored if (palette_type == GIMP_MAKE_PALETTE) (TRUE or FALSE)
    :param palette: The name of the custom palette to use, ignored unless (palette_type == GIMP_CUSTOM_PALETTE)
    """
    raise NotImplementedError()


def gimp_convert_rgb(image: Image):
    """
    This procedure is deprecated! Use 'gimp-image-convert-rgb' instead.

    This procedure is deprecated! Use 'gimp-image-convert-rgb' instead.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_convolve(drawable: Drawable, pressure: float, convolve_type: int, num_strokes: int, strokes: List[float]):
    """
    Convolve (Blur, Sharpen) using the current brush.

    This tool convolves the specified drawable with either a sharpening or blurring kernel. The pressure parameter controls the magnitude of the operation. Like the paintbrush, this tool linearly interpolates between the specified stroke coordinates.

    :param drawable: The affected drawable
    :param pressure: The pressure (0 <= pressure <= 100)
    :param convolve_type: Convolve type { BLUR-CONVOLVE (0), SHARPEN-CONVOLVE (1) }
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_convolve_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Convolve (Blur, Sharpen) using the current brush.

    This tool convolves the specified drawable with either a sharpening or blurring kernel. This function performs exactly the same as the 'gimp-convolve' function except that the tools arguments are obtained from the convolve option dialog. It this dialog has not been activated then the dialogs default values will be used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_crop(image: Image, new_width: int, new_height: int, offx: int, offy: int):
    """
    This procedure is deprecated! Use 'gimp-image-crop' instead.

    This procedure is deprecated! Use 'gimp-image-crop' instead.

    :param image: The image
    :param new_width: New image width: (0 < new_width <= width) (1 <= new-width <= 262144)
    :param new_height: New image height: (0 < new_height <= height) (1 <= new-height <= 262144)
    :param offx: X offset: (0 <= offx <= (width - new_width)) (offx >= 0)
    :param offy: Y offset: (0 <= offy <= (height - new_height)) (offy >= 0)
    """
    raise NotImplementedError()


def gimp_curves_explicit(drawable: Drawable, channel: int, num_bytes: int, curve: List[int]):
    """
    Modifies the intensity curve(s) for specified drawable.

    Modifies the intensity mapping for one channel in the specified drawable. The drawable must be either grayscale or RGB, and the channel can be either an intensity component, or the value. The 'curve' parameter is an array of bytes which explicitly defines how each pixel value in the drawable will be modified. Use the 'gimp-curves-spline' function to modify intensity levels with Catmull Rom splines.

    :param drawable: The drawable
    :param channel: The channel to modify { HISTOGRAM-VALUE (0), HISTOGRAM-RED (1), HISTOGRAM-GREEN (2), HISTOGRAM-BLUE (3), HISTOGRAM-ALPHA (4), HISTOGRAM-RGB (5) }
    :param num_bytes: The number of bytes in the new curve (always 256) (num-bytes >= 0)
    :param curve: The explicit curve
    """
    raise NotImplementedError()


def gimp_curves_spline(drawable: Drawable, channel: int, num_points: int, control_pts: List[int]):
    """
    Modifies the intensity curve(s) for specified drawable.

    Modifies the intensity mapping for one channel in the specified drawable. The drawable must be either grayscale or RGB, and the channel can be either an intensity component, or the value. The 'control_pts' parameter is an array of integers which define a set of control points which describe a Catmull Rom spline which yields the final intensity curve. Use the 'gimp-curves-explicit' function to explicitly modify intensity levels.

    :param drawable: The drawable
    :param channel: The channel to modify { HISTOGRAM-VALUE (0), HISTOGRAM-RED (1), HISTOGRAM-GREEN (2), HISTOGRAM-BLUE (3), HISTOGRAM-ALPHA (4), HISTOGRAM-RGB (5) }
    :param num_points: The number of values in the control point array (4 <= num-points <= 34)
    :param control_pts: The spline control points: { cp1.x, cp1.y, cp2.x, cp2.y, ... }
    """
    raise NotImplementedError()


def gimp_desaturate(drawable: Drawable):
    """
    Desaturate the contents of the specified drawable.

    This procedure desaturates the contents of the specified drawable. This procedure only works on drawables of type RGB color.

    :param drawable: The drawable
    """
    raise NotImplementedError()


def gimp_desaturate_full(drawable: Drawable, desaturate_mode: int):
    """
    Desaturate the contents of the specified drawable, with the specified formula.

    This procedure desaturates the contents of the specified drawable, with the specified formula. This procedure only works on drawables of type RGB color.

    :param drawable: The drawable
    :param desaturate_mode: The formula to use to desaturate { DESATURATE-LIGHTNESS (0), DESATURATE-LUMINOSITY (1), DESATURATE-AVERAGE (2) }
    """
    raise NotImplementedError()


def gimp_detach_parasite(name: str):
    """
    Removes a global parasite.

    This procedure detaches a global parasite from. It has no return values.

    :param name: The name of the parasite to detach.
    """
    raise NotImplementedError()


def gimp_display_delete(display: Display):
    """
    Delete the specified display.

    This procedure removes the specified display. If this is the last remaining display for the underlying image, then the image is deleted also. Note that the display is closed no matter if the image is dirty or not. Better save the image before calling this procedure.

    :param display: The display to delete
    """
    raise NotImplementedError()


def gimp_display_get_window_handle(display: Display) -> int:
    """
    Get a handle to the native window for an image display.

    This procedure returns a handle to the native window for a given image display. For example in the X backend of GDK, a native window handle is an Xlib XID. A value of 0 is returned for an invalid display or if this function is unimplemented for the windowing system that is being used.

    :param display: The display to get the window handle from
    :return: window
    """
    raise NotImplementedError()


def gimp_display_is_valid(display: Display) -> int:
    """
    Returns TRUE if the display is valid.

    This procedure checks if the given display ID is valid and refers to an existing display.

    :param display: The display to check
    :return: valid
    """
    raise NotImplementedError()


def gimp_display_new(image: Image) -> Display:
    """
    Create a new display for the specified image.

    Creates a new display for the specified image. If the image already has a display, another is added. Multiple displays are handled transparently by GIMP. The newly created display is returned and can be subsequently destroyed with a call to 'gimp-display-delete'. This procedure only makes sense for use with the GIMP UI, and will result in an execution error if called when GIMP has no UI.

    :param image: The image
    :return: display
    """
    raise NotImplementedError()


def gimp_displays_flush():
    """
    Flush all internal changes to the user interface

    This procedure takes no arguments and returns nothing except a success status. Its purpose is to flush all pending updates of image manipulations to the user interface. It should be called whenever appropriate.
    """
    raise NotImplementedError()


def gimp_displays_reconnect(old_image: Image, new_image: Image):
    """
    Reconnect displays from one image to another image.

    This procedure connects all displays of the old_image to the new_image. If the old_image has no display or new_image already has a display the reconnect is not performed and the procedure returns without success. You should rarely need to use this function.

    :param old_image: The old image (must have at least one display)
    :param new_image: The new image (must not have a display)
    """
    raise NotImplementedError()


def gimp_dodgeburn(drawable: Drawable, exposure: float, dodgeburn_type: int, dodgeburn_mode: int, num_strokes: int, strokes: List[float]):
    """
    Dodgeburn image with varying exposure.

    Dodgeburn. More details here later.

    :param drawable: The affected drawable
    :param exposure: The exposure of the strokes (0 <= exposure <= 100)
    :param dodgeburn_type: The type either dodge or burn { DODGE (0), BURN (1) }
    :param dodgeburn_mode: The mode { SHADOWS (0), MIDTONES (1), HIGHLIGHTS (2) }
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_dodgeburn_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Dodgeburn image with varying exposure. This is the same as the gimp_dodgeburn() function except that the exposure, type and mode are taken from the tools option dialog. If the dialog has not been activated then the defaults as used by the dialog will be used.

    Dodgeburn. More details here later.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_drawable_bpp(drawable: Drawable) -> int:
    """
    Returns the bytes per pixel.

    This procedure returns the number of bytes per pixel (or the number of channels) for the specified drawable.

    :param drawable: The drawable
    :return: bpp
    """
    raise NotImplementedError()


def gimp_drawable_bytes(drawable: Drawable) -> int:
    """
    This procedure is deprecated! Use 'gimp-drawable-bpp' instead.

    This procedure is deprecated! Use 'gimp-drawable-bpp' instead.

    :param drawable: The drawable
    :return: bpp
    """
    raise NotImplementedError()


def gimp_drawable_delete(item: Item):
    """
    This procedure is deprecated! Use 'gimp-item-delete' instead.

    This procedure is deprecated! Use 'gimp-item-delete' instead.

    :param item: The item to delete
    """
    raise NotImplementedError()


def gimp_drawable_fill(drawable: Drawable, fill_type: int):
    """
    Fill the drawable with the specified fill mode.

    This procedure fills the drawable. If the fill mode is foreground the current foreground color is used. If the fill mode is background, the current background color is used. If the fill type is white, then white is used. Transparent fill only affects layers with an alpha channel, in which case the alpha channel is set to transparent. If the drawable has no alpha channel, it is filled to white. No fill leaves the drawable's contents undefined. This procedure is unlike 'gimp-edit-fill' or the bucket fill tool because it fills regardless of a selection. Its main purpose is to fill a newly created drawable before adding it to the image. This operation cannot be undone.

    :param drawable: The drawable
    :param fill_type: The type of fill { FOREGROUND-FILL (0), BACKGROUND-FILL (1), WHITE-FILL (2), TRANSPARENT-FILL (3), PATTERN-FILL (4), NO-FILL (5) }
    """
    raise NotImplementedError()


def gimp_drawable_foreground_extract(drawable: Drawable, mode: int, mask: Drawable):
    """
    Extract the foreground of a drawable using a given trimap.

    Image Segmentation by Uniform Color Clustering, see http://www.inf.fu-berlin.de/inst/pubs/tr-b-05-07.pdf

    :param drawable: The drawable
    :param mode: The algorithm to use { FOREGROUND-EXTRACT-SIOX (0) }
    :param mask: Tri-Map
    """
    raise NotImplementedError()


def gimp_drawable_free_shadow(drawable: Drawable):
    """
    Free the specified drawable's shadow data (if it exists).

    This procedure is intended as a memory saving device. If any shadow memory has been allocated, it will be freed automatically when the drawable is removed from the image, or when the plug-in procedure which allocated it returns.

    :param drawable: The drawable
    """
    raise NotImplementedError()


def gimp_drawable_get_image(item: Item) -> Image:
    """
    This procedure is deprecated! Use 'gimp-item-get-image' instead.

    This procedure is deprecated! Use 'gimp-item-get-image' instead.

    :param item: The item
    :return: image
    """
    raise NotImplementedError()


def gimp_drawable_get_linked(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    :param item: The item
    :return: linked
    """
    raise NotImplementedError()


def gimp_drawable_get_name(item: Item) -> str:
    """
    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    :param item: The item
    :return: name
    """
    raise NotImplementedError()


def gimp_drawable_get_pixel(drawable: Drawable, x_coord: int, y_coord: int) -> Tuple[int, List[int]]:
    """
    Gets the value of the pixel at the specified coordinates.

    This procedure gets the pixel value at the specified coordinates. The 'num_channels' argument must always be equal to the bytes-per-pixel value for the specified drawable.

    :param drawable: The drawable
    :param x_coord: The x coordinate (x-coord >= 0)
    :param y_coord: The y coordinate (y-coord >= 0)
    :return: num_channels, pixel
    """
    raise NotImplementedError()


def gimp_drawable_get_tattoo(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    :param item: The item
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_drawable_get_visible(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    :param item: The item
    :return: visible
    """
    raise NotImplementedError()


def gimp_drawable_has_alpha(drawable: Drawable) -> int:
    """
    Returns TRUE if the drawable has an alpha channel.

    This procedure returns whether the specified drawable has an alpha channel. This can only be true for layers, and the associated type will be one of: { RGBA , GRAYA, INDEXEDA }.

    :param drawable: The drawable
    :return: has_alpha
    """
    raise NotImplementedError()


def gimp_drawable_height(drawable: Drawable) -> int:
    """
    Returns the height of the drawable.

    This procedure returns the specified drawable's height in pixels.

    :param drawable: The drawable
    :return: height
    """
    raise NotImplementedError()


def gimp_drawable_is_channel(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-channel' instead.

    This procedure is deprecated! Use 'gimp-item-is-channel' instead.

    :param item: The item
    :return: channel
    """
    raise NotImplementedError()


def gimp_drawable_is_gray(drawable: Drawable) -> int:
    """
    Returns whether the drawable is a grayscale type.

    This procedure returns TRUE if the specified drawable is of type { Gray, GrayA }.

    :param drawable: The drawable
    :return: is_gray
    """
    raise NotImplementedError()


def gimp_drawable_is_indexed(drawable: Drawable) -> int:
    """
    Returns whether the drawable is an indexed type.

    This procedure returns TRUE if the specified drawable is of type { Indexed, IndexedA }.

    :param drawable: The drawable
    :return: is_indexed
    """
    raise NotImplementedError()


def gimp_drawable_is_layer(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-layer' instead.

    This procedure is deprecated! Use 'gimp-item-is-layer' instead.

    :param item: The item
    :return: layer
    """
    raise NotImplementedError()


def gimp_drawable_is_layer_mask(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-layer-mask' instead.

    This procedure is deprecated! Use 'gimp-item-is-layer-mask' instead.

    :param item: The item
    :return: layer_mask
    """
    raise NotImplementedError()


def gimp_drawable_is_rgb(drawable: Drawable) -> int:
    """
    Returns whether the drawable is an RGB type.

    This procedure returns TRUE if the specified drawable is of type { RGB, RGBA }.

    :param drawable: The drawable
    :return: is_rgb
    """
    raise NotImplementedError()


def gimp_drawable_is_text_layer(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-text-layer' instead.

    This procedure is deprecated! Use 'gimp-item-is-text-layer' instead.

    :param item: The item
    :return: text_layer
    """
    raise NotImplementedError()


def gimp_drawable_is_valid(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-valid' instead.

    This procedure is deprecated! Use 'gimp-item-is-valid' instead.

    :param item: The item to check
    :return: valid
    """
    raise NotImplementedError()


def gimp_drawable_mask_bounds(drawable: Drawable) -> Tuple[int, int, int, int, int]:
    """
    Find the bounding box of the current selection in relation to the specified drawable.

    This procedure returns whether there is a selection. If there is one, the upper left and lower right-hand corners of its bounding box are returned. These coordinates are specified relative to the drawable's origin, and bounded by the drawable's extents. Please note that the pixel specified by the lower right-hand coordinate of the bounding box is not part of the selection. The selection ends at the upper left corner of this pixel. This means the width of the selection can be calculated as (x2 - x1), its height as (y2 - y1). Note that the returned boolean does NOT correspond with the returned region being empty or not, it always returns whether the selection is non_empty. See 'gimp-drawable-mask-intersect' for a boolean return value which is more useful in most cases.

    :param drawable: The drawable
    :return: non_empty, x1, y1, x2, y2
    """
    raise NotImplementedError()


def gimp_drawable_mask_intersect(drawable: Drawable) -> Tuple[int, int, int, int, int]:
    """
    Find the bounding box of the current selection in relation to the specified drawable.

    This procedure returns whether there is an intersection between the drawable and the selection. Unlike 'gimp-drawable-mask-bounds', the intersection's bounds are returned as x, y, width, height. If there is no selection this function returns TRUE and the returned bounds are the extents of the whole drawable.

    :param drawable: The drawable
    :return: non_empty, x, y, width, height
    """
    raise NotImplementedError()


def gimp_drawable_merge_shadow(drawable: Drawable, undo: int):
    """
    Merge the shadow buffer with the specified drawable.

    This procedure combines the contents of the drawable's shadow buffer (for temporary processing) with the specified drawable. The 'undo' parameter specifies whether to add an undo step for the operation. Requesting no undo is useful for such applications as 'auto-apply'.

    :param drawable: The drawable
    :param undo: Push merge to undo stack? (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_drawable_offset(drawable: Drawable, wrap_around: int, fill_type: int, offset_x: int, offset_y: int):
    """
    Offset the drawable by the specified amounts in the X and Y directions

    This procedure offsets the specified drawable by the amounts specified by 'offset_x' and 'offset_y'. If 'wrap_around' is set to TRUE, then portions of the drawable which are offset out of bounds are wrapped around. Alternatively, the undefined regions of the drawable can be filled with transparency or the background color, as specified by the 'fill-type' parameter.

    :param drawable: The drawable to offset
    :param wrap_around: wrap image around or fill vacated regions (TRUE or FALSE)
    :param fill_type: fill vacated regions of drawable with background or transparent { OFFSET-BACKGROUND (0), OFFSET-TRANSPARENT (1) }
    :param offset_x: offset by this amount in X direction
    :param offset_y: offset by this amount in Y direction
    """
    raise NotImplementedError()


def gimp_drawable_offsets(drawable: Drawable) -> Tuple[int, int]:
    """
    Returns the offsets for the drawable.

    This procedure returns the specified drawable's offsets. This only makes sense if the drawable is a layer since channels are anchored. The offsets of a channel will be returned as 0.

    :param drawable: The drawable
    :return: offset_x, offset_y
    """
    raise NotImplementedError()


def gimp_drawable_parasite_attach(item: Item, parasite: Parasite):
    """
    This procedure is deprecated! Use 'gimp-item-attach-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-attach-parasite' instead.

    :param item: The item
    :param parasite: The parasite to attach to the item
    """
    raise NotImplementedError()


def gimp_drawable_parasite_detach(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-detach-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-detach-parasite' instead.

    :param item: The item
    :param name: The name of the parasite to detach from the item.
    """
    raise NotImplementedError()


def gimp_drawable_parasite_find(item: Item, name: str) -> Parasite:
    """
    This procedure is deprecated! Use 'gimp-item-get-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-get-parasite' instead.

    :param item: The item
    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_drawable_parasite_list(item: Item) -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-item-get-parasite-list' instead.

    This procedure is deprecated! Use 'gimp-item-get-parasite-list' instead.

    :param item: The item
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_drawable_set_image(drawable: Drawable, image: Image):
    """
    Deprecated: There is no replacement for this procedure.

    Deprecated: There is no replacement for this procedure.

    :param drawable: The drawable
    :param image: The image
    """
    raise NotImplementedError()


def gimp_drawable_set_linked(item: Item, linked: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    :param item: The item
    :param linked: The new item linked state (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_drawable_set_name(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    :param item: The item
    :param name: The new item name
    """
    raise NotImplementedError()


def gimp_drawable_set_pixel(drawable: Drawable, x_coord: int, y_coord: int, num_channels: int, pixel: List[int]):
    """
    Sets the value of the pixel at the specified coordinates.

    This procedure sets the pixel value at the specified coordinates. The 'num_channels' argument must always be equal to the bytes-per-pixel value for the specified drawable. Note that this function is not undoable, you should use it only on drawables you just created yourself.

    :param drawable: The drawable
    :param x_coord: The x coordinate (x-coord >= 0)
    :param y_coord: The y coordinate (y-coord >= 0)
    :param num_channels: The number of channels for the pixel (num-channels >= 0)
    :param pixel: The pixel value
    """
    raise NotImplementedError()


def gimp_drawable_set_tattoo(item: Item, tattoo: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    :param item: The item
    :param tattoo: The new item tattoo
    """
    raise NotImplementedError()


def gimp_drawable_set_visible(item: Item, visible: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    :param item: The item
    :param visible: The new item visibility (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_drawable_sub_thumbnail(drawable: Drawable, src_x: int, src_y: int, src_width: int, src_height: int, dest_width: int, dest_height: int) -> Tuple[int, int, int, int, List[int]]:
    """
    Get a thumbnail of a sub-area of a drawable drawable.

    This function gets data from which a thumbnail of a drawable preview can be created. Maximum x or y dimension is 1024 pixels. The pixels are returned in RGB[A] or GRAY[A] format. The bpp return value gives the number of bytes in the image.

    :param drawable: The drawable
    :param src_x: The x coordinate of the area (src-x >= 0)
    :param src_y: The y coordinate of the area (src-y >= 0)
    :param src_width: The width of the area (src-width >= 1)
    :param src_height: The height of the area (src-height >= 1)
    :param dest_width: The thumbnail width (1 <= dest-width <= 1024)
    :param dest_height: The thumbnail height (1 <= dest-height <= 1024)
    :return: width, height, bpp, thumbnail_data_count, thumbnail_data
    """
    raise NotImplementedError()


def gimp_drawable_thumbnail(drawable: Drawable, width: int, height: int) -> Tuple[int, int, int, int, List[int]]:
    """
    Get a thumbnail of a drawable.

    This function gets data from which a thumbnail of a drawable preview can be created. Maximum x or y dimension is 1024 pixels. The pixels are returned in RGB[A] or GRAY[A] format. The bpp return value gives the number of bytes in the image.

    :param drawable: The drawable
    :param width: The requested thumbnail width (1 <= width <= 1024)
    :param height: The requested thumbnail height (1 <= height <= 1024)
    :return: actual_width, actual_height, bpp, thumbnail_data_count, thumbnail_data
    """
    raise NotImplementedError()


def gimp_drawable_transform_2d(drawable: Drawable, source_x: float, source_y: float, scale_x: float, scale_y: float, angle: float, dest_x: float, dest_y: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-2d' instead.

    Deprecated: Use 'gimp-item-transform-2d' instead.

    :param drawable: The affected drawable
    :param source_x: X coordinate of the transformation center
    :param source_y: Y coordinate of the transformation center
    :param scale_x: Amount to scale in x direction
    :param scale_y: Amount to scale in y direction
    :param angle: The angle of rotation (radians)
    :param dest_x: X coordinate of where the center goes
    :param dest_y: Y coordinate of where the center goes
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_2d_default(drawable: Drawable, source_x: float, source_y: float, scale_x: float, scale_y: float, angle: float, dest_x: float, dest_y: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-2d' instead.

    Deprecated: Use 'gimp-item-transform-2d' instead.

    :param drawable: The affected drawable
    :param source_x: X coordinate of the transformation center
    :param source_y: Y coordinate of the transformation center
    :param scale_x: Amount to scale in x direction
    :param scale_y: Amount to scale in y direction
    :param angle: The angle of rotation (radians)
    :param dest_x: X coordinate of where the center goes
    :param dest_y: Y coordinate of where the center goes
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_flip(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-flip' instead.

    Deprecated: Use 'gimp-item-transform-flip' instead.

    :param drawable: The affected drawable
    :param x0: horz. coord. of one end of axis
    :param y0: vert. coord. of one end of axis
    :param x1: horz. coord. of other end of axis
    :param y1: vert. coord. of other end of axis
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: Whether to clip results (TRUE or FALSE)
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_flip_default(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-flip' instead.

    Deprecated: Use 'gimp-item-transform-flip' instead.

    :param drawable: The affected drawable
    :param x0: horz. coord. of one end of axis
    :param y0: vert. coord. of one end of axis
    :param x1: horz. coord. of other end of axis
    :param y1: vert. coord. of other end of axis
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: Whether to clip results (TRUE or FALSE)
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_flip_simple(drawable: Drawable, flip_type: int, auto_center: int, axis: float, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-flip-simple' instead.

    Deprecated: Use 'gimp-item-transform-flip-simple' instead.

    :param drawable: The affected drawable
    :param flip_type: Type of flip { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param auto_center: Whether to automatically position the axis in the selection center (TRUE or FALSE)
    :param axis: coord. of flip axis
    :param clip_result: Whether to clip results (TRUE or FALSE)
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_matrix(drawable: Drawable, coeff_0_0: float, coeff_0_1: float, coeff_0_2: float, coeff_1_0: float, coeff_1_1: float, coeff_1_2: float, coeff_2_0: float, coeff_2_1: float, coeff_2_2: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-matrix' instead.

    Deprecated: Use 'gimp-item-transform-matrix' instead.

    :param drawable: The affected drawable
    :param coeff_0_0: coefficient (0,0) of the transformation matrix
    :param coeff_0_1: coefficient (0,1) of the transformation matrix
    :param coeff_0_2: coefficient (0,2) of the transformation matrix
    :param coeff_1_0: coefficient (1,0) of the transformation matrix
    :param coeff_1_1: coefficient (1,1) of the transformation matrix
    :param coeff_1_2: coefficient (1,2) of the transformation matrix
    :param coeff_2_0: coefficient (2,0) of the transformation matrix
    :param coeff_2_1: coefficient (2,1) of the transformation matrix
    :param coeff_2_2: coefficient (2,2) of the transformation matrix
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_matrix_default(drawable: Drawable, coeff_0_0: float, coeff_0_1: float, coeff_0_2: float, coeff_1_0: float, coeff_1_1: float, coeff_1_2: float, coeff_2_0: float, coeff_2_1: float, coeff_2_2: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-matrix' instead.

    Deprecated: Use 'gimp-item-transform-matrix' instead.

    :param drawable: The affected drawable
    :param coeff_0_0: coefficient (0,0) of the transformation matrix
    :param coeff_0_1: coefficient (0,1) of the transformation matrix
    :param coeff_0_2: coefficient (0,2) of the transformation matrix
    :param coeff_1_0: coefficient (1,0) of the transformation matrix
    :param coeff_1_1: coefficient (1,1) of the transformation matrix
    :param coeff_1_2: coefficient (1,2) of the transformation matrix
    :param coeff_2_0: coefficient (2,0) of the transformation matrix
    :param coeff_2_1: coefficient (2,1) of the transformation matrix
    :param coeff_2_2: coefficient (2,2) of the transformation matrix
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_perspective(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-perspective' instead.

    Deprecated: Use 'gimp-item-transform-perspective' instead.

    :param drawable: The affected drawable
    :param x0: The new x coordinate of upper-left corner of original bounding box
    :param y0: The new y coordinate of upper-left corner of original bounding box
    :param x1: The new x coordinate of upper-right corner of original bounding box
    :param y1: The new y coordinate of upper-right corner of original bounding box
    :param x2: The new x coordinate of lower-left corner of original bounding box
    :param y2: The new y coordinate of lower-left corner of original bounding box
    :param x3: The new x coordinate of lower-right corner of original bounding box
    :param y3: The new y coordinate of lower-right corner of original bounding box
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_perspective_default(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-perspective' instead.

    Deprecated: Use 'gimp-item-transform-perspective' instead.

    :param drawable: The affected drawable
    :param x0: The new x coordinate of upper-left corner of original bounding box
    :param y0: The new y coordinate of upper-left corner of original bounding box
    :param x1: The new x coordinate of upper-right corner of original bounding box
    :param y1: The new y coordinate of upper-right corner of original bounding box
    :param x2: The new x coordinate of lower-left corner of original bounding box
    :param y2: The new y coordinate of lower-left corner of original bounding box
    :param x3: The new x coordinate of lower-right corner of original bounding box
    :param y3: The new y coordinate of lower-right corner of original bounding box
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_rotate(drawable: Drawable, angle: float, auto_center: int, center_x: int, center_y: int, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-rotate' instead.

    Deprecated: Use 'gimp-item-transform-rotate' instead.

    :param drawable: The affected drawable
    :param angle: The angle of rotation (radians)
    :param auto_center: Whether to automatically rotate around the selection center (TRUE or FALSE)
    :param center_x: The hor. coordinate of the center of rotation
    :param center_y: The vert. coordinate of the center of rotation
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_rotate_default(drawable: Drawable, angle: float, auto_center: int, center_x: int, center_y: int, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-rotate' instead.

    Deprecated: Use 'gimp-item-transform-rotate' instead.

    :param drawable: The affected drawable
    :param angle: The angle of rotation (radians)
    :param auto_center: Whether to automatically rotate around the selection center (TRUE or FALSE)
    :param center_x: The hor. coordinate of the center of rotation
    :param center_y: The vert. coordinate of the center of rotation
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_rotate_simple(drawable: Drawable, rotate_type: int, auto_center: int, center_x: int, center_y: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-rotate-simple' instead.

    Deprecated: Use 'gimp-item-transform-rotate-simple' instead.

    :param drawable: The affected drawable
    :param rotate_type: Type of rotation { ROTATE-90 (0), ROTATE-180 (1), ROTATE-270 (2) }
    :param auto_center: Whether to automatically rotate around the selection center (TRUE or FALSE)
    :param center_x: The hor. coordinate of the center of rotation
    :param center_y: The vert. coordinate of the center of rotation
    :param clip_result: Whether to clip results (TRUE or FALSE)
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_scale(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-scale' instead.

    Deprecated: Use 'gimp-item-transform-scale' instead.

    :param drawable: The affected drawable
    :param x0: The new x coordinate of the upper-left corner of the scaled region
    :param y0: The new y coordinate of the upper-left corner of the scaled region
    :param x1: The new x coordinate of the lower-right corner of the scaled region
    :param y1: The new y coordinate of the lower-right corner of the scaled region
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_scale_default(drawable: Drawable, x0: float, y0: float, x1: float, y1: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-scale' instead.

    Deprecated: Use 'gimp-item-transform-scale' instead.

    :param drawable: The affected drawable
    :param x0: The new x coordinate of the upper-left corner of the scaled region
    :param y0: The new y coordinate of the upper-left corner of the scaled region
    :param x1: The new x coordinate of the lower-right corner of the scaled region
    :param y1: The new y coordinate of the lower-right corner of the scaled region
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_shear(drawable: Drawable, shear_type: int, magnitude: float, transform_direction: int, interpolation: int, supersample: int, recursion_level: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-shear' instead.

    Deprecated: Use 'gimp-item-transform-shear' instead.

    :param drawable: The affected drawable
    :param shear_type: Type of shear { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param magnitude: The magnitude of the shear
    :param transform_direction: Direction of transformation { TRANSFORM-FORWARD (0), TRANSFORM-BACKWARD (1) }
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    :param supersample: This parameter is ignored, supersampling is performed based on the interpolation type (TRUE or FALSE)
    :param recursion_level: Maximum recursion level used for supersampling (3 is a nice value) (recursion-level >= 1)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_transform_shear_default(drawable: Drawable, shear_type: int, magnitude: float, interpolate: int, clip_result: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-shear' instead.

    Deprecated: Use 'gimp-item-transform-shear' instead.

    :param drawable: The affected drawable
    :param shear_type: Type of shear { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param magnitude: The magnitude of the shear
    :param interpolate: Whether to use interpolation and supersampling (TRUE or FALSE)
    :param clip_result: How to clip results { TRANSFORM-RESIZE-ADJUST (0), TRANSFORM-RESIZE-CLIP (1), TRANSFORM-RESIZE-CROP (2), TRANSFORM-RESIZE-CROP-WITH-ASPECT (3) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_drawable_type(drawable: Drawable) -> int:
    """
    Returns the drawable's type.

    This procedure returns the drawable's type.

    :param drawable: The drawable
    :return: type
    """
    raise NotImplementedError()


def gimp_drawable_type_with_alpha(drawable: Drawable) -> int:
    """
    Returns the drawable's type with alpha.

    This procedure returns the drawable's type as if had an alpha channel. If the type is currently Gray, for instance, the returned type would be GrayA. If the drawable already has an alpha channel, the drawable's type is simply returned.

    :param drawable: The drawable
    :return: type_with_alpha
    """
    raise NotImplementedError()


def gimp_drawable_update(drawable: Drawable, x: int, y: int, width: int, height: int):
    """
    Update the specified region of the drawable.

    This procedure updates the specified region of the drawable. The (x, y) coordinate pair is relative to the drawable's origin, not to the image origin. Therefore, the entire drawable can be updated using (0, 0, width, height).

    :param drawable: The drawable
    :param x: x coordinate of upper left corner of update region
    :param y: y coordinate of upper left corner of update region
    :param width: Width of update region
    :param height: Height of update region
    """
    raise NotImplementedError()


def gimp_drawable_width(drawable: Drawable) -> int:
    """
    Returns the width of the drawable.

    This procedure returns the specified drawable's width in pixels.

    :param drawable: The drawable
    :return: width
    """
    raise NotImplementedError()


def gimp_dynamics_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve the list of loaded paint dynamics.

    This procedure returns a list of the paint dynamics that are currently available.

    :param filter: An optional regular expression used to filter the list
    :return: num_dynamics, dynamics_list
    """
    raise NotImplementedError()


def gimp_dynamics_refresh():
    """
    Refresh current paint dynamics. This function always succeeds.

    This procedure retrieves all paint dynamics currently in the user's paint dynamics path and updates the paint dynamics dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_edit_blend(drawable: Drawable, blend_mode: int, paint_mode: int, gradient_type: int, opacity: float, offset: float, repeat: int, reverse: int, supersample: int, max_depth: int, threshold: float, dither: int, x1: float, y1: float, x2: float, y2: float):
    """
    Blend between the starting and ending coordinates with the specified blend mode and gradient type.

    This tool requires information on the paint application mode, the blend mode, and the gradient type. It creates the specified variety of blend using the starting and ending coordinates as defined for each gradient type.

    :param drawable: The affected drawable
    :param blend_mode: The type of blend { FG-BG-RGB-MODE (0), FG-BG-HSV-MODE (1), FG-TRANSPARENT-MODE (2), CUSTOM-MODE (3) }
    :param paint_mode: The paint application mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :param gradient_type: The type of gradient { GRADIENT-LINEAR (0), GRADIENT-BILINEAR (1), GRADIENT-RADIAL (2), GRADIENT-SQUARE (3), GRADIENT-CONICAL-SYMMETRIC (4), GRADIENT-CONICAL-ASYMMETRIC (5), GRADIENT-SHAPEBURST-ANGULAR (6), GRADIENT-SHAPEBURST-SPHERICAL (7), GRADIENT-SHAPEBURST-DIMPLED (8), GRADIENT-SPIRAL-CLOCKWISE (9), GRADIENT-SPIRAL-ANTICLOCKWISE (10) }
    :param opacity: The opacity of the final blend (0 <= opacity <= 100)
    :param offset: Offset relates to the starting and ending coordinates specified for the blend. This parameter is mode dependent. (offset >= 0)
    :param repeat: Repeat mode { REPEAT-NONE (0), REPEAT-SAWTOOTH (1), REPEAT-TRIANGULAR (2) }
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :param supersample: Do adaptive supersampling (TRUE or FALSE)
    :param max_depth: Maximum recursion levels for supersampling (1 <= max-depth <= 9)
    :param threshold: Supersampling threshold (0 <= threshold <= 4)
    :param dither: Use dithering to reduce banding (TRUE or FALSE)
    :param x1: The x coordinate of this blend's starting point
    :param y1: The y coordinate of this blend's starting point
    :param x2: The x coordinate of this blend's ending point
    :param y2: The y coordinate of this blend's ending point
    """
    raise NotImplementedError()


def gimp_edit_bucket_fill(drawable: Drawable, fill_mode: int, paint_mode: int, opacity: float, threshold: float, sample_merged: int, x: float, y: float):
    """
    Fill the area specified either by the current selection if there is one, or by a seed fill starting at the specified coordinates.

    This tool requires information on the paint application mode, and the fill mode, which can either be in the foreground color, or in the currently active pattern. If there is no selection, a seed fill is executed at the specified coordinates and extends outward in keeping with the threshold parameter. If there is a selection in the target image, the threshold, sample merged, x, and y arguments are unused. If the sample_merged parameter is TRUE, the data of the composite image will be used instead of that for the specified drawable. This is equivalent to sampling for colors after merging all visible layers. In the case of merged sampling, the x and y coordinates are relative to the image's origin; otherwise, they are relative to the drawable's origin.

    :param drawable: The affected drawable
    :param fill_mode: The type of fill { FG-BUCKET-FILL (0), BG-BUCKET-FILL (1), PATTERN-BUCKET-FILL (2) }
    :param paint_mode: The paint application mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :param opacity: The opacity of the final bucket fill (0 <= opacity <= 100)
    :param threshold: The threshold determines how extensive the seed fill will be. It's value is specified in terms of intensity levels. This parameter is only valid when there is no selection in the specified image. (0 <= threshold <= 255)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param x: The x coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    :param y: The y coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    """
    raise NotImplementedError()


def gimp_edit_bucket_fill_full(drawable: Drawable, fill_mode: int, paint_mode: int, opacity: float, threshold: float, sample_merged: int, fill_transparent: int, select_criterion: int, x: float, y: float):
    """
    Fill the area specified either by the current selection if there is one, or by a seed fill starting at the specified coordinates.

    This tool requires information on the paint application mode, and the fill mode, which can either be in the foreground color, or in the currently active pattern. If there is no selection, a seed fill is executed at the specified coordinates and extends outward in keeping with the threshold parameter. If there is a selection in the target image, the threshold, sample merged, x, and y arguments are unused. If the sample_merged parameter is TRUE, the data of the composite image will be used instead of that for the specified drawable. This is equivalent to sampling for colors after merging all visible layers. In the case of merged sampling, the x and y coordinates are relative to the image's origin; otherwise, they are relative to the drawable's origin.

    :param drawable: The affected drawable
    :param fill_mode: The type of fill { FG-BUCKET-FILL (0), BG-BUCKET-FILL (1), PATTERN-BUCKET-FILL (2) }
    :param paint_mode: The paint application mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :param opacity: The opacity of the final bucket fill (0 <= opacity <= 100)
    :param threshold: The threshold determines how extensive the seed fill will be. It's value is specified in terms of intensity levels. This parameter is only valid when there is no selection in the specified image. (0 <= threshold <= 255)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param fill_transparent: Whether to consider transparent pixels for filling. If TRUE, transparency is considered as a unique fillable color. (TRUE or FALSE)
    :param select_criterion: The criterion used to determine color similarity. SELECT_CRITERION_COMPOSITE is the standard choice. { SELECT-CRITERION-COMPOSITE (0), SELECT-CRITERION-R (1), SELECT-CRITERION-G (2), SELECT-CRITERION-B (3), SELECT-CRITERION-H (4), SELECT-CRITERION-S (5), SELECT-CRITERION-V (6) }
    :param x: The x coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    :param y: The y coordinate of this bucket fill's application. This parameter is only valid when there is no selection in the specified image.
    """
    raise NotImplementedError()


def gimp_edit_clear(drawable: Drawable):
    """
    Clear selected area of drawable.

    This procedure clears the specified drawable. If the drawable has an alpha channel, the cleared pixels will become transparent. If the drawable does not have an alpha channel, cleared pixels will be set to the background color. This procedure only affects regions within a selection if there is a selection active.

    :param drawable: The drawable to clear from
    """
    raise NotImplementedError()


def gimp_edit_copy(drawable: Drawable) -> int:
    """
    Copy from the specified drawable.

    If there is a selection in the image, then the area specified by the selection is copied from the specified drawable and placed in an internal GIMP edit buffer. It can subsequently be retrieved using the 'gimp-edit-paste' command. If there is no selection, then the specified drawable's contents will be stored in the internal GIMP edit buffer. This procedure will fail if the selected area lies completely outside the bounds of the current drawable and there is nothing to copy from.

    :param drawable: The drawable to copy from
    :return: non_empty
    """
    raise NotImplementedError()


def gimp_edit_copy_visible(image: Image) -> int:
    """
    Copy from the projection.

    If there is a selection in the image, then the area specified by the selection is copied from the projection and placed in an internal GIMP edit buffer. It can subsequently be retrieved using the 'gimp-edit-paste' command. If there is no selection, then the projection's contents will be stored in the internal GIMP edit buffer.

    :param image: The image to copy from
    :return: non_empty
    """
    raise NotImplementedError()


def gimp_edit_cut(drawable: Drawable) -> int:
    """
    Cut from the specified drawable.

    If there is a selection in the image, then the area specified by the selection is cut from the specified drawable and placed in an internal GIMP edit buffer. It can subsequently be retrieved using the 'gimp-edit-paste' command. If there is no selection, then the specified drawable will be removed and its contents stored in the internal GIMP edit buffer. This procedure will fail if the selected area lies completely outside the bounds of the current drawable and there is nothing to copy from.

    :param drawable: The drawable to cut from
    :return: non_empty
    """
    raise NotImplementedError()


def gimp_edit_fill(drawable: Drawable, fill_type: int):
    """
    Fill selected area of drawable.

    This procedure fills the specified drawable with the fill mode. If the fill mode is foreground, the current foreground color is used. If the fill mode is background, the current background color is used. Other fill modes should not be used. This procedure only affects regions within a selection if there is a selection active. If you want to fill the whole drawable, regardless of the selection, use 'gimp-drawable-fill'.

    :param drawable: The drawable to fill to
    :param fill_type: The type of fill { FOREGROUND-FILL (0), BACKGROUND-FILL (1), WHITE-FILL (2), TRANSPARENT-FILL (3), PATTERN-FILL (4), NO-FILL (5) }
    """
    raise NotImplementedError()


def gimp_edit_named_copy(drawable: Drawable, buffer_name: str) -> str:
    """
    Copy into a named buffer.

    This procedure works like 'gimp-edit-copy', but additionally stores the copied buffer into a named buffer that will stay available for later pasting, regardless of any intermediate copy or cut operations.

    :param drawable: The drawable to copy from
    :param buffer_name: The name of the buffer to create
    :return: real_name
    """
    raise NotImplementedError()


def gimp_edit_named_copy_visible(image: Image, buffer_name: str) -> str:
    """
    Copy from the projection into a named buffer.

    This procedure works like 'gimp-edit-copy-visible', but additionally stores the copied buffer into a named buffer that will stay available for later pasting, regardless of any intermediate copy or cut operations.

    :param image: The image to copy from
    :param buffer_name: The name of the buffer to create
    :return: real_name
    """
    raise NotImplementedError()


def gimp_edit_named_cut(drawable: Drawable, buffer_name: str) -> str:
    """
    Cut into a named buffer.

    This procedure works like 'gimp-edit-cut', but additionally stores the cut buffer into a named buffer that will stay available for later pasting, regardless of any intermediate copy or cut operations.

    :param drawable: The drawable to cut from
    :param buffer_name: The name of the buffer to create
    :return: real_name
    """
    raise NotImplementedError()


def gimp_edit_named_paste(drawable: Drawable, buffer_name: str, paste_into: int) -> Layer:
    """
    Paste named buffer to the specified drawable.

    This procedure works like 'gimp-edit-paste' but pastes a named buffer instead of the global buffer.

    :param drawable: The drawable to paste to
    :param buffer_name: The name of the buffer to paste
    :param paste_into: Clear selection, or paste behind it? (TRUE or FALSE)
    :return: floating_sel
    """
    raise NotImplementedError()


def gimp_edit_named_paste_as_new(buffer_name: str) -> Image:
    """
    Paste named buffer to a new image.

    This procedure works like 'gimp-edit-paste-as-new' but pastes a named buffer instead of the global buffer.

    :param buffer_name: The name of the buffer to paste
    :return: image
    """
    raise NotImplementedError()


def gimp_edit_paste(drawable: Drawable, paste_into: int) -> Layer:
    """
    Paste buffer to the specified drawable.

    This procedure pastes a copy of the internal GIMP edit buffer to the specified drawable. The GIMP edit buffer will be empty unless a call was previously made to either 'gimp-edit-cut' or 'gimp-edit-copy'. The "paste_into" option specifies whether to clear the current image selection, or to paste the buffer "behind" the selection. This allows the selection to act as a mask for the pasted buffer. Anywhere that the selection mask is non-zero, the pasted buffer will show through. The pasted buffer will be a new layer in the image which is designated as the image floating selection. If the image has a floating selection at the time of pasting, the old floating selection will be anchored to it's drawable before the new floating selection is added. This procedure returns the new floating layer. The resulting floating selection will already be attached to the specified drawable, and a subsequent call to floating_sel_attach is not needed.

    :param drawable: The drawable to paste to
    :param paste_into: Clear selection, or paste behind it? (TRUE or FALSE)
    :return: floating_sel
    """
    raise NotImplementedError()


def gimp_edit_paste_as_new() -> Image:
    """
    Paste buffer to a new image.

    This procedure pastes a copy of the internal GIMP edit buffer to a new image. The GIMP edit buffer will be empty unless a call was previously made to either 'gimp-edit-cut' or 'gimp-edit-copy'. This procedure returns the new image or -1 if the edit buffer was empty.
    :return: image
    """
    raise NotImplementedError()


def gimp_edit_stroke(drawable: Drawable):
    """
    Stroke the current selection

    This procedure strokes the current selection, painting along the selection boundary with the active brush and foreground color. The paint is applied to the specified drawable regardless of the active selection.

    :param drawable: The drawable to stroke to
    """
    raise NotImplementedError()


def gimp_edit_stroke_vectors(drawable: Drawable, vectors: Vectors):
    """
    Stroke the specified vectors object

    This procedure strokes the specified vectors object, painting along the path with the active brush and foreground color.

    :param drawable: The drawable to stroke to
    :param vectors: The vectors object
    """
    raise NotImplementedError()


def gimp_ellipse_select(image: Image, x: float, y: float, width: float, height: float, operation: int, antialias: int, feather: int, feather_radius: float):
    """
    Deprecated: Use 'gimp-image-select-ellipse' instead.

    Deprecated: Use 'gimp-image-select-ellipse' instead.

    :param image: The image
    :param x: x coordinate of upper-left corner of ellipse bounding box
    :param y: y coordinate of upper-left corner of ellipse bounding box
    :param width: The width of the ellipse (width >= 0)
    :param height: The height of the ellipse (height >= 0)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius: Radius for feather operation (feather-radius >= 0)
    """
    raise NotImplementedError()


def gimp_equalize(drawable: Drawable, mask_only: int):
    """
    Equalize the contents of the specified drawable.

    This procedure equalizes the contents of the specified drawable. Each intensity channel is equalized independently. The equalized intensity is given as inten' = (255 - inten). Indexed color drawables are not valid for this operation. The 'mask_only' option specifies whether to adjust only the area of the image within the selection bounds, or the entire image based on the histogram of the selected area. If there is no selection, the entire image is adjusted based on the histogram for the entire image.

    :param drawable: The drawable
    :param mask_only: Equalization option (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_eraser(drawable: Drawable, num_strokes: int, strokes: List[float], hardness: int, method: int):
    """
    Erase using the current brush.

    This tool erases using the current brush mask. If the specified drawable contains an alpha channel, then the erased pixels will become transparent. Otherwise, the eraser tool replaces the contents of the drawable with the background color. Like paintbrush, this tool linearly interpolates between the specified stroke coordinates.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    :param hardness: How to apply the brush { BRUSH-HARD (0), BRUSH-SOFT (1) }
    :param method: The paint method to use { PAINT-CONSTANT (0), PAINT-INCREMENTAL (1) }
    """
    raise NotImplementedError()


def gimp_eraser_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Erase using the current brush.

    This tool erases using the current brush mask. This function performs exactly the same as the 'gimp-eraser' function except that the tools arguments are obtained from the eraser option dialog. It this dialog has not been activated then the dialogs default values will be used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_file_load(filename: str, raw_filename: str) -> Image:
    """
    Loads an image file by invoking the right load handler.

    This procedure invokes the correct file load handler using magic if possible, and falling back on the file's extension and/or prefix if not. The name of the file to load is typically a full pathname, and the name entered is what the user actually typed before prepending a directory path. The reason for this is that if the user types http://www.xcf/~gimp/ he wants to fetch a URL, and the full pathname will not look like a URL."

    :param filename: The name of the file to load
    :param raw_filename: The name as entered by the user
    :return: image
    """
    raise NotImplementedError()


def gimp_file_load_layer(image: Image, filename: str) -> Layer:
    """
    Loads an image file as a layer for an existing image.

    This procedure behaves like the file-load procedure but opens the specified image as a layer for an existing image. The returned layer needs to be added to the existing image with 'gimp-image-insert-layer'.

    :param image: Destination image
    :param filename: The name of the file to load
    :return: layer
    """
    raise NotImplementedError()


def gimp_file_load_layers(image: Image, filename: str) -> Tuple[int, List[int]]:
    """
    Loads an image file as layers for an existing image.

    This procedure behaves like the file-load procedure but opens the specified image as layers for an existing image. The returned layers needs to be added to the existing image with 'gimp-image-insert-layer'.

    :param image: Destination image
    :param filename: The name of the file to load
    :return: num_layers, layer_ids
    """
    raise NotImplementedError()


def gimp_file_load_thumbnail(filename: str) -> Tuple[int, int, int, List[int]]:
    """
    Loads the thumbnail for a file.

    This procedure tries to load a thumbnail that belongs to the file with the given filename. This name is a full pathname. The returned data is an array of colordepth 3 (RGB), regardless of the image type. Width and height of the thumbnail are also returned. Don't use this function if you need a thumbnail of an already opened image, use 'gimp-image-thumbnail' instead.

    :param filename: The name of the file that owns the thumbnail to load
    :return: width, height, thumb_data_count, thumb_data
    """
    raise NotImplementedError()


def gimp_file_save(image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves a file by extension.

    This procedure invokes the correct file save handler according to the file's extension and/or prefix. The name of the file to save is typically a full pathname, and the name entered is what the user actually typed before prepending a directory path. The reason for this is that if the user types http://www.xcf/~gimp/ she wants to fetch a URL, and the full pathname will not look like a URL.

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param raw_filename: The name as entered by the user
    """
    raise NotImplementedError()


def gimp_file_save_thumbnail(image: Image, filename: str):
    """
    Saves a thumbnail for the given image

    This procedure saves a thumbnail for the given image according to the Free Desktop Thumbnail Managing Standard. The thumbnail is saved so that it belongs to the file with the given filename. This means you have to save the image under this name first, otherwise this procedure will fail. This procedure may become useful if you want to explicitely save a thumbnail with a file.

    :param image: The image
    :param filename: The name of the file the thumbnail belongs to
    """
    raise NotImplementedError()


def gimp_flip(drawable: Drawable, flip_type: int) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-flip-simple' instead.

    Deprecated: Use 'gimp-item-transform-flip-simple' instead.

    :param drawable: The affected drawable
    :param flip_type: Type of flip { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :return: drawable
    """
    raise NotImplementedError()


def gimp_floating_sel_anchor(floating_sel: Layer):
    """
    Anchor the specified floating selection to its associated drawable.

    This procedure anchors the floating selection to its associated drawable. This is similar to merging with a merge type of ClipToBottomLayer. The floating selection layer is no longer valid after this operation.

    :param floating_sel: The floating selection
    """
    raise NotImplementedError()


def gimp_floating_sel_attach(layer: Layer, drawable: Drawable):
    """
    Attach the specified layer as floating to the specified drawable.

    This procedure attaches the layer as floating selection to the drawable.

    :param layer: The layer (is attached as floating selection)
    :param drawable: The drawable (where to attach the floating selection)
    """
    raise NotImplementedError()


def gimp_floating_sel_relax(floating_sel: Layer, undo: int):
    """
    Deprecated: There is no replacement for this procedure.

    Deprecated: There is no replacement for this procedure.

    :param floating_sel: The floating selection
    :param undo:  (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_floating_sel_remove(floating_sel: Layer):
    """
    Remove the specified floating selection from its associated drawable.

    This procedure removes the floating selection completely, without any side effects. The associated drawable is then set to active.

    :param floating_sel: The floating selection
    """
    raise NotImplementedError()


def gimp_floating_sel_rigor(floating_sel: Layer, undo: int):
    """
    Deprecated: There is no replacement for this procedure.

    Deprecated: There is no replacement for this procedure.

    :param floating_sel: The floating selection
    :param undo:  (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_floating_sel_to_layer(floating_sel: Layer):
    """
    Transforms the specified floating selection into a layer.

    This procedure transforms the specified floating selection into a layer with the same offsets and extents. The composited image will look precisely the same, but the floating selection layer will no longer be clipped to the extents of the drawable it was attached to. The floating selection will become the active layer. This procedure will not work if the floating selection has a different base type from the underlying image. This might be the case if the floating selection is above an auxillary channel or a layer mask.

    :param floating_sel: The floating selection
    """
    raise NotImplementedError()


def gimp_fonts_close_popup(font_callback: str):
    """
    Close the font selection dialog.

    This procedure closes an opened font selection dialog.

    :param font_callback: The name of the callback registered for this pop-up
    """
    raise NotImplementedError()


def gimp_fonts_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve the list of loaded fonts.

    This procedure returns a list of the fonts that are currently available.

    :param filter: An optional regular expression used to filter the list
    :return: num_fonts, font_list
    """
    raise NotImplementedError()


def gimp_fonts_popup(font_callback: str, popup_title: str, initial_font: str):
    """
    Invokes the Gimp font selection.

    This procedure opens the font selection dialog.

    :param font_callback: The callback PDB proc to call when font selection is made
    :param popup_title: Title of the font selection dialog
    :param initial_font: The name of the font to set as the first selected
    """
    raise NotImplementedError()


def gimp_fonts_refresh():
    """
    Refresh current fonts. This function always succeeds.

    This procedure retrieves all fonts currently in the user's font path and updates the font dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_fonts_set_popup(font_callback: str, font_name: str):
    """
    Sets the current font in a font selection dialog.

    Sets the current font in a font selection dialog.

    :param font_callback: The name of the callback registered for this pop-up
    :param font_name: The name of the font to set as selected
    """
    raise NotImplementedError()


def gimp_free_select(image: Image, num_segs: int, segs: List[float], operation: int, antialias: int, feather: int, feather_radius: float):
    """
    Deprecated: Use 'gimp-image-select-polygon' instead.

    Deprecated: Use 'gimp-image-select-polygon' instead.

    :param image: The image
    :param num_segs: Number of points (count 1 coordinate as two points) (num-segs >= 2)
    :param segs: Array of points: { p1.x, p1.y, p2.x, p2.y, ..., pn.x, pn.y}
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius: Radius for feather operation (feather-radius >= 0)
    """
    raise NotImplementedError()


def gimp_fuzzy_select(drawable: Drawable, x: float, y: float, threshold: int, operation: int, antialias: int, feather: int, feather_radius: float, sample_merged: int):
    """
    Deprecated: Use 'gimp-image-select-contiguous-color' instead.

    Deprecated: Use 'gimp-image-select-contiguous-color' instead.

    :param drawable: The affected drawable
    :param x: x coordinate of initial seed fill point: (image coordinates)
    :param y: y coordinate of initial seed fill point: (image coordinates)
    :param threshold: Threshold in intensity levels (0 <= threshold <= 255)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius: Radius for feather operation (feather-radius >= 0)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_fuzzy_select_full(drawable: Drawable, x: float, y: float, threshold: int, operation: int, antialias: int, feather: int, feather_radius_x: float, feather_radius_y: float, sample_merged: int, select_transparent: int, select_criterion: int):
    """
    Deprecated: Use 'gimp-image-select-contiguous-color' instead.

    Deprecated: Use 'gimp-image-select-contiguous-color' instead.

    :param drawable: The affected drawable
    :param x: x coordinate of initial seed fill point: (image coordinates)
    :param y: y coordinate of initial seed fill point: (image coordinates)
    :param threshold: Threshold in intensity levels (0 <= threshold <= 255)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius_x: Radius for feather operation in X direction (feather-radius-x >= 0)
    :param feather_radius_y: Radius for feather operation in Y direction (feather-radius-y >= 0)
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param select_transparent: Whether to consider transparent pixels for selection. If TRUE, transparency is considered as a unique selectable color. (TRUE or FALSE)
    :param select_criterion: The criterion used to determine color similarity. SELECT_CRITERION_COMPOSITE is the standard choice. { SELECT-CRITERION-COMPOSITE (0), SELECT-CRITERION-R (1), SELECT-CRITERION-G (2), SELECT-CRITERION-B (3), SELECT-CRITERION-H (4), SELECT-CRITERION-S (5), SELECT-CRITERION-V (6) }
    """
    raise NotImplementedError()


def gimp_get_color_configuration() -> str:
    """
    Get a serialized version of the color management configuration.

    Returns a string that can be deserialized into a GimpColorConfig object representing the current color management configuration.
    :return: config
    """
    raise NotImplementedError()


def gimp_get_default_comment() -> str:
    """
    Get the default image comment as specified in the Preferences.

    Returns a copy of the default image comment.
    :return: comment
    """
    raise NotImplementedError()


def gimp_get_default_unit() -> int:
    """
    Get the default unit (taken from the user's locale).

    Returns the default unit's integer ID.
    :return: unit_id
    """
    raise NotImplementedError()


def gimp_get_module_load_inhibit() -> str:
    """
    Get the list of modules which should not be loaded.

    Returns a copy of the list of modules which should not be loaded.
    :return: load_inhibit
    """
    raise NotImplementedError()


def gimp_get_monitor_resolution() -> Tuple[float, float]:
    """
    Get the monitor resolution as specified in the Preferences.

    Returns the resolution of the monitor in pixels/inch. This value is taken from the Preferences (or the windowing system if this is set in the Preferences) and there's no guarantee for the value to be reasonable.
    :return: xres, yres
    """
    raise NotImplementedError()


def gimp_get_parasite(name: str) -> Parasite:
    """
    Look up a global parasite.

    Finds and returns the global parasite that was previously attached.

    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_get_parasite_list() -> Tuple[int, List[str]]:
    """
    List all parasites.

    Returns a list of all currently attached global parasites.
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_get_path_by_tattoo(image: Image, tattoo: int) -> str:
    """
    Deprecated: Use 'gimp-image-get-vectors-by-tattoo' instead.

    Deprecated: Use 'gimp-image-get-vectors-by-tattoo' instead.

    :param image: The image
    :param tattoo: The tattoo of the required path.
    :return: name
    """
    raise NotImplementedError()


def gimp_get_theme_dir() -> str:
    """
    Get the directory of the current GUI theme.

    Returns a copy of the current GUI theme dir.
    :return: theme_dir
    """
    raise NotImplementedError()


def gimp_getpid() -> int:
    """
    Returns the PID of the host GIMP process.

    This procedure returns the process ID of the currently running GIMP.
    :return: pid
    """
    raise NotImplementedError()


def gimp_gimprc_query(token: str) -> str:
    """
    Queries the gimprc file parser for information on a specified token.

    This procedure is used to locate additional information contained in the gimprc file considered extraneous to the operation of GIMP. Plug-ins that need configuration information can expect it will be stored in the user gimprc file and can use this procedure to retrieve it. This query procedure will return the value associated with the specified token. This corresponds _only_ to entries with the format: (<token> <value>). The value must be a string. Entries not corresponding to this format will cause warnings to be issued on gimprc parsing and will not be queryable.

    :param token: The token to query for
    :return: value
    """
    raise NotImplementedError()


def gimp_gimprc_set(token: str, value: str):
    """
    Sets a gimprc token to a value and saves it in the gimprc.

    This procedure is used to add or change additional information in the gimprc file that is considered extraneous to the operation of GIMP. Plug-ins that need configuration information can use this function to store it, and 'gimp-gimprc-query' to retrieve it. This will accept _only_ string values in UTF-8 encoding.

    :param token: The token to add or modify
    :param value: The value to set the token to
    """
    raise NotImplementedError()


def gimp_gradient_delete(name: str):
    """
    Deletes a gradient

    This procedure deletes a gradient

    :param name: The gradient name
    """
    raise NotImplementedError()


def gimp_gradient_duplicate(name: str) -> str:
    """
    Duplicates a gradient

    This procedure creates an identical gradient by a different name

    :param name: The gradient name
    :return: copy_name
    """
    raise NotImplementedError()


def gimp_gradient_get_custom_samples(name: str, num_samples: int, positions: List[float], reverse: int) -> Tuple[int, List[float]]:
    """
    Sample the spacified gradient in custom positions.

    This procedure samples the active gradient in the specified number of points. The procedure will sample the gradient in the specified positions from the list. The left endpoint of the gradient corresponds to position 0.0, and the right endpoint corresponds to 1.0. The procedure returns a list of floating-point values which correspond to the RGBA values for each sample.

    :param name: The gradient name
    :param num_samples: The number of samples to take (num-samples >= 1)
    :param positions: The list of positions to sample along the gradient
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :return: num_color_samples, color_samples
    """
    raise NotImplementedError()


def gimp_gradient_get_number_of_segments(name: str) -> int:
    """
    Returns the number of segments of the specified gradient

    This procedure returns the number of segments of the specified gradient.

    :param name: The gradient name
    :return: num_segments
    """
    raise NotImplementedError()


def gimp_gradient_get_uniform_samples(name: str, num_samples: int, reverse: int) -> Tuple[int, List[float]]:
    """
    Sample the specified in uniform parts.

    This procedure samples the active gradient in the specified number of uniform parts. It returns a list of floating-point values which correspond to the RGBA values for each sample. The minimum number of samples to take is 2, in which case the returned colors will correspond to the { 0.0, 1.0 } positions in the gradient. For example, if the number of samples is 3, the procedure will return the colors at positions { 0.0, 0.5, 1.0 }.

    :param name: The gradient name
    :param num_samples: The number of samples to take (num-samples >= 2)
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :return: num_color_samples, color_samples
    """
    raise NotImplementedError()


def gimp_gradient_is_editable(name: str) -> int:
    """
    Tests if gradient can be edited

    Returns TRUE if you have permission to change the gradient

    :param name: The gradient name
    :return: editable
    """
    raise NotImplementedError()


def gimp_gradient_new(name: str) -> str:
    """
    Creates a new gradient

    This procedure creates a new, uninitialized gradient

    :param name: The requested name of the new gradient
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_gradient_rename(name: str, new_name: str) -> str:
    """
    Rename a gradient

    This procedure renames a gradient

    :param name: The gradient name
    :param new_name: The new name of the gradient
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_blending_function(name: str, segment: int) -> int:
    """
    Retrieves the gradient segment's blending function

    This procedure retrieves the blending function of the segment at the specified gradient name and segment index.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: blend_func
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_coloring_type(name: str, segment: int) -> int:
    """
    Retrieves the gradient segment's coloring type

    This procedure retrieves the coloring type of the segment at the specified gradient name and segment index.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: coloring_type
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_left_color(name: str, segment: int) -> Tuple[Color, float]:
    """
    Retrieves the left endpoint color of the specified segment

    This procedure retrieves the left endpoint color of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: color, opacity
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_left_pos(name: str, segment: int) -> float:
    """
    Retrieves the left endpoint position of the specified segment

    This procedure retrieves the left endpoint position of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: pos
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_middle_pos(name: str, segment: int) -> float:
    """
    Retrieves the middle point position of the specified segment

    This procedure retrieves the middle point position of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: pos
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_right_color(name: str, segment: int) -> Tuple[Color, float]:
    """
    Retrieves the right endpoint color of the specified segment

    This procedure retrieves the right endpoint color of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: color, opacity
    """
    raise NotImplementedError()


def gimp_gradient_segment_get_right_pos(name: str, segment: int) -> float:
    """
    Retrieves the right endpoint position of the specified segment

    This procedure retrieves the right endpoint position of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :return: pos
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_blend_colors(name: str, start_segment: int, end_segment: int):
    """
    Blend the colors of the segment range.

    This function blends the colors (but not the opacity) of the segments' range of the gradient. Using it, the colors' transition will be uniform across the range.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_blend_opacity(name: str, start_segment: int, end_segment: int):
    """
    Blend the opacity of the segment range.

    This function blends the opacity (but not the colors) of the segments' range of the gradient. Using it, the opacity's transition will be uniform across the range.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_delete(name: str, start_segment: int, end_segment: int):
    """
    Delete the segment range

    This function deletes a segment range.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_flip(name: str, start_segment: int, end_segment: int):
    """
    Flip the segment range

    This function flips a segment range.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_move(name: str, start_segment: int, end_segment: int, delta: float, control_compress: int) -> float:
    """
    Move the position of an entire segment range by a delta.

    This funtions moves the position of an entire segment range by a delta. The actual delta (which is returned) will be limited by the control points of the neighboring segments.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    :param delta: The delta to move the segment range (-1 <= delta <= 1)
    :param control_compress: Whether or not to compress the neighboring segments (TRUE or FALSE)
    :return: final_delta
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_redistribute_handles(name: str, start_segment: int, end_segment: int):
    """
    Uniformly redistribute the segment range's handles

    This function redistributes the handles of the specified segment range of the specified gradient, so they'll be evenly spaced.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_replicate(name: str, start_segment: int, end_segment: int, replicate_times: int):
    """
    Replicate the segment range

    This function replicates a segment range a given number of times. Instead of the original segment range, several smaller scaled copies of it will appear in equal widths.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    :param replicate_times: The number of times to replicate (2 <= replicate-times <= 20)
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_set_blending_function(name: str, start_segment: int, end_segment: int, blending_function: int):
    """
    Change the blending function of a segments range

    This function changes the blending function of a segment range to the specified blending function.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    :param blending_function: The blending function { GRADIENT-SEGMENT-LINEAR (0), GRADIENT-SEGMENT-CURVED (1), GRADIENT-SEGMENT-SINE (2), GRADIENT-SEGMENT-SPHERE-INCREASING (3), GRADIENT-SEGMENT-SPHERE-DECREASING (4) }
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_set_coloring_type(name: str, start_segment: int, end_segment: int, coloring_type: int):
    """
    Change the coloring type of a segments range

    This function changes the coloring type of a segment range to the specified coloring type.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    :param coloring_type: The coloring type { GRADIENT-SEGMENT-RGB (0), GRADIENT-SEGMENT-HSV-CCW (1), GRADIENT-SEGMENT-HSV-CW (2) }
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_split_midpoint(name: str, start_segment: int, end_segment: int):
    """
    Splits each segment in the segment range at midpoint

    This function splits each segment in the segment range at its midpoint.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    """
    raise NotImplementedError()


def gimp_gradient_segment_range_split_uniform(name: str, start_segment: int, end_segment: int, split_parts: int):
    """
    Splits each segment in the segment range uniformly

    This function splits each segment in the segment range uniformly according to the number of times specified by the parameter.

    :param name: The gradient name
    :param start_segment: The index of the first segment to operate on (start-segment >= 0)
    :param end_segment: The index of the last segment to operate on. If negative, the selection will extend to the end of the string.
    :param split_parts: The number of uniform divisions to split each segment to (2 <= split-parts <= 1024)
    """
    raise NotImplementedError()


def gimp_gradient_segment_set_left_color(name: str, segment: int, color: Color, opacity: float):
    """
    Sets the left endpoint color of the specified segment

    This procedure sets the left endpoint color of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :param color: The color to set
    :param opacity: The opacity to set for the endpoint (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_gradient_segment_set_left_pos(name: str, segment: int, pos: float) -> float:
    """
    Sets the left endpoint position of the specified segment

    This procedure sets the left endpoint position of the specified segment of the specified gradient. The final position will be between the position of the middle point to the left to the middle point of the current segement. This procedure returns the final position.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :param pos: The position to set the guidepoint to (0 <= pos <= 1)
    :return: final_pos
    """
    raise NotImplementedError()


def gimp_gradient_segment_set_middle_pos(name: str, segment: int, pos: float) -> float:
    """
    Sets the middle point position of the specified segment

    This procedure sets the middle point position of the specified segment of the specified gradient. The final position will be between the two endpoints of the segment. This procedure returns the final position.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :param pos: The position to set the guidepoint to (0 <= pos <= 1)
    :return: final_pos
    """
    raise NotImplementedError()


def gimp_gradient_segment_set_right_color(name: str, segment: int, color: Color, opacity: float):
    """
    Sets the right endpoint color of the specified segment

    This procedure sets the right endpoint color of the specified segment of the specified gradient.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :param color: The color to set
    :param opacity: The opacity to set for the endpoint (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_gradient_segment_set_right_pos(name: str, segment: int, pos: float) -> float:
    """
    Sets the right endpoint position of the specified segment

    This procedure sets the right endpoint position of the specified segment of the specified gradient. The final position will be between the position of the middle point of the current segment and the middle point of the segment to the right. This procedure returns the final position.

    :param name: The gradient name
    :param segment: The index of the segment within the gradient (segment >= 0)
    :param pos: The position to set the guidepoint to (0 <= pos <= 1)
    :return: final_pos
    """
    raise NotImplementedError()


def gimp_gradients_close_popup(gradient_callback: str):
    """
    Close the gradient selection dialog.

    This procedure closes an opened gradient selection dialog.

    :param gradient_callback: The name of the callback registered for this pop-up
    """
    raise NotImplementedError()


def gimp_gradients_get_active() -> str:
    """
    This procedure is deprecated! Use 'gimp-context-get-gradient' instead.

    This procedure is deprecated! Use 'gimp-context-get-gradient' instead.
    :return: name
    """
    raise NotImplementedError()


def gimp_gradients_get_gradient() -> str:
    """
    This procedure is deprecated! Use 'gimp-context-get-gradient' instead.

    This procedure is deprecated! Use 'gimp-context-get-gradient' instead.
    :return: name
    """
    raise NotImplementedError()


def gimp_gradients_get_gradient_data(name: str, sample_size: int, reverse: int) -> Tuple[str, int, List[float]]:
    """
    Deprecated: Use 'gimp-gradient-get-uniform-samples' instead.

    Deprecated: Use 'gimp-gradient-get-uniform-samples' instead.

    :param name: The gradient name ("" means current active gradient)
    :param sample_size: Size of the sample to return when the gradient is changed (1 <= sample-size <= 10000)
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :return: actual_name, width, grad_data
    """
    raise NotImplementedError()


def gimp_gradients_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve the list of loaded gradients.

    This procedure returns a list of the gradients that are currently loaded. You can later use the 'gimp-context-set-gradient' function to set the active gradient.

    :param filter: An optional regular expression used to filter the list
    :return: num_gradients, gradient_list
    """
    raise NotImplementedError()


def gimp_gradients_popup(gradient_callback: str, popup_title: str, initial_gradient: str, sample_size: int):
    """
    Invokes the Gimp gradients selection.

    This procedure opens the gradient selection dialog.

    :param gradient_callback: The callback PDB proc to call when gradient selection is made
    :param popup_title: Title of the gradient selection dialog
    :param initial_gradient: The name of the gradient to set as the first selected
    :param sample_size: Size of the sample to return when the gradient is changed (1 <= sample-size <= 10000)
    """
    raise NotImplementedError()


def gimp_gradients_refresh():
    """
    Refresh current gradients. This function always succeeds.

    This procedure retrieves all gradients currently in the user's gradient path and updates the gradient dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_gradients_sample_custom(num_samples: int, positions: List[float], reverse: int) -> Tuple[int, List[float]]:
    """
    Deprecated: Use 'gimp-gradient-get-custom-samples' instead.

    Deprecated: Use 'gimp-gradient-get-custom-samples' instead.

    :param num_samples: The number of samples to take (num-samples >= 0)
    :param positions: The list of positions to sample along the gradient
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :return: array_length, color_samples
    """
    raise NotImplementedError()


def gimp_gradients_sample_uniform(num_samples: int, reverse: int) -> Tuple[int, List[float]]:
    """
    Deprecated: Use 'gimp-gradient-get-uniform-samples' instead.

    Deprecated: Use 'gimp-gradient-get-uniform-samples' instead.

    :param num_samples: The number of samples to take (num-samples >= 2)
    :param reverse: Use the reverse gradient (TRUE or FALSE)
    :return: array_length, color_samples
    """
    raise NotImplementedError()


def gimp_gradients_set_active(name: str):
    """
    This procedure is deprecated! Use 'gimp-context-set-gradient' instead.

    This procedure is deprecated! Use 'gimp-context-set-gradient' instead.

    :param name: The name of the gradient
    """
    raise NotImplementedError()


def gimp_gradients_set_gradient(name: str):
    """
    This procedure is deprecated! Use 'gimp-context-set-gradient' instead.

    This procedure is deprecated! Use 'gimp-context-set-gradient' instead.

    :param name: The name of the gradient
    """
    raise NotImplementedError()


def gimp_gradients_set_popup(gradient_callback: str, gradient_name: str):
    """
    Sets the current gradient in a gradient selection dialog.

    Sets the current gradient in a gradient selection dialog.

    :param gradient_callback: The name of the callback registered for this pop-up
    :param gradient_name: The name of the gradient to set as selected
    """
    raise NotImplementedError()


def gimp_heal(drawable: Drawable, src_drawable: Drawable, src_x: float, src_y: float, num_strokes: int, strokes: List[float]):
    """
    Heal from the source to the dest drawable using the current brush

    This tool heals the source drawable starting at the specified source coordinates to the dest drawable. For image healing, if the sum of the src coordinates and subsequent stroke offsets exceeds the extents of the src drawable, then no paint is transferred. The healing tool is capable of transforming between any image types except RGB->Indexed.

    :param drawable: The affected drawable
    :param src_drawable: The source drawable
    :param src_x: The x coordinate in the source image
    :param src_y: The y coordinate in the source image
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_heal_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Heal from the source to the dest drawable using the current brush

    This tool heals from the source drawable starting at the specified source coordinates to the dest drawable. This function performs exactly the same as the 'gimp-heal' function except that the tools arguments are obtained from the healing option dialog. It this dialog has not been activated then the dialogs default values will be used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_help(help_domain: str, help_id: str):
    """
    Load a help page.

    This procedure loads the specified help page into the helpbrowser or what ever is configured as help viewer. The help page is identified by its domain and ID: if help_domain is NULL, we use the help_domain which was registered using the 'gimp-plugin-help-register' procedure. If help_domain is NULL and no help domain was registered, the help domain of the main GIMP installation is used.

    :param help_domain: The help domain in which help_id is registered
    :param help_id: The help page's ID
    """
    raise NotImplementedError()


def gimp_help_concepts_paths():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_concepts_usage():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_docks():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_fileformats():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_photography():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_selections():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_simpleobjects():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_help_using_web():
    """
    Bookmark to the user manual

    """
    raise NotImplementedError()


def gimp_histogram(drawable: Drawable, channel: int, start_range: int, end_range: int) -> Tuple[float, float, float, float, float, float]:
    """
    Returns information on the intensity histogram for the specified drawable.

    This tool makes it possible to gather information about the intensity histogram of a drawable. A channel to examine is first specified. This can be either value, red, green, or blue, depending on whether the drawable is of type color or grayscale. The drawable may not be indexed. Second, a range of intensities are specified. The 'gimp-histogram' function returns statistics based on the pixels in the drawable that fall under this range of values. Mean, standard deviation, median, number of pixels, and percentile are all returned. Additionally, the total count of pixels in the image is returned. Counts of pixels are weighted by any associated alpha values and by the current selection mask. That is, pixels that lie outside an active selection mask will not be counted. Similarly, pixels with transparent alpha values will not be counted.

    :param drawable: The drawable
    :param channel: The channel to modify { HISTOGRAM-VALUE (0), HISTOGRAM-RED (1), HISTOGRAM-GREEN (2), HISTOGRAM-BLUE (3), HISTOGRAM-ALPHA (4), HISTOGRAM-RGB (5) }
    :param start_range: Start of the intensity measurement range (0 <= start-range <= 255)
    :param end_range: End of the intensity measurement range (0 <= end-range <= 255)
    :return: mean, std_dev, median, pixels, count, percentile
    """
    raise NotImplementedError()


def gimp_hue_saturation(drawable: Drawable, hue_range: int, hue_offset: float, lightness: float, saturation: float):
    """
    Modify hue, lightness, and saturation in the specified drawable.

    This procedures allows the hue, lightness, and saturation in the specified drawable to be modified. The 'hue-range' parameter provides the capability to limit range of affected hues.

    :param drawable: The drawable
    :param hue_range: Range of affected hues { ALL-HUES (0), RED-HUES (1), YELLOW-HUES (2), GREEN-HUES (3), CYAN-HUES (4), BLUE-HUES (5), MAGENTA-HUES (6) }
    :param hue_offset: Hue offset in degrees (-180 <= hue-offset <= 180)
    :param lightness: Lightness modification (-100 <= lightness <= 100)
    :param saturation: Saturation modification (-100 <= saturation <= 100)
    """
    raise NotImplementedError()


def gimp_image_active_drawable(image: Image) -> Drawable:
    """
    This procedure is deprecated! Use 'gimp-image-get-active-drawable' instead.

    This procedure is deprecated! Use 'gimp-image-get-active-drawable' instead.

    :param image: The image
    :return: drawable
    """
    raise NotImplementedError()


def gimp_image_add_channel(image: Image, channel: Channel, position: int):
    """
    Deprecated: Use 'gimp-image-insert-channel' instead.

    Deprecated: Use 'gimp-image-insert-channel' instead.

    :param image: The image
    :param channel: The channel
    :param position: The channel position
    """
    raise NotImplementedError()


def gimp_image_add_hguide(image: Image, yposition: int) -> int:
    """
    Add a horizontal guide to an image.

    This procedure adds a horizontal guide to an image. It takes the input image and the y-position of the new guide as parameters. It returns the guide ID of the new guide.

    :param image: The image
    :param yposition: The guide's y-offset from top of image (yposition >= 0)
    :return: guide
    """
    raise NotImplementedError()


def gimp_image_add_layer(image: Image, layer: Layer, position: int):
    """
    Deprecated: Use 'gimp-image-insert-layer' instead.

    Deprecated: Use 'gimp-image-insert-layer' instead.

    :param image: The image
    :param layer: The layer
    :param position: The layer position
    """
    raise NotImplementedError()


def gimp_image_add_layer_mask(image: Image, layer: Layer, mask: Channel):
    """
    Deprecated: Use 'gimp-layer-add-mask' instead.

    Deprecated: Use 'gimp-layer-add-mask' instead.

    :param image: The image
    :param layer: The layer to receive the mask
    :param mask: The mask to add to the layer
    """
    raise NotImplementedError()


def gimp_image_add_vectors(image: Image, vectors: Vectors, position: int):
    """
    Deprecated: Use 'gimp-image-insert-vectors' instead.

    Deprecated: Use 'gimp-image-insert-vectors' instead.

    :param image: The image
    :param vectors: The vectors object
    :param position: The vectors objects position
    """
    raise NotImplementedError()


def gimp_image_add_vguide(image: Image, xposition: int) -> int:
    """
    Add a vertical guide to an image.

    This procedure adds a vertical guide to an image. It takes the input image and the x-position of the new guide as parameters. It returns the guide ID of the new guide.

    :param image: The image
    :param xposition: The guide's x-offset from left of image (xposition >= 0)
    :return: guide
    """
    raise NotImplementedError()


def gimp_image_attach_parasite(image: Image, parasite: Parasite):
    """
    Add a parasite to an image.

    This procedure attaches a parasite to an image. It has no return values.

    :param image: The image
    :param parasite: The parasite to attach to an image
    """
    raise NotImplementedError()


def gimp_image_base_type(image: Image) -> int:
    """
    Get the base type of the image.

    This procedure returns the image's base type. Layers in the image must be of this subtype, but can have an optional alpha channel.

    :param image: The image
    :return: base_type
    """
    raise NotImplementedError()


def gimp_image_clean_all(image: Image):
    """
    Set the image dirty count to 0.

    This procedure sets the specified image's dirty count to 0, allowing operations to occur without having a 'dirtied' image. This is especially useful for creating and loading images which should not initially be considered dirty, even though layers must be created, filled, and installed in the image. Note that save plug-ins must NOT call this function themselves after saving the image.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_convert_grayscale(image: Image):
    """
    Convert specified image to grayscale (256 intensity levels)

    This procedure converts the specified image to grayscale with 8 bits per pixel (256 intensity levels). This process requires an image in RGB or Indexed color mode.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_convert_indexed(image: Image, dither_type: int, palette_type: int, num_cols: int, alpha_dither: int, remove_unused: int, palette: str):
    """
    Convert specified image to and Indexed image

    This procedure converts the specified image to 'indexed' color. This process requires an image in RGB or Grayscale mode. The 'palette_type' specifies what kind of palette to use, A type of '0' means to use an optimal palette of 'num_cols' generated from the colors in the image. A type of '1' means to re-use the previous palette (not currently implemented). A type of '2' means to use the so-called WWW-optimized palette. Type '3' means to use only black and white colors. A type of '4' means to use a palette from the gimp palettes directories. The 'dither type' specifies what kind of dithering to use. '0' means no dithering, '1' means standard Floyd-Steinberg error diffusion, '2' means Floyd-Steinberg error diffusion with reduced bleeding, '3' means dithering based on pixel location ('Fixed' dithering).

    :param image: The image
    :param dither_type: The dither type to use { NO-DITHER (0), FS-DITHER (1), FSLOWBLEED-DITHER (2), FIXED-DITHER (3) }
    :param palette_type: The type of palette to use { MAKE-PALETTE (0), WEB-PALETTE (2), MONO-PALETTE (3), CUSTOM-PALETTE (4) }
    :param num_cols: The number of colors to quantize to, ignored unless (palette_type == GIMP_MAKE_PALETTE)
    :param alpha_dither: Dither transparency to fake partial opacity (TRUE or FALSE)
    :param remove_unused: Remove unused or duplicate color entries from final palette, ignored if (palette_type == GIMP_MAKE_PALETTE) (TRUE or FALSE)
    :param palette: The name of the custom palette to use, ignored unless (palette_type == GIMP_CUSTOM_PALETTE)
    """
    raise NotImplementedError()


def gimp_image_convert_rgb(image: Image):
    """
    Convert specified image to RGB color

    This procedure converts the specified image to RGB color. This process requires an image in Grayscale or Indexed color mode. No image content is lost in this process aside from the colormap for an indexed image.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_convert_set_dither_matrix(width: int, height: int, matrix_length: int, matrix: List[int]):
    """
    Set dither matrix for conversion to indexed

    This procedure sets the dither matrix used when converting images to INDEXED mode with positional dithering.

    :param width: Width of the matrix (0 to reset to default matrix)
    :param height: Height of the matrix (0 to reset to default matrix)
    :param matrix_length: The length of 'matrix' (1 <= matrix-length <= 1024)
    :param matrix: The matrix -- all values must be >= 1
    """
    raise NotImplementedError()


def gimp_image_crop(image: Image, new_width: int, new_height: int, offx: int, offy: int):
    """
    Crop the image to the specified extents.

    This procedure crops the image so that it's new width and height are equal to the supplied parameters. Offsets are also provided which describe the position of the previous image's content. All channels and layers within the image are cropped to the new image extents; this includes the image selection mask. If any parameters are out of range, an error is returned.

    :param image: The image
    :param new_width: New image width: (0 < new_width <= width) (1 <= new-width <= 262144)
    :param new_height: New image height: (0 < new_height <= height) (1 <= new-height <= 262144)
    :param offx: X offset: (0 <= offx <= (width - new_width)) (offx >= 0)
    :param offy: Y offset: (0 <= offy <= (height - new_height)) (offy >= 0)
    """
    raise NotImplementedError()


def gimp_image_delete(image: Image):
    """
    Delete the specified image.

    If there are no displays associated with this image it will be deleted. This means that you can not delete an image through the PDB that was created by the user. If the associated display was however created through the PDB and you know the display ID, you may delete the display. Removal of the last associated display will then delete the image.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_delete_guide(image: Image, guide: int):
    """
    Deletes a guide from an image.

    This procedure takes an image and a guide ID as input and removes the specified guide from the specified image.

    :param image: The image
    :param guide: The ID of the guide to be removed
    """
    raise NotImplementedError()


def gimp_image_detach_parasite(image: Image, name: str):
    """
    Removes a parasite from an image.

    This procedure detaches a parasite from an image. It has no return values.

    :param image: The image
    :param name: The name of the parasite to detach from an image.
    """
    raise NotImplementedError()


def gimp_image_duplicate(image: Image) -> Image:
    """
    Duplicate the specified image

    This procedure duplicates the specified image, copying all layers, channels, and image information.

    :param image: The image
    :return: new_image
    """
    raise NotImplementedError()


def gimp_image_find_next_guide(image: Image, guide: int) -> int:
    """
    Find next guide on an image.

    This procedure takes an image and a guide ID as input and finds the guide ID of the successor of the given guide ID in the image's guide list. If the supplied guide ID is 0, the procedure will return the first Guide. The procedure will return 0 if given the final guide ID as an argument or the image has no guides.

    :param image: The image
    :param guide: The ID of the current guide (0 if first invocation)
    :return: next_guide
    """
    raise NotImplementedError()


def gimp_image_flatten(image: Image) -> Layer:
    """
    Flatten all visible layers into a single layer. Discard all invisible layers.

    This procedure combines the visible layers in a manner analogous to merging with the CLIP_TO_IMAGE merge type. Non-visible layers are discarded, and the resulting image is stripped of its alpha channel.

    :param image: The image
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_flip(image: Image, flip_type: int):
    """
    Flips the image horizontally or vertically.

    This procedure flips (mirrors) the image.

    :param image: The image
    :param flip_type: Type of flip { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    """
    raise NotImplementedError()


def gimp_image_floating_sel_attached_to(image: Image) -> Drawable:
    """
    Return the drawable the floating selection is attached to.

    This procedure returns the drawable the image's floating selection is attached to, if it exists. If it doesn't exist, -1 is returned as the drawable ID.

    :param image: The image
    :return: drawable
    """
    raise NotImplementedError()


def gimp_image_floating_selection(image: Image) -> Layer:
    """
    This procedure is deprecated! Use 'gimp-image-get-floating-sel' instead.

    This procedure is deprecated! Use 'gimp-image-get-floating-sel' instead.

    :param image: The image
    :return: floating_sel
    """
    raise NotImplementedError()


def gimp_image_free_shadow(image: Image):
    """
    Deprecated: Use 'gimp-drawable-free-shadow' instead.

    Deprecated: Use 'gimp-drawable-free-shadow' instead.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_get_active_channel(image: Image) -> Channel:
    """
    Returns the specified image's active channel.

    If there is an active channel, this will return the channel ID, otherwise, -1.

    :param image: The image
    :return: active_channel
    """
    raise NotImplementedError()


def gimp_image_get_active_drawable(image: Image) -> Drawable:
    """
    Get the image's active drawable

    This procedure returns the ID of the image's active drawable. This can be either a layer, a channel, or a layer mask. The active drawable is specified by the active image channel. If that is -1, then by the active image layer. If the active image layer has a layer mask and the layer mask is in edit mode, then the layer mask is the active drawable.

    :param image: The image
    :return: drawable
    """
    raise NotImplementedError()


def gimp_image_get_active_layer(image: Image) -> Layer:
    """
    Returns the specified image's active layer.

    If there is an active layer, its ID will be returned, otherwise, -1. If a channel is currently active, then no layer will be. If a layer mask is active, then this will return the associated layer.

    :param image: The image
    :return: active_layer
    """
    raise NotImplementedError()


def gimp_image_get_active_vectors(image: Image) -> Vectors:
    """
    Returns the specified image's active vectors.

    If there is an active path, its ID will be returned, otherwise, -1.

    :param image: The image
    :return: active_vectors
    """
    raise NotImplementedError()


def gimp_image_get_channel_by_name(image: Image, name: str) -> Channel:
    """
    Find a channel with a given name in an image.

    This procedure returns the channel with the given name in the specified image.

    :param image: The image
    :param name: The name of the channel to find
    :return: channel
    """
    raise NotImplementedError()


def gimp_image_get_channel_by_tattoo(image: Image, tattoo: int) -> Channel:
    """
    Find a channel with a given tattoo in an image.

    This procedure returns the channel with the given tattoo in the specified image.

    :param image: The image
    :param tattoo: The tattoo of the channel to find
    :return: channel
    """
    raise NotImplementedError()


def gimp_image_get_channel_position(image: Image, item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    :param image: The image
    :param item: The item
    :return: position
    """
    raise NotImplementedError()


def gimp_image_get_channels(image: Image) -> Tuple[int, List[int]]:
    """
    Returns the list of channels contained in the specified image.

    This procedure returns the list of channels contained in the specified image. This does not include the selection mask, or layer masks. The order is from topmost to bottommost.

    :param image: The image
    :return: num_channels, channel_ids
    """
    raise NotImplementedError()


def gimp_image_get_cmap(image: Image) -> Tuple[int, List[int]]:
    """
    This procedure is deprecated! Use 'gimp-image-get-colormap' instead.

    This procedure is deprecated! Use 'gimp-image-get-colormap' instead.

    :param image: The image
    :return: num_bytes, colormap
    """
    raise NotImplementedError()


def gimp_image_get_colormap(image: Image) -> Tuple[int, List[int]]:
    """
    Returns the image's colormap

    This procedure returns an actual pointer to the image's colormap, as well as the number of bytes contained in the colormap. The actual number of colors in the transmitted colormap will be 'num-bytes' / 3. If the image is not in Indexed color mode, no colormap is returned.

    :param image: The image
    :return: num_bytes, colormap
    """
    raise NotImplementedError()


def gimp_image_get_component_active(image: Image, component: int) -> int:
    """
    Returns if the specified image's image component is active.

    This procedure returns if the specified image's image component (i.e. Red, Green, Blue intensity channels in an RGB image) is active or inactive -- whether or not it can be modified. If the specified component is not valid for the image type, an error is returned.

    :param image: The image
    :param component: The image component { RED-CHANNEL (0), GREEN-CHANNEL (1), BLUE-CHANNEL (2), GRAY-CHANNEL (3), INDEXED-CHANNEL (4), ALPHA-CHANNEL (5) }
    :return: active
    """
    raise NotImplementedError()


def gimp_image_get_component_visible(image: Image, component: int) -> int:
    """
    Returns if the specified image's image component is visible.

    This procedure returns if the specified image's image component (i.e. Red, Green, Blue intensity channels in an RGB image) is visible or invisible -- whether or not it can be seen. If the specified component is not valid for the image type, an error is returned.

    :param image: The image
    :param component: The image component { RED-CHANNEL (0), GREEN-CHANNEL (1), BLUE-CHANNEL (2), GRAY-CHANNEL (3), INDEXED-CHANNEL (4), ALPHA-CHANNEL (5) }
    :return: visible
    """
    raise NotImplementedError()


def gimp_image_get_exported_uri(image: Image) -> str:
    """
    Returns the exported URI for the specified image.

    This procedure returns the URI associated with the specified image if the image was exported a non-native GIMP format. If the image was not exported, this procedure returns %NULL.

    :param image: The image
    :return: uri
    """
    raise NotImplementedError()


def gimp_image_get_filename(image: Image) -> str:
    """
    Returns the specified image's filename.

    This procedure returns the specified image's filename in the filesystem encoding. The image has a filename only if it was loaded or imported from a file or has since been saved or exported. Otherwise, this function returns %NULL. See also 'gimp-image-get-uri'.

    :param image: The image
    :return: filename
    """
    raise NotImplementedError()


def gimp_image_get_floating_sel(image: Image) -> Layer:
    """
    Return the floating selection of the image.

    This procedure returns the image's floating selection, if it exists. If it doesn't exist, -1 is returned as the layer ID.

    :param image: The image
    :return: floating_sel
    """
    raise NotImplementedError()


def gimp_image_get_guide_orientation(image: Image, guide: int) -> int:
    """
    Get orientation of a guide on an image.

    This procedure takes an image and a guide ID as input and returns the orientations of the guide.

    :param image: The image
    :param guide: The guide
    :return: orientation
    """
    raise NotImplementedError()


def gimp_image_get_guide_position(image: Image, guide: int) -> int:
    """
    Get position of a guide on an image.

    This procedure takes an image and a guide ID as input and returns the position of the guide relative to the top or left of the image.

    :param image: The image
    :param guide: The guide
    :return: position
    """
    raise NotImplementedError()


def gimp_image_get_imported_uri(image: Image) -> str:
    """
    Returns the imported URI for the specified image.

    This procedure returns the URI associated with the specified image if the image was imported from a non-native Gimp format. If the image was not imported, or has since been saved in the native Gimp format, this procedure returns %NULL.

    :param image: The image
    :return: uri
    """
    raise NotImplementedError()


def gimp_image_get_item_position(image: Image, item: Item) -> int:
    """
    Returns the position of the item in its level of its item tree.

    This procedure determines the position of the specified item in its level in its item tree in the image. If the item doesn't exist in the image, or the item is not part of an item tree, an error is returned.

    :param image: The image
    :param item: The item
    :return: position
    """
    raise NotImplementedError()


def gimp_image_get_layer_by_name(image: Image, name: str) -> Layer:
    """
    Find a layer with a given name in an image.

    This procedure returns the layer with the given name in the specified image.

    :param image: The image
    :param name: The name of the layer to find
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_get_layer_by_tattoo(image: Image, tattoo: int) -> Layer:
    """
    Find a layer with a given tattoo in an image.

    This procedure returns the layer with the given tattoo in the specified image.

    :param image: The image
    :param tattoo: The tattoo of the layer to find
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_get_layer_position(image: Image, item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    :param image: The image
    :param item: The item
    :return: position
    """
    raise NotImplementedError()


def gimp_image_get_layers(image: Image) -> Tuple[int, List[int]]:
    """
    Returns the list of layers contained in the specified image.

    This procedure returns the list of layers contained in the specified image. The order of layers is from topmost to bottommost.

    :param image: The image
    :return: num_layers, layer_ids
    """
    raise NotImplementedError()


def gimp_image_get_name(image: Image) -> str:
    """
    Returns the specified image's name.

    This procedure returns the image's name. If the image has a filename or an URI, then the returned name contains the filename's or URI's base name (the last component of the path). Otherwise it is the translated string "Untitled". The returned name is formatted like the image name in the image window title, it may contain '[]', '(imported)' etc. and should only be used to label user interface elements. Never use it to construct filenames.

    :param image: The image
    :return: name
    """
    raise NotImplementedError()


def gimp_image_get_parasite(image: Image, name: str) -> Parasite:
    """
    Look up a parasite in an image

    Finds and returns the parasite that was previously attached to an image.

    :param image: The image
    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_image_get_parasite_list(image: Image) -> Tuple[int, List[str]]:
    """
    List all parasites.

    Returns a list of all currently attached parasites.

    :param image: The image
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_image_get_resolution(image: Image) -> Tuple[float, float]:
    """
    Returns the specified image's resolution.

    This procedure returns the specified image's resolution in dots per inch. This value is independent of any of the layers in this image.

    :param image: The image
    :return: xresolution, yresolution
    """
    raise NotImplementedError()


def gimp_image_get_selection(image: Image) -> Selection:
    """
    Returns the specified image's selection.

    This will always return a valid ID for a selection -- which is represented as a channel internally.

    :param image: The image
    :return: selection
    """
    raise NotImplementedError()


def gimp_image_get_tattoo_state(image: Image) -> int:
    """
    Returns the tattoo state associated with the image.

    This procedure returns the tattoo state of the image. Use only by save/load plugins that wish to preserve an images tattoo state. Using this function at other times will produce unexpected results.

    :param image: The image
    :return: tattoo_state
    """
    raise NotImplementedError()


def gimp_image_get_unit(image: Image) -> int:
    """
    Returns the specified image's unit.

    This procedure returns the specified image's unit. This value is independent of any of the layers in this image. See the gimp_unit_*() procedure definitions for the valid range of unit IDs and a description of the unit system.

    :param image: The image
    :return: unit
    """
    raise NotImplementedError()


def gimp_image_get_uri(image: Image) -> str:
    """
    Returns the URI for the specified image.

    This procedure returns the URI associated with the specified image. The image has an URI only if it was loaded or imported from a file or has since been saved or exported. Otherwise, this function returns %NULL. See also gimp-image-get-imported-uri to get the URI of the current file if it was imported from a non-GIMP file format and not yet saved, or gimp-image-get-exported-uri if the image has been exported to a non-GIMP file format.

    :param image: The image
    :return: uri
    """
    raise NotImplementedError()


def gimp_image_get_vectors(image: Image) -> Tuple[int, List[int]]:
    """
    Returns the list of vectors contained in the specified image.

    This procedure returns the list of vectors contained in the specified image.

    :param image: The image
    :return: num_vectors, vector_ids
    """
    raise NotImplementedError()


def gimp_image_get_vectors_by_name(image: Image, name: str) -> Vectors:
    """
    Find a vectors with a given name in an image.

    This procedure returns the vectors with the given name in the specified image.

    :param image: The image
    :param name: The name of the vectors to find
    :return: vectors
    """
    raise NotImplementedError()


def gimp_image_get_vectors_by_tattoo(image: Image, tattoo: int) -> Vectors:
    """
    Find a vectors with a given tattoo in an image.

    This procedure returns the vectors with the given tattoo in the specified image.

    :param image: The image
    :param tattoo: The tattoo of the vectors to find
    :return: vectors
    """
    raise NotImplementedError()


def gimp_image_get_vectors_position(image: Image, item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    This procedure is deprecated! Use 'gimp-image-get-item-position' instead.

    :param image: The image
    :param item: The item
    :return: position
    """
    raise NotImplementedError()


def gimp_image_get_xcf_uri(image: Image) -> str:
    """
    Returns the XCF URI for the specified image.

    This procedure returns the XCF URI associated with the image. If there is no such URI, this procedure returns %NULL.

    :param image: The image
    :return: uri
    """
    raise NotImplementedError()


def gimp_image_grid_get_background_color(image: Image) -> Color:
    """
    Sets the background color of an image's grid.

    This procedure gets the background color of an image's grid.

    :param image: The image
    :return: bgcolor
    """
    raise NotImplementedError()


def gimp_image_grid_get_foreground_color(image: Image) -> Color:
    """
    Sets the foreground color of an image's grid.

    This procedure gets the foreground color of an image's grid.

    :param image: The image
    :return: fgcolor
    """
    raise NotImplementedError()


def gimp_image_grid_get_offset(image: Image) -> Tuple[float, float]:
    """
    Gets the offset of an image's grid.

    This procedure retrieves the horizontal and vertical offset of an image's grid. It takes the image as parameter.

    :param image: The image
    :return: xoffset, yoffset
    """
    raise NotImplementedError()


def gimp_image_grid_get_spacing(image: Image) -> Tuple[float, float]:
    """
    Gets the spacing of an image's grid.

    This procedure retrieves the horizontal and vertical spacing of an image's grid. It takes the image as parameter.

    :param image: The image
    :return: xspacing, yspacing
    """
    raise NotImplementedError()


def gimp_image_grid_get_style(image: Image) -> int:
    """
    Gets the style of an image's grid.

    This procedure retrieves the style of an image's grid.

    :param image: The image
    :return: style
    """
    raise NotImplementedError()


def gimp_image_grid_set_background_color(image: Image, bgcolor: Color):
    """
    Gets the background color of an image's grid.

    This procedure sets the background color of an image's grid.

    :param image: The image
    :param bgcolor: The new background color
    """
    raise NotImplementedError()


def gimp_image_grid_set_foreground_color(image: Image, fgcolor: Color):
    """
    Gets the foreground color of an image's grid.

    This procedure sets the foreground color of an image's grid.

    :param image: The image
    :param fgcolor: The new foreground color
    """
    raise NotImplementedError()


def gimp_image_grid_set_offset(image: Image, xoffset: float, yoffset: float):
    """
    Sets the offset of an image's grid.

    This procedure sets the horizontal and vertical offset of an image's grid.

    :param image: The image
    :param xoffset: The image's grid horizontal offset
    :param yoffset: The image's grid vertical offset
    """
    raise NotImplementedError()


def gimp_image_grid_set_spacing(image: Image, xspacing: float, yspacing: float):
    """
    Sets the spacing of an image's grid.

    This procedure sets the horizontal and vertical spacing of an image's grid.

    :param image: The image
    :param xspacing: The image's grid horizontal spacing
    :param yspacing: The image's grid vertical spacing
    """
    raise NotImplementedError()


def gimp_image_grid_set_style(image: Image, style: int):
    """
    Sets the style unit of an image's grid.

    This procedure sets the style of an image's grid. It takes the image and the new style as parameters.

    :param image: The image
    :param style: The image's grid style { GRID-DOTS (0), GRID-INTERSECTIONS (1), GRID-ON-OFF-DASH (2), GRID-DOUBLE-DASH (3), GRID-SOLID (4) }
    """
    raise NotImplementedError()


def gimp_image_height(image: Image) -> int:
    """
    Return the height of the image

    This procedure returns the image's height. This value is independent of any of the layers in this image. This is the "canvas" height.

    :param image: The image
    :return: height
    """
    raise NotImplementedError()


def gimp_image_insert_channel(image: Image, channel: Channel, parent: Channel, position: int):
    """
    Add the specified channel to the image.

    This procedure adds the specified channel to the image at the given position. Since channel groups are not currently supported, the parent argument must always be 0. The position argument specifies the location of the channel inside the stack, starting from the top (0) and increasing. If the position is specified as -1, then the channel is inserted above the active channel.

    :param image: The image
    :param channel: The channel
    :param parent: The parent channel
    :param position: The channel position
    """
    raise NotImplementedError()


def gimp_image_insert_layer(image: Image, layer: Layer, parent: Layer, position: int):
    """
    Add the specified layer to the image.

    This procedure adds the specified layer to the image at the given position. If the specified parent is a valid layer group (See 'gimp-item-is-group' and 'gimp-layer-group-new') then the layer is added inside the group. If the parent is 0, the layer is added inside the main stack, outside of any group. The position argument specifies the location of the layer inside the stack (or the group, if a valid parent was supplied), starting from the top (0) and increasing. If the position is specified as -1 and the parent is specified as 0, then the layer is inserted above the active layer, or inside the group if the active layer is a layer group. The layer type must be compatible with the image base type.

    :param image: The image
    :param layer: The layer
    :param parent: The parent layer
    :param position: The layer position
    """
    raise NotImplementedError()


def gimp_image_insert_vectors(image: Image, vectors: Vectors, parent: Vectors, position: int):
    """
    Add the specified vectors to the image.

    This procedure adds the specified vectors to the image at the given position. Since vectors groups are not currently supported, the parent argument must always be 0. The position argument specifies the location of the vectors inside the stack, starting from the top (0) and increasing. If the position is specified as -1, then the vectors is inserted above the active vectors.

    :param image: The image
    :param vectors: The vectors
    :param parent: The parent vectors
    :param position: The vectors position
    """
    raise NotImplementedError()


def gimp_image_is_dirty(image: Image) -> int:
    """
    Checks if the image has unsaved changes.

    This procedure checks the specified image's dirty count to see if it needs to be saved. Note that saving the image does not automatically set the dirty count to 0, you need to call 'gimp-image-clean-all' after calling a save procedure to make the image clean.

    :param image: The image
    :return: dirty
    """
    raise NotImplementedError()


def gimp_image_is_valid(image: Image) -> int:
    """
    Returns TRUE if the image is valid.

    This procedure checks if the given image ID is valid and refers to an existing image.

    :param image: The image to check
    :return: valid
    """
    raise NotImplementedError()


def gimp_image_list() -> Tuple[int, List[int]]:
    """
    Returns the list of images currently open.

    This procedure returns the list of images currently open in GIMP.
    :return: num_images, image_ids
    """
    raise NotImplementedError()


def gimp_image_lower_channel(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    :param image: The image
    :param item: The item to lower
    """
    raise NotImplementedError()


def gimp_image_lower_item(image: Image, item: Item):
    """
    Lower the specified item in its level in its item tree

    This procedure lowers the specified item one step in the item tree. The procecure call will fail if there is no item below it.

    :param image: The image
    :param item: The item to lower
    """
    raise NotImplementedError()


def gimp_image_lower_item_to_bottom(image: Image, item: Item):
    """
    Lower the specified item to the bottom of its level in its item tree

    This procedure lowers the specified item to bottom of its level in the item tree. It will not move the layer if there is no layer below it.

    :param image: The image
    :param item: The item to lower to bottom
    """
    raise NotImplementedError()


def gimp_image_lower_layer(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    :param image: The image
    :param item: The item to lower
    """
    raise NotImplementedError()


def gimp_image_lower_layer_to_bottom(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-lower-item-to-bottom' instead.

    This procedure is deprecated! Use 'gimp-image-lower-item-to-bottom' instead.

    :param image: The image
    :param item: The item to lower to bottom
    """
    raise NotImplementedError()


def gimp_image_lower_vectors(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    This procedure is deprecated! Use 'gimp-image-lower-item' instead.

    :param image: The image
    :param item: The item to lower
    """
    raise NotImplementedError()


def gimp_image_lower_vectors_to_bottom(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-lower-item-to-bottom' instead.

    This procedure is deprecated! Use 'gimp-image-lower-item-to-bottom' instead.

    :param image: The image
    :param item: The item to lower to bottom
    """
    raise NotImplementedError()


def gimp_image_merge_down(image: Image, merge_layer: Layer, merge_type: int) -> Layer:
    """
    Merge the layer passed and the first visible layer below.

    This procedure combines the passed layer and the first visible layer below it using the specified merge type. A merge type of EXPAND_AS_NECESSARY expands the final layer to encompass the areas of the visible layers. A merge type of CLIP_TO_IMAGE clips the final layer to the extents of the image. A merge type of CLIP_TO_BOTTOM_LAYER clips the final layer to the size of the bottommost layer.

    :param image: The image
    :param merge_layer: The layer to merge down from
    :param merge_type: The type of merge { EXPAND-AS-NECESSARY (0), CLIP-TO-IMAGE (1), CLIP-TO-BOTTOM-LAYER (2) }
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_merge_visible_layers(image: Image, merge_type: int) -> Layer:
    """
    Merge the visible image layers into one.

    This procedure combines the visible layers into a single layer using the specified merge type. A merge type of EXPAND_AS_NECESSARY expands the final layer to encompass the areas of the visible layers. A merge type of CLIP_TO_IMAGE clips the final layer to the extents of the image. A merge type of CLIP_TO_BOTTOM_LAYER clips the final layer to the size of the bottommost layer.

    :param image: The image
    :param merge_type: The type of merge { EXPAND-AS-NECESSARY (0), CLIP-TO-IMAGE (1), CLIP-TO-BOTTOM-LAYER (2) }
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_new(width: int, height: int, type: int) -> Image:
    """
    Creates a new image with the specified width, height, and type.

    Creates a new image, undisplayed with the specified extents and type. A layer should be created and added before this image is displayed, or subsequent calls to 'gimp-display-new' with this image as an argument will fail. Layers can be created using the 'gimp-layer-new' commands. They can be added to an image using the 'gimp-image-insert-layer' command.

    :param width: The width of the image (1 <= width <= 262144)
    :param height: The height of the image (1 <= height <= 262144)
    :param type: The type of image { RGB (0), GRAY (1), INDEXED (2) }
    :return: image
    """
    raise NotImplementedError()


def gimp_image_parasite_attach(image: Image, parasite: Parasite):
    """
    This procedure is deprecated! Use 'gimp-image-attach-parasite' instead.

    This procedure is deprecated! Use 'gimp-image-attach-parasite' instead.

    :param image: The image
    :param parasite: The parasite to attach to an image
    """
    raise NotImplementedError()


def gimp_image_parasite_detach(image: Image, name: str):
    """
    This procedure is deprecated! Use 'gimp-image-detach-parasite' instead.

    This procedure is deprecated! Use 'gimp-image-detach-parasite' instead.

    :param image: The image
    :param name: The name of the parasite to detach from an image.
    """
    raise NotImplementedError()


def gimp_image_parasite_find(image: Image, name: str) -> Parasite:
    """
    This procedure is deprecated! Use 'gimp-image-get-parasite' instead.

    This procedure is deprecated! Use 'gimp-image-get-parasite' instead.

    :param image: The image
    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_image_parasite_list(image: Image) -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-image-get-parasite-list' instead.

    This procedure is deprecated! Use 'gimp-image-get-parasite-list' instead.

    :param image: The image
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_image_pick_color(image: Image, drawable: Drawable, x: float, y: float, sample_merged: int, sample_average: int, average_radius: float) -> Color:
    """
    Determine the color at the given drawable coordinates

    This tool determines the color at the specified coordinates. The returned color is an RGB triplet even for grayscale and indexed drawables. If the coordinates lie outside of the extents of the specified drawable, then an error is returned. If the drawable has an alpha channel, the algorithm examines the alpha value of the drawable at the coordinates. If the alpha value is completely transparent (0), then an error is returned. If the sample_merged parameter is TRUE, the data of the composite image will be used instead of that for the specified drawable. This is equivalent to sampling for colors after merging all visible layers. In the case of a merged sampling, the supplied drawable is ignored.

    :param image: The image
    :param drawable: The drawable to pick from
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param sample_merged: Use the composite image, not the drawable (TRUE or FALSE)
    :param sample_average: Average the color of all the pixels in a specified radius (TRUE or FALSE)
    :param average_radius: The radius of pixels to average (average-radius >= 0)
    :return: color
    """
    raise NotImplementedError()


def gimp_image_pick_correlate_layer(image: Image, x: int, y: int) -> Layer:
    """
    Find the layer visible at the specified coordinates.

    This procedure finds the layer which is visible at the specified coordinates. Layers which do not qualify are those whose extents do not pass within the specified coordinates, or which are transparent at the specified coordinates. This procedure will return -1 if no layer is found.

    :param image: The image
    :param x: The x coordinate for the pick
    :param y: The y coordinate for the pick
    :return: layer
    """
    raise NotImplementedError()


def gimp_image_raise_channel(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    :param image: The image
    :param item: The item to raise
    """
    raise NotImplementedError()


def gimp_image_raise_item(image: Image, item: Item):
    """
    Raise the specified item in its level in its item tree

    This procedure raises the specified item one step in the item tree. The procecure call will fail if there is no item above it.

    :param image: The image
    :param item: The item to raise
    """
    raise NotImplementedError()


def gimp_image_raise_item_to_top(image: Image, item: Item):
    """
    Raise the specified item to the top of its level in its item tree

    This procedure raises the specified item to top of its level in the item tree. It will not move the item if there is no item above it.

    :param image: The image
    :param item: The item to raise to top
    """
    raise NotImplementedError()


def gimp_image_raise_layer(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    :param image: The image
    :param item: The item to raise
    """
    raise NotImplementedError()


def gimp_image_raise_layer_to_top(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-raise-item-to-top' instead.

    This procedure is deprecated! Use 'gimp-image-raise-item-to-top' instead.

    :param image: The image
    :param item: The item to raise to top
    """
    raise NotImplementedError()


def gimp_image_raise_vectors(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    This procedure is deprecated! Use 'gimp-image-raise-item' instead.

    :param image: The image
    :param item: The item to raise
    """
    raise NotImplementedError()


def gimp_image_raise_vectors_to_top(image: Image, item: Item):
    """
    This procedure is deprecated! Use 'gimp-image-raise-item-to-top' instead.

    This procedure is deprecated! Use 'gimp-image-raise-item-to-top' instead.

    :param image: The image
    :param item: The item to raise to top
    """
    raise NotImplementedError()


def gimp_image_remove_channel(image: Image, channel: Channel):
    """
    Remove the specified channel from the image.

    This procedure removes the specified channel from the image. If the channel doesn't exist, an error is returned.

    :param image: The image
    :param channel: The channel
    """
    raise NotImplementedError()


def gimp_image_remove_layer(image: Image, layer: Layer):
    """
    Remove the specified layer from the image.

    This procedure removes the specified layer from the image. If the layer doesn't exist, an error is returned. If there are no layers left in the image, this call will fail. If this layer is the last layer remaining, the image will become empty and have no active layer.

    :param image: The image
    :param layer: The layer
    """
    raise NotImplementedError()


def gimp_image_remove_layer_mask(image: Image, layer: Layer, mode: int):
    """
    Deprecated: Use 'gimp-layer-remove-mask' instead.

    Deprecated: Use 'gimp-layer-remove-mask' instead.

    :param image: The image
    :param layer: The layer from which to remove mask
    :param mode: Removal mode { MASK-APPLY (0), MASK-DISCARD (1) }
    """
    raise NotImplementedError()


def gimp_image_remove_vectors(image: Image, vectors: Vectors):
    """
    Remove the specified path from the image.

    This procedure removes the specified path from the image. If the path doesn't exist, an error is returned.

    :param image: The image
    :param vectors: The vectors object
    """
    raise NotImplementedError()


def gimp_image_reorder_item(image: Image, item: Item, parent: Item, position: int):
    """
    Reorder the specified item within its item tree

    This procedure reorders the specified item within its item tree.

    :param image: The image
    :param item: The item to reorder
    :param parent: The new parent item
    :param position: The new position of the item
    """
    raise NotImplementedError()


def gimp_image_resize(image: Image, new_width: int, new_height: int, offx: int, offy: int):
    """
    Resize the image to the specified extents.

    This procedure resizes the image so that it's new width and height are equal to the supplied parameters. Offsets are also provided which describe the position of the previous image's content. All channels within the image are resized according to the specified parameters; this includes the image selection mask. All layers within the image are repositioned according to the specified offsets.

    :param image: The image
    :param new_width: New image width (1 <= new-width <= 262144)
    :param new_height: New image height (1 <= new-height <= 262144)
    :param offx: x offset between upper left corner of old and new images: (new - old)
    :param offy: y offset between upper left corner of old and new images: (new - old)
    """
    raise NotImplementedError()


def gimp_image_resize_to_layers(image: Image):
    """
    Resize the image to fit all layers.

    This procedure resizes the image to the bounding box of all layers of the image. All channels within the image are resized to the new size; this includes the image selection mask. All layers within the image are repositioned to the new image area.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_rotate(image: Image, rotate_type: int):
    """
    Rotates the image by the specified degrees.

    This procedure rotates the image.

    :param image: The image
    :param rotate_type: Angle of rotation { ROTATE-90 (0), ROTATE-180 (1), ROTATE-270 (2) }
    """
    raise NotImplementedError()


def gimp_image_scale(image: Image, new_width: int, new_height: int):
    """
    Scale the image using the default interpolation method.

    This procedure scales the image so that its new width and height are equal to the supplied parameters. All layers and channels within the image are scaled according to the specified parameters; this includes the image selection mask. The interpolation method used can be set with 'gimp-context-set-interpolation'.

    :param image: The image
    :param new_width: New image width (1 <= new-width <= 262144)
    :param new_height: New image height (1 <= new-height <= 262144)
    """
    raise NotImplementedError()


def gimp_image_scale_full(image: Image, new_width: int, new_height: int, interpolation: int):
    """
    Deprecated: Use 'gimp-image-scale' instead.

    Deprecated: Use 'gimp-image-scale' instead.

    :param image: The image
    :param new_width: New image width (1 <= new-width <= 262144)
    :param new_height: New image height (1 <= new-height <= 262144)
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    """
    raise NotImplementedError()


def gimp_image_select_color(image: Image, operation: int, drawable: Drawable, color: Color):
    """
    Create a selection by selecting all pixels (in the specified drawable) with the same (or similar) color to that specified.

    This tool creates a selection over the specified image. A by-color selection is determined by the supplied color under the constraints of the current context settings. Essentially, all pixels (in the drawable) that have color sufficiently close to the specified color (as determined by the threshold and criterion context values) are included in the selection. To select transparent regions, the color specified must also have minimum alpha. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius', 'gimp-context-set-sample-merged', 'gimp-context-set-sample-criterion', 'gimp-context-set-sample-threshold', 'gimp-context-set-sample-transparent'. In the case of a merged sampling, the supplied drawable is ignored.

    :param image: The affected image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param drawable: The affected drawable
    :param color: The color to select
    """
    raise NotImplementedError()


def gimp_image_select_contiguous_color(image: Image, operation: int, drawable: Drawable, x: float, y: float):
    """
    Create a selection by selecting all pixels around specified coordinates with the same (or similar) color to that at the coordinates.

    This tool creates a contiguous selection over the specified image. A contiguous color selection is determined by a seed fill under the constraints of the current context settings. Essentially, the color at the specified coordinates (in the drawable) is measured and the selection expands outwards from that point to any adjacent pixels which are not significantly different (as determined by the threshold and criterion context settings). This process continues until no more expansion is possible. If antialiasing is turned on, the final selection mask will contain intermediate values based on close misses to the threshold bar at pixels along the seed fill boundary. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius', 'gimp-context-set-sample-merged', 'gimp-context-set-sample-criterion', 'gimp-context-set-sample-threshold', 'gimp-context-set-sample-transparent'. In the case of a mergedsampling, the supplied drawable is ignored. If the sample is merged, the specified coordinates are relative to the image origin; otherwise, they are relative to the drawable's origin.

    :param image: The affected image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param drawable: The affected drawable
    :param x: x coordinate of initial seed fill point: (image coordinates)
    :param y: y coordinate of initial seed fill point: (image coordinates)
    """
    raise NotImplementedError()


def gimp_image_select_ellipse(image: Image, operation: int, x: float, y: float, width: float, height: float):
    """
    Create an elliptical selection over the specified image.

    This tool creates an elliptical selection over the specified image. The elliptical region can be either added to, subtracted from, or replace the contents of the previous selection mask. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius'.

    :param image: The image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param x: x coordinate of upper-left corner of ellipse bounding box
    :param y: y coordinate of upper-left corner of ellipse bounding box
    :param width: The width of the ellipse (width >= 0)
    :param height: The height of the ellipse (height >= 0)
    """
    raise NotImplementedError()


def gimp_image_select_item(image: Image, operation: int, item: Item):
    """
    Transforms the specified item into a selection

    This procedure renders the item's outline into the current selection of the image the item belongs to. What exactly the item's outline is depends on the item type: for layers, it's the layer's alpha channel, for vectors the vector's shape. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius'.

    :param image: The image
    :param operation: The desired operation with current selection { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param item: The item to render to the selection
    """
    raise NotImplementedError()


def gimp_image_select_polygon(image: Image, operation: int, num_segs: int, segs: List[float]):
    """
    Create a polygonal selection over the specified image.

    This tool creates a polygonal selection over the specified image. The polygonal region can be either added to, subtracted from, or replace the contents of the previous selection mask. The polygon is specified through an array of floating point numbers and its length. The length of array must be 2n, where n is the number of points. Each point is defined by 2 floating point values which correspond to the x and y coordinates. If the final point does not connect to the starting point, a connecting segment is automatically added. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius'.

    :param image: The image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param num_segs: Number of points (count 1 coordinate as two points) (num-segs >= 2)
    :param segs: Array of points: { p1.x, p1.y, p2.x, p2.y, ..., pn.x, pn.y}
    """
    raise NotImplementedError()


def gimp_image_select_rectangle(image: Image, operation: int, x: float, y: float, width: float, height: float):
    """
    Create a rectangular selection over the specified image;

    This tool creates a rectangular selection over the specified image. The rectangular region can be either added to, subtracted from, or replace the contents of the previous selection mask. This procedure is affected by the following context setters: 'gimp-context-set-feather', 'gimp-context-set-feather-radius'.

    :param image: The image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param width: The width of the rectangle (width >= 0)
    :param height: The height of the rectangle (height >= 0)
    """
    raise NotImplementedError()


def gimp_image_select_round_rectangle(image: Image, operation: int, x: float, y: float, width: float, height: float, corner_radius_x: float, corner_radius_y: float):
    """
    Create a rectangular selection with round corners over the specified image;

    This tool creates a rectangular selection with round corners over the specified image. The rectangular region can be either added to, subtracted from, or replace the contents of the previous selection mask. This procedure is affected by the following context setters: 'gimp-context-set-antialias', 'gimp-context-set-feather', 'gimp-context-set-feather-radius'.

    :param image: The image
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param width: The width of the rectangle (width >= 0)
    :param height: The height of the rectangle (height >= 0)
    :param corner_radius_x: The corner radius in X direction (0 <= corner-radius-x <= 262144)
    :param corner_radius_y: The corner radius in Y direction (0 <= corner-radius-y <= 262144)
    """
    raise NotImplementedError()


def gimp_image_set_active_channel(image: Image, active_channel: Channel):
    """
    Sets the specified image's active channel.

    If the channel exists, it is set as the active channel in the image. Any previous active channel or channel is set to inactive. An exception is a previously existing floating selection, in which case this procedure will return an execution error.

    :param image: The image
    :param active_channel: The new image active channel
    """
    raise NotImplementedError()


def gimp_image_set_active_layer(image: Image, active_layer: Layer):
    """
    Sets the specified image's active layer.

    If the layer exists, it is set as the active layer in the image. Any previous active layer or channel is set to inactive. An exception is a previously existing floating selection, in which case this procedure will return an execution error.

    :param image: The image
    :param active_layer: The new image active layer
    """
    raise NotImplementedError()


def gimp_image_set_active_vectors(image: Image, active_vectors: Vectors):
    """
    Sets the specified image's active vectors.

    If the path exists, it is set as the active path in the image.

    :param image: The image
    :param active_vectors: The new image active vectors
    """
    raise NotImplementedError()


def gimp_image_set_cmap(image: Image, num_bytes: int, colormap: List[int]):
    """
    This procedure is deprecated! Use 'gimp-image-set-colormap' instead.

    This procedure is deprecated! Use 'gimp-image-set-colormap' instead.

    :param image: The image
    :param num_bytes: Number of bytes in the colormap array (0 <= num-bytes <= 768)
    :param colormap: The new colormap values
    """
    raise NotImplementedError()


def gimp_image_set_colormap(image: Image, num_bytes: int, colormap: List[int]):
    """
    Sets the entries in the image's colormap.

    This procedure sets the entries in the specified image's colormap. The number of entries is specified by the 'num-bytes' parameter and corresponds to the number of INT8 triples that must be contained in the 'colormap' array. The actual number of colors in the transmitted colormap is 'num-bytes' / 3.

    :param image: The image
    :param num_bytes: Number of bytes in the colormap array (0 <= num-bytes <= 768)
    :param colormap: The new colormap values
    """
    raise NotImplementedError()


def gimp_image_set_component_active(image: Image, component: int, active: int):
    """
    Sets if the specified image's image component is active.

    This procedure sets if the specified image's image component (i.e. Red, Green, Blue intensity channels in an RGB image) is active or inactive -- whether or not it can be modified. If the specified component is not valid for the image type, an error is returned.

    :param image: The image
    :param component: The image component { RED-CHANNEL (0), GREEN-CHANNEL (1), BLUE-CHANNEL (2), GRAY-CHANNEL (3), INDEXED-CHANNEL (4), ALPHA-CHANNEL (5) }
    :param active: Component is active (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_image_set_component_visible(image: Image, component: int, visible: int):
    """
    Sets if the specified image's image component is visible.

    This procedure sets if the specified image's image component (i.e. Red, Green, Blue intensity channels in an RGB image) is visible or invisible -- whether or not it can be seen. If the specified component is not valid for the image type, an error is returned.

    :param image: The image
    :param component: The image component { RED-CHANNEL (0), GREEN-CHANNEL (1), BLUE-CHANNEL (2), GRAY-CHANNEL (3), INDEXED-CHANNEL (4), ALPHA-CHANNEL (5) }
    :param visible: Component is visible (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_image_set_filename(image: Image, filename: str):
    """
    Sets the specified image's filename.

    This procedure sets the specified image's filename. The filename should be in the filesystem encoding.

    :param image: The image
    :param filename: The new image filename
    """
    raise NotImplementedError()


def gimp_image_set_resolution(image: Image, xresolution: float, yresolution: float):
    """
    Sets the specified image's resolution.

    This procedure sets the specified image's resolution in dots per inch. This value is independent of any of the layers in this image. No scaling or resizing is performed.

    :param image: The image
    :param xresolution: The new image resolution in the x-axis, in dots per inch
    :param yresolution: The new image resolution in the y-axis, in dots per inch
    """
    raise NotImplementedError()


def gimp_image_set_tattoo_state(image: Image, tattoo_state: int):
    """
    Set the tattoo state associated with the image.

    This procedure sets the tattoo state of the image. Use only by save/load plugins that wish to preserve an images tattoo state. Using this function at other times will produce unexpected results. A full check of uniqueness of states in layers, channels and paths will be performed by this procedure and a execution failure will be returned if this fails. A failure will also be returned if the new tattoo state value is less than the maximum tattoo value from all of the tattoos from the paths, layers and channels. After the image data has been loaded and all the tattoos have been set then this is the last procedure that should be called. If effectively does a status check on the tattoo values that have been set to make sure that all is OK.

    :param image: The image
    :param tattoo_state: The new image tattoo state
    """
    raise NotImplementedError()


def gimp_image_set_unit(image: Image, unit: int):
    """
    Sets the specified image's unit.

    This procedure sets the specified image's unit. No scaling or resizing is performed. This value is independent of any of the layers in this image. See the gimp_unit_*() procedure definitions for the valid range of unit IDs and a description of the unit system.

    :param image: The image
    :param unit: The new image unit
    """
    raise NotImplementedError()


def gimp_image_thumbnail(image: Image, width: int, height: int) -> Tuple[int, int, int, int, List[int]]:
    """
    Get a thumbnail of an image.

    This function gets data from which a thumbnail of an image preview can be created. Maximum x or y dimension is 1024 pixels. The pixels are returned in RGB[A] or GRAY[A] format. The bpp return value gives the number of bits per pixel in the image.

    :param image: The image
    :param width: The requested thumbnail width (1 <= width <= 1024)
    :param height: The requested thumbnail height (1 <= height <= 1024)
    :return: actual_width, actual_height, bpp, thumbnail_data_count, thumbnail_data
    """
    raise NotImplementedError()


def gimp_image_undo_disable(image: Image) -> int:
    """
    Disable the image's undo stack.

    This procedure disables the image's undo stack, allowing subsequent operations to ignore their undo steps. This is generally called in conjunction with 'gimp-image-undo-enable' to temporarily disable an image undo stack. This is advantageous because saving undo steps can be time and memory intensive.

    :param image: The image
    :return: disabled
    """
    raise NotImplementedError()


def gimp_image_undo_enable(image: Image) -> int:
    """
    Enable the image's undo stack.

    This procedure enables the image's undo stack, allowing subsequent operations to store their undo steps. This is generally called in conjunction with 'gimp-image-undo-disable' to temporarily disable an image undo stack.

    :param image: The image
    :return: enabled
    """
    raise NotImplementedError()


def gimp_image_undo_freeze(image: Image) -> int:
    """
    Freeze the image's undo stack.

    This procedure freezes the image's undo stack, allowing subsequent operations to ignore their undo steps. This is generally called in conjunction with 'gimp-image-undo-thaw' to temporarily disable an image undo stack. This is advantageous because saving undo steps can be time and memory intensive. 'gimp-image-undo-freeze' / 'gimp-image-undo-thaw' and 'gimp-image-undo-disable' / 'gimp-image-undo-enable' differ in that the former does not free up all undo steps when undo is thawed, so is more suited to interactive in-situ previews. It is important in this case that the image is back to the same state it was frozen in before thawing, else 'undo' behaviour is undefined.

    :param image: The image
    :return: frozen
    """
    raise NotImplementedError()


def gimp_image_undo_group_end(image: Image):
    """
    Finish a group undo.

    This function must be called once for each 'gimp-image-undo-group-start' call that is made.

    :param image: The ID of the image in which to close an undo group
    """
    raise NotImplementedError()


def gimp_image_undo_group_start(image: Image):
    """
    Starts a group undo.

    This function is used to start a group undo--necessary for logically combining two or more undo operations into a single operation. This call must be used in conjunction with a 'gimp-image-undo-group-end' call.

    :param image: The ID of the image in which to open an undo group
    """
    raise NotImplementedError()


def gimp_image_undo_is_enabled(image: Image) -> int:
    """
    Check if the image's undo stack is enabled.

    This procedure checks if the image's undo stack is currently enabled or disabled. This is useful when several plugins or scripts call each other and want to check if their caller has already used 'gimp-image-undo-disable' or 'gimp-image-undo-freeze'.

    :param image: The image
    :return: enabled
    """
    raise NotImplementedError()


def gimp_image_undo_thaw(image: Image) -> int:
    """
    Thaw the image's undo stack.

    This procedure thaws the image's undo stack, allowing subsequent operations to store their undo steps. This is generally called in conjunction with 'gimp-image-undo-freeze' to temporarily freeze an image undo stack. 'gimp-image-undo-thaw' does NOT free the undo stack as 'gimp-image-undo-enable' does, so is suited for situations where one wishes to leave the undo stack in the same state in which one found it despite non-destructively playing with the image in the meantime. An example would be in-situ plugin previews. Balancing freezes and thaws and ensuring image consistancy is the responsibility of the caller.

    :param image: The image
    :return: thawed
    """
    raise NotImplementedError()


def gimp_image_unset_active_channel(image: Image):
    """
    Unsets the active channel in the specified image.

    If an active channel exists, it is unset. There then exists no active channel, and if desired, one can be set through a call to 'Set Active Channel'. No error is returned in the case of no existing active channel.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_image_width(image: Image) -> int:
    """
    Return the width of the image

    This procedure returns the image's width. This value is independent of any of the layers in this image. This is the "canvas" width.

    :param image: The image
    :return: width
    """
    raise NotImplementedError()


def gimp_invert(drawable: Drawable):
    """
    Invert the contents of the specified drawable.

    This procedure inverts the contents of the specified drawable. Each intensity channel is inverted independently. The inverted intensity is given as inten' = (255 - inten). Indexed color drawables are not valid for this operation.

    :param drawable: The drawable
    """
    raise NotImplementedError()


def gimp_item_attach_parasite(item: Item, parasite: Parasite):
    """
    Add a parasite to an item.

    This procedure attaches a parasite to an item. It has no return values.

    :param item: The item
    :param parasite: The parasite to attach to the item
    """
    raise NotImplementedError()


def gimp_item_delete(item: Item):
    """
    Delete a item.

    This procedure deletes the specified item. This must not be done if the image containing this item was already deleted or if the item was already removed from the image. The only case in which this procedure is useful is if you want to get rid of a item which has not yet been added to an image.

    :param item: The item to delete
    """
    raise NotImplementedError()


def gimp_item_detach_parasite(item: Item, name: str):
    """
    Removes a parasite from an item.

    This procedure detaches a parasite from an item. It has no return values.

    :param item: The item
    :param name: The name of the parasite to detach from the item.
    """
    raise NotImplementedError()


def gimp_item_get_children(item: Item) -> Tuple[int, List[int]]:
    """
    Returns the item's list of children.

    This procedure returns the list of items which are children of the specified item. The order is topmost to bottommost.

    :param item: The item
    :return: num_children, child_ids
    """
    raise NotImplementedError()


def gimp_item_get_image(item: Item) -> Image:
    """
    Returns the item's image.

    This procedure returns the item's image.

    :param item: The item
    :return: image
    """
    raise NotImplementedError()


def gimp_item_get_linked(item: Item) -> int:
    """
    Get the linked state of the specified item.

    This procedure returns the specified item's linked state.

    :param item: The item
    :return: linked
    """
    raise NotImplementedError()


def gimp_item_get_lock_content(item: Item) -> int:
    """
    Get the 'lock content' state of the specified item.

    This procedure returns the specified item's lock content state.

    :param item: The item
    :return: lock_content
    """
    raise NotImplementedError()


def gimp_item_get_name(item: Item) -> str:
    """
    Get the name of the specified item.

    This procedure returns the specified item's name.

    :param item: The item
    :return: name
    """
    raise NotImplementedError()


def gimp_item_get_parasite(item: Item, name: str) -> Parasite:
    """
    Look up a parasite in an item

    Finds and returns the parasite that is attached to an item.

    :param item: The item
    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_item_get_parasite_list(item: Item) -> Tuple[int, List[str]]:
    """
    List all parasites.

    Returns a list of all parasites currently attached the an item.

    :param item: The item
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_item_get_parent(item: Item) -> Item:
    """
    Returns the item's parent item.

    This procedure returns the item's parent item, if any.

    :param item: The item
    :return: parent
    """
    raise NotImplementedError()


def gimp_item_get_tattoo(item: Item) -> int:
    """
    Get the tattoo of the specified item.

    This procedure returns the specified item's tattoo. A tattoo is a unique and permanent identifier attached to a item that can be used to uniquely identify a item within an image even between sessions.

    :param item: The item
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_item_get_visible(item: Item) -> int:
    """
    Get the visibility of the specified item.

    This procedure returns the specified item's visibility.

    :param item: The item
    :return: visible
    """
    raise NotImplementedError()


def gimp_item_is_channel(item: Item) -> int:
    """
    Returns whether the item is a channel.

    This procedure returns TRUE if the specified item is a channel.

    :param item: The item
    :return: channel
    """
    raise NotImplementedError()


def gimp_item_is_drawable(item: Item) -> int:
    """
    Returns whether the item is a drawable.

    This procedure returns TRUE if the specified item is a drawable.

    :param item: The item
    :return: drawable
    """
    raise NotImplementedError()


def gimp_item_is_group(item: Item) -> int:
    """
    Returns whether the item is a group item.

    This procedure returns TRUE if the specified item is a group item which can have children.

    :param item: The item
    :return: group
    """
    raise NotImplementedError()


def gimp_item_is_layer(item: Item) -> int:
    """
    Returns whether the item is a layer.

    This procedure returns TRUE if the specified item is a layer.

    :param item: The item
    :return: layer
    """
    raise NotImplementedError()


def gimp_item_is_layer_mask(item: Item) -> int:
    """
    Returns whether the item is a layer mask.

    This procedure returns TRUE if the specified item is a layer mask.

    :param item: The item
    :return: layer_mask
    """
    raise NotImplementedError()


def gimp_item_is_selection(item: Item) -> int:
    """
    Returns whether the item is a selection.

    This procedure returns TRUE if the specified item is a selection.

    :param item: The item
    :return: selection
    """
    raise NotImplementedError()


def gimp_item_is_text_layer(item: Item) -> int:
    """
    Returns whether the item is a text layer.

    This procedure returns TRUE if the specified item is a text layer.

    :param item: The item
    :return: text_layer
    """
    raise NotImplementedError()


def gimp_item_is_valid(item: Item) -> int:
    """
    Returns TRUE if the item is valid.

    This procedure checks if the given item ID is valid and refers to an existing item.

    :param item: The item to check
    :return: valid
    """
    raise NotImplementedError()


def gimp_item_is_vectors(item: Item) -> int:
    """
    Returns whether the item is a vectors.

    This procedure returns TRUE if the specified item is a vectors.

    :param item: The item
    :return: vectors
    """
    raise NotImplementedError()


def gimp_item_set_linked(item: Item, linked: int):
    """
    Set the linked state of the specified item.

    This procedure sets the specified item's linked state.

    :param item: The item
    :param linked: The new item linked state (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_item_set_lock_content(item: Item, lock_content: int):
    """
    Set the 'lock content' state of the specified item.

    This procedure sets the specified item's lock content state.

    :param item: The item
    :param lock_content: The new item 'lock content' state (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_item_set_name(item: Item, name: str):
    """
    Set the name of the specified item.

    This procedure sets the specified item's name.

    :param item: The item
    :param name: The new item name
    """
    raise NotImplementedError()


def gimp_item_set_tattoo(item: Item, tattoo: int):
    """
    Set the tattoo of the specified item.

    This procedure sets the specified item's tattoo. A tattoo is a unique and permanent identifier attached to a item that can be used to uniquely identify a item within an image even between sessions.

    :param item: The item
    :param tattoo: The new item tattoo
    """
    raise NotImplementedError()


def gimp_item_set_visible(item: Item, visible: int):
    """
    Set the visibility of the specified item.

    This procedure sets the specified item's visibility.

    :param item: The item
    :param visible: The new item visibility (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_item_transform_2d(item: Item, source_x: float, source_y: float, scale_x: float, scale_y: float, angle: float, dest_x: float, dest_y: float) -> Item:
    """
    Transform the specified item in 2d.

    This procedure transforms the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then transformed. The transformation is done by scaling the image by the x and y scale factors about the point (source_x, source_y), then rotating around the same point, then translating that point to the new position (dest_x, dest_y). The return value is the ID of the rotated drawable. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and transformed drawable. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param source_x: X coordinate of the transformation center
    :param source_y: Y coordinate of the transformation center
    :param scale_x: Amount to scale in x direction
    :param scale_y: Amount to scale in y direction
    :param angle: The angle of rotation (radians)
    :param dest_x: X coordinate of where the center goes
    :param dest_y: Y coordinate of where the center goes
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_flip(item: Item, x0: float, y0: float, x1: float, y1: float) -> Item:
    """
    Flip the specified item around a given line.

    This procedure flips the specified item. If a selection exists and the item is a drawable , the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then flipped. The axis to flip around is specified by specifying two points from that line. The return value is the ID of the flipped item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and flipped drawable. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param x0: horz. coord. of one end of axis
    :param y0: vert. coord. of one end of axis
    :param x1: horz. coord. of other end of axis
    :param y1: vert. coord. of other end of axis
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_flip_simple(item: Item, flip_type: int, auto_center: int, axis: float) -> Item:
    """
    Flip the specified item either vertically or horizontally.

    This procedure flips the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then flipped. If auto_center is set to TRUE, the flip is around the selection's center. Otherwise, the coordinate of the axis needs to be specified. The return value is the ID of the flipped item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and flipped drawable. This procedure is affected by the following context setters: 'gimp-context-set-transform-resize'.

    :param item: The affected item
    :param flip_type: Type of flip { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param auto_center: Whether to automatically position the axis in the selection center (TRUE or FALSE)
    :param axis: coord. of flip axis
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_matrix(item: Item, coeff_0_0: float, coeff_0_1: float, coeff_0_2: float, coeff_1_0: float, coeff_1_1: float, coeff_1_2: float, coeff_2_0: float, coeff_2_1: float, coeff_2_2: float) -> Item:
    """
    Transform the specified item in 2d.

    This procedure transforms the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then transformed. The transformation is done by assembling a 3x3 matrix from the coefficients passed. The return value is the ID of the transformed item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and transformed drawable. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param coeff_0_0: coefficient (0,0) of the transformation matrix
    :param coeff_0_1: coefficient (0,1) of the transformation matrix
    :param coeff_0_2: coefficient (0,2) of the transformation matrix
    :param coeff_1_0: coefficient (1,0) of the transformation matrix
    :param coeff_1_1: coefficient (1,1) of the transformation matrix
    :param coeff_1_2: coefficient (1,2) of the transformation matrix
    :param coeff_2_0: coefficient (2,0) of the transformation matrix
    :param coeff_2_1: coefficient (2,1) of the transformation matrix
    :param coeff_2_2: coefficient (2,2) of the transformation matrix
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_perspective(item: Item, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> Item:
    """
    Perform a possibly non-affine transformation on the specified item.

    This procedure performs a possibly non-affine transformation on the specified item by allowing the corners of the original bounding box to be arbitrarily remapped to any values. The specified item is remapped if no selection exists or it is not a drawable. However, if a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then remapped as specified. The return value is the ID of the remapped item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and remapped drawable. The 4 coordinates specify the new locations of each corner of the original bounding box. By specifying these values, any affine transformation (rotation, scaling, translation) can be affected. Additionally, these values can be specified such that the resulting transformed item will appear to havebeen projected via a perspective transform. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param x0: The new x coordinate of upper-left corner of original bounding box
    :param y0: The new y coordinate of upper-left corner of original bounding box
    :param x1: The new x coordinate of upper-right corner of original bounding box
    :param y1: The new y coordinate of upper-right corner of original bounding box
    :param x2: The new x coordinate of lower-left corner of original bounding box
    :param y2: The new y coordinate of lower-left corner of original bounding box
    :param x3: The new x coordinate of lower-right corner of original bounding box
    :param y3: The new y coordinate of lower-right corner of original bounding box
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_rotate(item: Item, angle: float, auto_center: int, center_x: float, center_y: float) -> Item:
    """
    Rotate the specified item about given coordinates through the specified angle.

    This function rotates the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then rotated by the specified amount. The return value is the ID of the rotated item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and rotated drawable. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param angle: The angle of rotation (radians)
    :param auto_center: Whether to automatically rotate around the selection center (TRUE or FALSE)
    :param center_x: The hor. coordinate of the center of rotation
    :param center_y: The vert. coordinate of the center of rotation
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_rotate_simple(item: Item, rotate_type: int, auto_center: int, center_x: float, center_y: float) -> Item:
    """
    Rotate the specified item about given coordinates through the specified angle.

    This function rotates the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then rotated by the specified amount. The return value is the ID of the rotated item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and rotated drawable. This procedure is affected by the following context setters: 'gimp-context-set-transform-resize'.

    :param item: The affected item
    :param rotate_type: Type of rotation { ROTATE-90 (0), ROTATE-180 (1), ROTATE-270 (2) }
    :param auto_center: Whether to automatically rotate around the selection center (TRUE or FALSE)
    :param center_x: The hor. coordinate of the center of rotation
    :param center_y: The vert. coordinate of the center of rotation
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_scale(item: Item, x0: float, y0: float, x1: float, y1: float) -> Item:
    """
    Scale the specified item.

    This procedure scales the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then scaled by the specified amount. The return value is the ID of the scaled item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and scaled drawable. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param x0: The new x coordinate of the upper-left corner of the scaled region
    :param y0: The new y coordinate of the upper-left corner of the scaled region
    :param x1: The new x coordinate of the lower-right corner of the scaled region
    :param y1: The new y coordinate of the lower-right corner of the scaled region
    :return: item
    """
    raise NotImplementedError()


def gimp_item_transform_shear(item: Item, shear_type: int, magnitude: float) -> Item:
    """
    Shear the specified item about its center by the specified magnitude.

    This procedure shears the specified item. If a selection exists and the item is a drawable, the portion of the drawable which lies under the selection is cut from the drawable and made into a floating selection which is then sheard by the specified amount. The return value is the ID of the sheard item. If there was no selection or the item is not a drawable, this will be equal to the item ID supplied as input. Otherwise, this will be the newly created and sheard drawable. The shear type parameter indicates whether the shear will be applied horizontally or vertically. The magnitude can be either positive or negative and indicates the extent (in pixels) to shear by. This procedure is affected by the following context setters: 'gimp-context-set-interpolation', 'gimp-context-set-transform-direction', 'gimp-context-set-transform-resize', 'gimp-context-set-transform-recursion'.

    :param item: The affected item
    :param shear_type: Type of shear { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param magnitude: The magnitude of the shear
    :return: item
    """
    raise NotImplementedError()


def gimp_layer_add_alpha(layer: Layer):
    """
    Add an alpha channel to the layer if it doesn't already have one.

    This procedure adds an additional component to the specified layer if it does not already possess an alpha channel. An alpha channel makes it possible to clear and erase to transparency, instead of the background color. This transforms layers of type RGB to RGBA, GRAY to GRAYA, and INDEXED to INDEXEDA.

    :param layer: The layer
    """
    raise NotImplementedError()


def gimp_layer_add_mask(layer: Layer, mask: Channel):
    """
    Add a layer mask to the specified layer.

    This procedure adds a layer mask to the specified layer. Layer masks serve as an additional alpha channel for a layer. This procedure will fail if a number of prerequisites aren't met. The layer cannot already have a layer mask. The specified mask must exist and have the same dimensions as the layer. The layer must have been created for use with the specified image and the mask must have been created with the procedure 'gimp-layer-create-mask'.

    :param layer: The layer to receive the mask
    :param mask: The mask to add to the layer
    """
    raise NotImplementedError()


def gimp_layer_copy(layer: Layer, add_alpha: int) -> Layer:
    """
    Copy a layer.

    This procedure copies the specified layer and returns the copy. The newly copied layer is for use within the original layer's image. It should not be subsequently added to any other image. The copied layer can optionally have an added alpha channel. This is useful if the background layer in an image is being copied and added to the same image.

    :param layer: The layer to copy
    :param add_alpha: Add an alpha channel to the copied layer (TRUE or FALSE)
    :return: layer_copy
    """
    raise NotImplementedError()


def gimp_layer_create_mask(layer: Layer, mask_type: int) -> Channel:
    """
    Create a layer mask for the specified specified layer.

    This procedure creates a layer mask for the specified layer. Layer masks serve as an additional alpha channel for a layer. A number of different types of masks are allowed for initialisation: completely white masks (which will leave the layer fully visible), completely black masks (which will give the layer complete transparency, the layer's already existing alpha channel (which will leave the layer fully visible, but which may be more useful than a white mask), the current selection or a grayscale copy of the layer. The layer mask still needs to be added to the layer. This can be done with a call to 'gimp-layer-add-mask'.

    :param layer: The layer to which to add the mask
    :param mask_type: The type of mask { ADD-WHITE-MASK (0), ADD-BLACK-MASK (1), ADD-ALPHA-MASK (2), ADD-ALPHA-TRANSFER-MASK (3), ADD-SELECTION-MASK (4), ADD-COPY-MASK (5), ADD-CHANNEL-MASK (6) }
    :return: mask
    """
    raise NotImplementedError()


def gimp_layer_delete(item: Item):
    """
    This procedure is deprecated! Use 'gimp-item-delete' instead.

    This procedure is deprecated! Use 'gimp-item-delete' instead.

    :param item: The item to delete
    """
    raise NotImplementedError()


def gimp_layer_flatten(layer: Layer):
    """
    Remove the alpha channel from the layer if it has one.

    This procedure removes the alpha channel from a layer, blending all (partially) transparent pixels in the layer against the background color. This transforms layers of type RGBA to RGB, GRAYA to GRAY, and INDEXEDA to INDEXED.

    :param layer: The layer
    """
    raise NotImplementedError()


def gimp_layer_from_mask(mask: Channel) -> Layer:
    """
    Get the specified mask's layer.

    This procedure returns the specified mask's layer , or -1 if none exists.

    :param mask: Mask for which to return the layer
    :return: layer
    """
    raise NotImplementedError()


def gimp_layer_get_apply_mask(layer: Layer) -> int:
    """
    Get the apply mask setting of the specified layer.

    This procedure returns the specified layer's apply mask setting. If the value is TRUE, then the layer mask for this layer is currently being composited with the layer's alpha channel.

    :param layer: The layer
    :return: apply_mask
    """
    raise NotImplementedError()


def gimp_layer_get_edit_mask(layer: Layer) -> int:
    """
    Get the edit mask setting of the specified layer.

    This procedure returns the specified layer's edit mask setting. If the value is TRUE, then the layer mask for this layer is currently active, and not the layer.

    :param layer: The layer
    :return: edit_mask
    """
    raise NotImplementedError()


def gimp_layer_get_linked(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    :param item: The item
    :return: linked
    """
    raise NotImplementedError()


def gimp_layer_get_lock_alpha(layer: Layer) -> int:
    """
    Get the lock alpha channel setting of the specified layer.

    This procedure returns the specified layer's lock alpha channel setting.

    :param layer: The layer
    :return: lock_alpha
    """
    raise NotImplementedError()


def gimp_layer_get_mask(layer: Layer) -> Channel:
    """
    Get the specified layer's mask if it exists.

    This procedure returns the specified layer's mask, or -1 if none exists.

    :param layer: The layer
    :return: mask
    """
    raise NotImplementedError()


def gimp_layer_get_mode(layer: Layer) -> int:
    """
    Get the combination mode of the specified layer.

    This procedure returns the specified layer's combination mode.

    :param layer: The layer
    :return: mode
    """
    raise NotImplementedError()


def gimp_layer_get_name(item: Item) -> str:
    """
    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    :param item: The item
    :return: name
    """
    raise NotImplementedError()


def gimp_layer_get_opacity(layer: Layer) -> float:
    """
    Get the opacity of the specified layer.

    This procedure returns the specified layer's opacity.

    :param layer: The layer
    :return: opacity
    """
    raise NotImplementedError()


def gimp_layer_get_preserve_trans(layer: Layer) -> int:
    """
    This procedure is deprecated! Use 'gimp-layer-get-lock-alpha' instead.

    This procedure is deprecated! Use 'gimp-layer-get-lock-alpha' instead.

    :param layer: The layer
    :return: lock_alpha
    """
    raise NotImplementedError()


def gimp_layer_get_show_mask(layer: Layer) -> int:
    """
    Get the show mask setting of the specified layer.

    This procedure returns the specified layer's show mask setting. This controls whether the layer or its mask is visible. TRUE indicates that the mask should be visible. If the layer has no mask, then this function returns an error.

    :param layer: The layer
    :return: show_mask
    """
    raise NotImplementedError()


def gimp_layer_get_tattoo(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    :param item: The item
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_layer_get_visible(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    :param item: The item
    :return: visible
    """
    raise NotImplementedError()


def gimp_layer_group_new(image: Image) -> Layer:
    """
    Create a new layer group.

    This procedure creates a new layer group. Attributes such as layer mode and opacity should be set with explicit procedure calls. Add the new layer group (which is a kind of layer) with the 'gimp-image-insert-layer' command. Other procedures useful with layer groups: 'gimp-image-reorder-item', 'gimp-item-get-parent', 'gimp-item-get-children', 'gimp-item-is-group'.

    :param image: The image to which to add the layer group
    :return: layer_group
    """
    raise NotImplementedError()


def gimp_layer_is_floating_sel(layer: Layer) -> int:
    """
    Is the specified layer a floating selection?

    This procedure returns whether the layer is a floating selection. Floating selections are special cases of layers which are attached to a specific drawable.

    :param layer: The layer
    :return: is_floating_sel
    """
    raise NotImplementedError()


def gimp_layer_mask(layer: Layer) -> Channel:
    """
    This procedure is deprecated! Use 'gimp-layer-get-mask' instead.

    This procedure is deprecated! Use 'gimp-layer-get-mask' instead.

    :param layer: The layer
    :return: mask
    """
    raise NotImplementedError()


def gimp_layer_new(image: Image, width: int, height: int, type: int, name: str, opacity: float, mode: int) -> Layer:
    """
    Create a new layer.

    This procedure creates a new layer with the specified width, height, and type. Name, opacity, and mode are also supplied parameters. The new layer still needs to be added to the image, as this is not automatic. Add the new layer with the 'gimp-image-insert-layer' command. Other attributes such as layer mask modes, and offsets should be set with explicit procedure calls.

    :param image: The image to which to add the layer
    :param width: The layer width (1 <= width <= 262144)
    :param height: The layer height (1 <= height <= 262144)
    :param type: The layer type { RGB-IMAGE (0), RGBA-IMAGE (1), GRAY-IMAGE (2), GRAYA-IMAGE (3), INDEXED-IMAGE (4), INDEXEDA-IMAGE (5) }
    :param name: The layer name
    :param opacity: The layer opacity (0 <= opacity <= 100)
    :param mode: The layer combination mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    :return: layer
    """
    raise NotImplementedError()


def gimp_layer_new_from_drawable(drawable: Drawable, dest_image: Image) -> Layer:
    """
    Create a new layer by copying an existing drawable.

    This procedure creates a new layer as a copy of the specified drawable. The new layer still needs to be added to the image, as this is not automatic. Add the new layer with the 'gimp-image-insert-layer' command. Other attributes such as layer mask modes, and offsets should be set with explicit procedure calls.

    :param drawable: The source drawable from where the new layer is copied
    :param dest_image: The destination image to which to add the layer
    :return: layer_copy
    """
    raise NotImplementedError()


def gimp_layer_new_from_visible(image: Image, dest_image: Image, name: str) -> Layer:
    """
    Create a new layer from what is visible in an image.

    This procedure creates a new layer from what is visible in the given image. The new layer still needs to be added to the destination image, as this is not automatic. Add the new layer with the 'gimp-image-insert-layer' command. Other attributes such as layer mask modes, and offsets should be set with explicit procedure calls.

    :param image: The source image from where the content is copied
    :param dest_image: The destination image to which to add the layer
    :param name: The layer name
    :return: layer
    """
    raise NotImplementedError()


def gimp_layer_remove_mask(layer: Layer, mode: int):
    """
    Remove the specified layer mask from the layer.

    This procedure removes the specified layer mask from the layer. If the mask doesn't exist, an error is returned.

    :param layer: The layer from which to remove mask
    :param mode: Removal mode { MASK-APPLY (0), MASK-DISCARD (1) }
    """
    raise NotImplementedError()


def gimp_layer_resize(layer: Layer, new_width: int, new_height: int, offx: int, offy: int):
    """
    Resize the layer to the specified extents.

    This procedure resizes the layer so that its new width and height are equal to the supplied parameters. Offsets are also provided which describe the position of the previous layer's content. This operation only works if the layer has been added to an image.

    :param layer: The layer
    :param new_width: New layer width (1 <= new-width <= 262144)
    :param new_height: New layer height (1 <= new-height <= 262144)
    :param offx: x offset between upper left corner of old and new layers: (old - new)
    :param offy: y offset between upper left corner of old and new layers: (old - new)
    """
    raise NotImplementedError()


def gimp_layer_resize_to_image_size(layer: Layer):
    """
    Resize a layer to the image size.

    This procedure resizes the layer so that it's new width and height are equal to the width and height of its image container.

    :param layer: The layer to resize
    """
    raise NotImplementedError()


def gimp_layer_scale(layer: Layer, new_width: int, new_height: int, local_origin: int):
    """
    Scale the layer using the default interpolation method.

    This procedure scales the layer so that its new width and height are equal to the supplied parameters. The 'local-origin' parameter specifies whether to scale from the center of the layer, or from the image origin. This operation only works if the layer has been added to an image. The interpolation method used can be set with 'gimp-context-set-interpolation'.

    :param layer: The layer
    :param new_width: New layer width (1 <= new-width <= 262144)
    :param new_height: New layer height (1 <= new-height <= 262144)
    :param local_origin: Use a local origin (as opposed to the image origin) (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_scale_full(layer: Layer, new_width: int, new_height: int, local_origin: int, interpolation: int):
    """
    Deprecated: Use 'gimp-layer-scale' instead.

    Deprecated: Use 'gimp-layer-scale' instead.

    :param layer: The layer
    :param new_width: New layer width (1 <= new-width <= 262144)
    :param new_height: New layer height (1 <= new-height <= 262144)
    :param local_origin: Use a local origin (as opposed to the image origin) (TRUE or FALSE)
    :param interpolation: Type of interpolation { INTERPOLATION-NONE (0), INTERPOLATION-LINEAR (1), INTERPOLATION-CUBIC (2), INTERPOLATION-LANCZOS (3) }
    """
    raise NotImplementedError()


def gimp_layer_set_apply_mask(layer: Layer, apply_mask: int):
    """
    Set the apply mask setting of the specified layer.

    This procedure sets the specified layer's apply mask setting. This controls whether the layer's mask is currently affecting the alpha channel. If there is no layer mask, this function will return an error.

    :param layer: The layer
    :param apply_mask: The new layer's apply mask setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_edit_mask(layer: Layer, edit_mask: int):
    """
    Set the edit mask setting of the specified layer.

    This procedure sets the specified layer's edit mask setting. This controls whether the layer or it's mask is currently active for editing. If the specified layer has no layer mask, then this procedure will return an error.

    :param layer: The layer
    :param edit_mask: The new layer's edit mask setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_linked(item: Item, linked: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    :param item: The item
    :param linked: The new item linked state (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_lock_alpha(layer: Layer, lock_alpha: int):
    """
    Set the lock alpha channel setting of the specified layer.

    This procedure sets the specified layer's lock alpha channel setting.

    :param layer: The layer
    :param lock_alpha: The new layer's lock alpha channel setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_mode(layer: Layer, mode: int):
    """
    Set the combination mode of the specified layer.

    This procedure sets the specified layer's combination mode.

    :param layer: The layer
    :param mode: The new layer combination mode { NORMAL-MODE (0), DISSOLVE-MODE (1), BEHIND-MODE (2), MULTIPLY-MODE (3), SCREEN-MODE (4), OVERLAY-MODE (5), DIFFERENCE-MODE (6), ADDITION-MODE (7), SUBTRACT-MODE (8), DARKEN-ONLY-MODE (9), LIGHTEN-ONLY-MODE (10), HUE-MODE (11), SATURATION-MODE (12), COLOR-MODE (13), VALUE-MODE (14), DIVIDE-MODE (15), DODGE-MODE (16), BURN-MODE (17), HARDLIGHT-MODE (18), SOFTLIGHT-MODE (19), GRAIN-EXTRACT-MODE (20), GRAIN-MERGE-MODE (21), COLOR-ERASE-MODE (22), ERASE-MODE (23), REPLACE-MODE (24), ANTI-ERASE-MODE (25) }
    """
    raise NotImplementedError()


def gimp_layer_set_name(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    :param item: The item
    :param name: The new item name
    """
    raise NotImplementedError()


def gimp_layer_set_offsets(layer: Layer, offx: int, offy: int):
    """
    Set the layer offsets.

    This procedure sets the offsets for the specified layer. The offsets are relative to the image origin and can be any values. This operation is valid only on layers which have been added to an image.

    :param layer: The layer
    :param offx: Offset in x direction
    :param offy: Offset in y direction
    """
    raise NotImplementedError()


def gimp_layer_set_opacity(layer: Layer, opacity: float):
    """
    Set the opacity of the specified layer.

    This procedure sets the specified layer's opacity.

    :param layer: The layer
    :param opacity: The new layer opacity (0 <= opacity <= 100)
    """
    raise NotImplementedError()


def gimp_layer_set_preserve_trans(layer: Layer, lock_alpha: int):
    """
    This procedure is deprecated! Use 'gimp-layer-set-lock-alpha' instead.

    This procedure is deprecated! Use 'gimp-layer-set-lock-alpha' instead.

    :param layer: The layer
    :param lock_alpha: The new layer's lock alpha channel setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_show_mask(layer: Layer, show_mask: int):
    """
    Set the show mask setting of the specified layer.

    This procedure sets the specified layer's show mask setting. This controls whether the layer or its mask is visible. TRUE indicates that the mask should be visible. If there is no layer mask, this function will return an error.

    :param layer: The layer
    :param show_mask: The new layer's show mask setting (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_set_tattoo(item: Item, tattoo: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    :param item: The item
    :param tattoo: The new item tattoo
    """
    raise NotImplementedError()


def gimp_layer_set_visible(item: Item, visible: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    :param item: The item
    :param visible: The new item visibility (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_layer_translate(layer: Layer, offx: int, offy: int):
    """
    Translate the layer by the specified offsets.

    This procedure translates the layer by the amounts specified in the x and y arguments. These can be negative, and are considered offsets from the current position. This command only works if the layer has been added to an image. All additional layers contained in the image which have the linked flag set to TRUE w ill also be translated by the specified offsets.

    :param layer: The layer
    :param offx: Offset in x direction
    :param offy: Offset in y direction
    """
    raise NotImplementedError()


def gimp_levels(drawable: Drawable, channel: int, low_input: int, high_input: int, gamma: float, low_output: int, high_output: int):
    """
    Modifies intensity levels in the specified drawable.

    This tool allows intensity levels in the specified drawable to be remapped according to a set of parameters. The low/high input levels specify an initial mapping from the source intensities. The gamma value determines how intensities between the low and high input intensities are interpolated. A gamma value of 1.0 results in a linear interpolation. Higher gamma values result in more high-level intensities. Lower gamma values result in more low-level intensities. The low/high output levels constrain the final intensity mapping--that is, no final intensity will be lower than the low output level and no final intensity will be higher than the high output level. This tool is only valid on RGB color and grayscale images. It will not operate on indexed drawables.

    :param drawable: The drawable
    :param channel: The channel to modify { HISTOGRAM-VALUE (0), HISTOGRAM-RED (1), HISTOGRAM-GREEN (2), HISTOGRAM-BLUE (3), HISTOGRAM-ALPHA (4), HISTOGRAM-RGB (5) }
    :param low_input: Intensity of lowest input (0 <= low-input <= 255)
    :param high_input: Intensity of highest input (0 <= high-input <= 255)
    :param gamma: Gamma correction factor (0.1 <= gamma <= 10)
    :param low_output: Intensity of lowest output (0 <= low-output <= 255)
    :param high_output: Intensity of highest output (0 <= high-output <= 255)
    """
    raise NotImplementedError()


def gimp_levels_auto(drawable: Drawable):
    """
    Deprecated: Use 'gimp-levels-stretch' instead.

    Deprecated: Use 'gimp-levels-stretch' instead.

    :param drawable: The drawable
    """
    raise NotImplementedError()


def gimp_levels_stretch(drawable: Drawable):
    """
    Automatically modifies intensity levels in the specified drawable.

    This procedure allows intensity levels in the specified drawable to be remapped according to a set of guessed parameters. It is equivalent to clicking the "Auto" button in the Levels tool. This procedure is only valid on RGB color and grayscale images. It will not operate on indexed drawables.

    :param drawable: The drawable
    """
    raise NotImplementedError()


def gimp_message(message: str):
    """
    Displays a dialog box with a message.

    Displays a dialog box with a message. Useful for status or error reporting. The message must be in UTF-8 encoding.

    :param message: Message to display in the dialog
    """
    raise NotImplementedError()


def gimp_message_get_handler() -> int:
    """
    Returns the current state of where warning messages are displayed.

    This procedure returns the way g_message warnings are displayed. They can be shown in a dialog box or printed on the console where gimp was started.
    :return: handler
    """
    raise NotImplementedError()


def gimp_message_set_handler(handler: int):
    """
    Controls where warning messages are displayed.

    This procedure controls how g_message warnings are displayed. They can be shown in a dialog box or printed on the console where gimp was started.

    :param handler: The new handler type { MESSAGE-BOX (0), CONSOLE (1), ERROR-CONSOLE (2) }
    """
    raise NotImplementedError()


def gimp_online_developer_web_site():
    """
    Bookmark to the GIMP web site

    """
    raise NotImplementedError()


def gimp_online_docs_web_site():
    """
    Bookmark to the GIMP web site

    """
    raise NotImplementedError()


def gimp_online_main_web_site():
    """
    Bookmark to the GIMP web site

    """
    raise NotImplementedError()


def gimp_online_plug_in_web_site():
    """
    Bookmark to the GIMP web site

    """
    raise NotImplementedError()


def gimp_paintbrush(drawable: Drawable, fade_out: float, num_strokes: int, strokes: List[float], method: int, gradient_length: float):
    """
    Paint in the current brush with optional fade out parameter and pull colors from a gradient.

    This tool is the standard paintbrush. It draws linearly interpolated lines through the specified stroke coordinates. It operates on the specified drawable in the foreground color with the active brush. The 'fade-out' parameter is measured in pixels and allows the brush stroke to linearly fall off. The pressure is set to the maximum at the beginning of the stroke. As the distance of the stroke nears the fade-out value, the pressure will approach zero. The gradient-length is the distance to spread the gradient over. It is measured in pixels. If the gradient-length is 0, no gradient is used.

    :param drawable: The affected drawable
    :param fade_out: Fade out parameter (fade-out >= 0)
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    :param method: The paint method to use { PAINT-CONSTANT (0), PAINT-INCREMENTAL (1) }
    :param gradient_length: Length of gradient to draw (gradient-length >= 0)
    """
    raise NotImplementedError()


def gimp_paintbrush_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Paint in the current brush. The fade out parameter and pull colors from a gradient parameter are set from the paintbrush options dialog. If this dialog has not been activated then the dialog defaults will be used.

    This tool is similar to the standard paintbrush. It draws linearly interpolated lines through the specified stroke coordinates. It operates on the specified drawable in the foreground color with the active brush. The 'fade-out' parameter is measured in pixels and allows the brush stroke to linearly fall off (value obtained from the option dialog). The pressure is set to the maximum at the beginning of the stroke. As the distance of the stroke nears the fade-out value, the pressure will approach zero. The gradient-length (value obtained from the option dialog) is the distance to spread the gradient over. It is measured in pixels. If the gradient-length is 0, no gradient is used.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_palette_add_entry(name: str, entry_name: str, color: Color) -> int:
    """
    Adds a palette entry to the specified palette.

    This procedure adds an entry to the specifed palette. It returns an error if the entry palette does not exist.

    :param name: The palette name
    :param entry_name: The name of the entry
    :param color: The new entry's color color
    :return: entry_num
    """
    raise NotImplementedError()


def gimp_palette_delete(name: str):
    """
    Deletes a palette

    This procedure deletes a palette

    :param name: The palette name
    """
    raise NotImplementedError()


def gimp_palette_delete_entry(name: str, entry_num: int):
    """
    Deletes a palette entry from the specified palette.

    This procedure deletes an entry from the specifed palette. It returns an error if the entry palette does not exist.

    :param name: The palette name
    :param entry_num: The index of the added entry
    """
    raise NotImplementedError()


def gimp_palette_duplicate(name: str) -> str:
    """
    Duplicates a palette

    This procedure creates an identical palette by a different name

    :param name: The palette name
    :return: copy_name
    """
    raise NotImplementedError()


def gimp_palette_entry_get_color(name: str, entry_num: int) -> Color:
    """
    Gets the specified palette entry from the specified palette.

    This procedure retrieves the color of the zero-based entry specifed for the specified palette. It returns an error if the entry does not exist.

    :param name: The palette name
    :param entry_num: The entry to retrieve
    :return: color
    """
    raise NotImplementedError()


def gimp_palette_entry_get_name(name: str, entry_num: int) -> str:
    """
    Gets the specified palette entry from the specified palette.

    This procedure retrieves the name of the zero-based entry specifed for the specified palette. It returns an error if the entry does not exist.

    :param name: The palette name
    :param entry_num: The entry to retrieve
    :return: entry_name
    """
    raise NotImplementedError()


def gimp_palette_entry_set_color(name: str, entry_num: int, color: Color):
    """
    Sets the specified palette entry in the specified palette.

    This procedure sets the color of the zero-based entry specifed for the specified palette. It returns an error if the entry does not exist.

    :param name: The palette name
    :param entry_num: The entry to retrieve
    :param color: The new color
    """
    raise NotImplementedError()


def gimp_palette_entry_set_name(name: str, entry_num: int, entry_name: str):
    """
    Sets the specified palette entry in the specified palette.

    This procedure sets the name of the zero-based entry specifed for the specified palette. It returns an error if the entry does not exist.

    :param name: The palette name
    :param entry_num: The entry to retrieve
    :param entry_name: The new name
    """
    raise NotImplementedError()


def gimp_palette_export_css(dirname: str, string: str):
    """
    Export the active palette as a CSS stylesheet with the color entry name as their class name, and the color itself as the color attribute


    :param dirname: Folder for the output file
    :param string: The name of the file to create (if a file with this name already exist, it will be replaced)
    """
    raise NotImplementedError()


def gimp_palette_export_java(dirname: str, string: str):
    """
    Export the active palette as a java.util.Hashtable<String, Color>


    :param dirname: Folder for the output file
    :param string: The name of the file to create (if a file with this name already exist, it will be replaced)
    """
    raise NotImplementedError()


def gimp_palette_export_php(dirname: str, string: str):
    """
    Export the active palette as a PHP dictionary (name => color)


    :param dirname: Folder for the output file
    :param string: The name of the file to create (if a file with this name already exist, it will be replaced)
    """
    raise NotImplementedError()


def gimp_palette_export_python(dirname: str, string: str):
    """
    Export the active palette as a Python dictionary (name: color)


    :param dirname: Folder for the output file
    :param string: The name of the file to create (if a file with this name already exist, it will be replaced)
    """
    raise NotImplementedError()


def gimp_palette_export_text(dirname: str, string: str):
    """
    Write all the colors in a palette to a text file, one hexadecimal value per line (no names)


    :param dirname: Folder for the output file
    :param string: The name of the file to create (if a file with this name already exist, it will be replaced)
    """
    raise NotImplementedError()


def gimp_palette_get_background() -> Color:
    """
    This procedure is deprecated! Use 'gimp-context-get-background' instead.

    This procedure is deprecated! Use 'gimp-context-get-background' instead.
    :return: background
    """
    raise NotImplementedError()


def gimp_palette_get_colors(name: str) -> Tuple[int, ColorArray]:
    """
    Gets all colors from the specified palette.

    This procedure retrieves all color entries of the specified palette.

    :param name: The palette name
    :return: num_colors, colors
    """
    raise NotImplementedError()


def gimp_palette_get_columns(name: str) -> int:
    """
    Retrieves the number of columns to use to display this palette

    This procedures retrieves the prefered number of columns to use when the palette is being displayed.

    :param name: The palette name
    :return: num_columns
    """
    raise NotImplementedError()


def gimp_palette_get_foreground() -> Color:
    """
    This procedure is deprecated! Use 'gimp-context-get-foreground' instead.

    This procedure is deprecated! Use 'gimp-context-get-foreground' instead.
    :return: foreground
    """
    raise NotImplementedError()


def gimp_palette_get_info(name: str) -> int:
    """
    Retrieve information about the specified palette.

    This procedure retrieves information about the specified palette. This includes the name, and the number of colors.

    :param name: The palette name
    :return: num_colors
    """
    raise NotImplementedError()


def gimp_palette_is_editable(name: str) -> int:
    """
    Tests if palette can be edited

    Returns TRUE if you have permission to change the palette

    :param name: The palette name
    :return: editable
    """
    raise NotImplementedError()


def gimp_palette_new(name: str) -> str:
    """
    Creates a new palette

    This procedure creates a new, uninitialized palette

    :param name: The requested name of the new palette
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_palette_refresh():
    """
    This procedure is deprecated! Use 'gimp-palettes-refresh' instead.

    This procedure is deprecated! Use 'gimp-palettes-refresh' instead.
    """
    raise NotImplementedError()


def gimp_palette_rename(name: str, new_name: str) -> str:
    """
    Rename a palette

    This procedure renames a palette

    :param name: The palette name
    :param new_name: The new name of the palette
    :return: actual_name
    """
    raise NotImplementedError()


def gimp_palette_set_background(background: Color):
    """
    This procedure is deprecated! Use 'gimp-context-set-background' instead.

    This procedure is deprecated! Use 'gimp-context-set-background' instead.

    :param background: The background color
    """
    raise NotImplementedError()


def gimp_palette_set_columns(name: str, columns: int):
    """
    Sets the number of columns to use when displaying the palette

    This procedures allows to control how many colors are shown per row when the palette is being displayed. This value can only be changed if the palette is writable. The maximum allowed value is 64.

    :param name: The palette name
    :param columns: The new number of columns (0 <= columns <= 64)
    """
    raise NotImplementedError()


def gimp_palette_set_default_colors():
    """
    This procedure is deprecated! Use 'gimp-context-set-default-colors' instead.

    This procedure is deprecated! Use 'gimp-context-set-default-colors' instead.
    """
    raise NotImplementedError()


def gimp_palette_set_foreground(foreground: Color):
    """
    This procedure is deprecated! Use 'gimp-context-set-foreground' instead.

    This procedure is deprecated! Use 'gimp-context-set-foreground' instead.

    :param foreground: The foreground color
    """
    raise NotImplementedError()


def gimp_palette_swap_colors():
    """
    This procedure is deprecated! Use 'gimp-context-swap-colors' instead.

    This procedure is deprecated! Use 'gimp-context-swap-colors' instead.
    """
    raise NotImplementedError()


def gimp_palettes_close_popup(palette_callback: str):
    """
    Close the palette selection dialog.

    This procedure closes an opened palette selection dialog.

    :param palette_callback: The name of the callback registered for this pop-up
    """
    raise NotImplementedError()


def gimp_palettes_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieves a list of all of the available palettes

    This procedure returns a complete listing of available palettes. Each name returned can be used as input to the command 'gimp-context-set-palette'.

    :param filter: An optional regular expression used to filter the list
    :return: num_palettes, palette_list
    """
    raise NotImplementedError()


def gimp_palettes_get_palette() -> Tuple[str, int]:
    """
    Deprecated: Use 'gimp-context-get-palette' instead.

    Deprecated: Use 'gimp-context-get-palette' instead.
    :return: name, num_colors
    """
    raise NotImplementedError()


def gimp_palettes_get_palette_entry(name: str, entry_num: int) -> Tuple[str, int, Color]:
    """
    Deprecated: Use 'gimp-palette-entry-get-color' instead.

    Deprecated: Use 'gimp-palette-entry-get-color' instead.

    :param name: The palette name ("" means currently active palette)
    :param entry_num: The entry to retrieve
    :return: actual_name, num_colors, color
    """
    raise NotImplementedError()


def gimp_palettes_popup(palette_callback: str, popup_title: str, initial_palette: str):
    """
    Invokes the Gimp palette selection.

    This procedure opens the palette selection dialog.

    :param palette_callback: The callback PDB proc to call when palette selection is made
    :param popup_title: Title of the palette selection dialog
    :param initial_palette: The name of the palette to set as the first selected
    """
    raise NotImplementedError()


def gimp_palettes_refresh():
    """
    Refreshes current palettes. This function always succeeds.

    This procedure retrieves all palettes currently in the user's palette path and updates the palette dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_palettes_set_palette(name: str):
    """
    This procedure is deprecated! Use 'gimp-context-set-palette' instead.

    This procedure is deprecated! Use 'gimp-context-set-palette' instead.

    :param name: The name of the palette
    """
    raise NotImplementedError()


def gimp_palettes_set_popup(palette_callback: str, palette_name: str):
    """
    Sets the current palette in a palette selection dialog.

    Sets the current palette in a palette selection dialog.

    :param palette_callback: The name of the callback registered for this pop-up
    :param palette_name: The name of the palette to set as selected
    """
    raise NotImplementedError()


def gimp_parasite_attach(parasite: Parasite):
    """
    This procedure is deprecated! Use 'gimp-attach-parasite' instead.

    This procedure is deprecated! Use 'gimp-attach-parasite' instead.

    :param parasite: The parasite to attach
    """
    raise NotImplementedError()


def gimp_parasite_detach(name: str):
    """
    This procedure is deprecated! Use 'gimp-detach-parasite' instead.

    This procedure is deprecated! Use 'gimp-detach-parasite' instead.

    :param name: The name of the parasite to detach.
    """
    raise NotImplementedError()


def gimp_parasite_find(name: str) -> Parasite:
    """
    This procedure is deprecated! Use 'gimp-get-parasite' instead.

    This procedure is deprecated! Use 'gimp-get-parasite' instead.

    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_parasite_list() -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-get-parasite-list' instead.

    This procedure is deprecated! Use 'gimp-get-parasite-list' instead.
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_path_delete(image: Image, name: str):
    """
    Deprecated: Use 'gimp-image-remove-vectors' instead.

    Deprecated: Use 'gimp-image-remove-vectors' instead.

    :param image: The image to delete the path from
    :param name: The name of the path to delete.
    """
    raise NotImplementedError()


def gimp_path_get_current(image: Image) -> str:
    """
    Deprecated: Use 'gimp-image-get-active-vectors' instead.

    Deprecated: Use 'gimp-image-get-active-vectors' instead.

    :param image: The image to get the current path from
    :return: name
    """
    raise NotImplementedError()


def gimp_path_get_locked(image: Image, name: str) -> int:
    """
    Deprecated: Use 'gimp-vectors-get-linked' instead.

    Deprecated: Use 'gimp-vectors-get-linked' instead.

    :param image: The image
    :param name: The name of the path whose locked status should be obtained.
    :return: locked
    """
    raise NotImplementedError()


def gimp_path_get_point_at_dist(image: Image, distance: float) -> Tuple[int, int, float]:
    """
    Deprecated: Use 'gimp-vectors-stroke-get-point-at-dist' instead.

    Deprecated: Use 'gimp-vectors-stroke-get-point-at-dist' instead.

    :param image: The image the paths belongs to
    :param distance: The distance along the path.
    :return: x_point, y_point, slope
    """
    raise NotImplementedError()


def gimp_path_get_points(image: Image, name: str) -> Tuple[int, int, int, List[float]]:
    """
    Deprecated: Use 'gimp-vectors-stroke-get-points' instead.

    Deprecated: Use 'gimp-vectors-stroke-get-points' instead.

    :param image: The image to list the paths from
    :param name: The name of the path whose points should be listed.
    :return: path_type, path_closed, num_path_point_details, points_pairs
    """
    raise NotImplementedError()


def gimp_path_get_tattoo(image: Image, name: str) -> int:
    """
    Deprecated: Use 'gimp-vectors-get-tattoo' instead.

    Deprecated: Use 'gimp-vectors-get-tattoo' instead.

    :param image: The image
    :param name: The name of the path whose tattoo should be obtained.
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_path_import(image: Image, filename: str, merge: int, scale: int):
    """
    Deprecated: Use 'gimp-vectors-import-from-file' instead.

    Deprecated: Use 'gimp-vectors-import-from-file' instead.

    :param image: The image
    :param filename: The name of the SVG file to import.
    :param merge: Merge paths into a single vectors object. (TRUE or FALSE)
    :param scale: Scale the SVG to image dimensions. (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_path_list(image: Image) -> Tuple[int, List[str]]:
    """
    Deprecated: Use 'gimp-image-get-vectors' instead.

    Deprecated: Use 'gimp-image-get-vectors' instead.

    :param image: The image to list the paths from
    :return: num_paths, path_list
    """
    raise NotImplementedError()


def gimp_path_set_current(image: Image, name: str):
    """
    Deprecated: Use 'gimp-image-set-active-vectors' instead.

    Deprecated: Use 'gimp-image-set-active-vectors' instead.

    :param image: The image in which a path will become current
    :param name: The name of the path to make current.
    """
    raise NotImplementedError()


def gimp_path_set_locked(image: Image, name: str, locked: int):
    """
    Deprecated: Use 'gimp-vectors-set-linked' instead.

    Deprecated: Use 'gimp-vectors-set-linked' instead.

    :param image: The image
    :param name: the name of the path whose locked status should be set
    :param locked: Whether the path is locked (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_path_set_points(image: Image, name: str, ptype: int, num_path_points: int, points_pairs: List[float]):
    """
    Deprecated: Use 'gimp-vectors-stroke-new-from-points' instead.

    Deprecated: Use 'gimp-vectors-stroke-new-from-points' instead.

    :param image: The image to set the paths in
    :param name: The name of the path to create. If it exists then a unique name will be created - query the list of paths if you want to make sure that the name of the path you create is unique. This will be set as the current path.
    :param ptype: The type of the path. Currently only one type (1 = Bezier) is supported.
    :param num_path_points: The number of elements in the array, i.e. the number of points in the path * 3. Each point is made up of (x, y, type) of floats. Currently only the creation of bezier curves is allowed. The type parameter must be set to (1) to indicate a BEZIER type curve. Note that for BEZIER curves, points must be given in the following order: ACCACCAC... If the path is not closed the last control point is missed off. Points consist of three control points (control/anchor/control) so for a curve that is not closed there must be at least two points passed (2 x,y pairs). If (num_path_points/3) % 3 = 0 then the path is assumed to be closed and the points are ACCACCACCACC. (num-path-points >= 0)
    :param points_pairs: The points in the path represented as 3 floats. The first is the x pos, next is the y pos, last is the type of the pnt. The type field is dependant on the path type. For beziers (type 1 paths) the type can either be (1.0 = BEZIER_ANCHOR, 2.0 = BEZIER_CONTROL, 3.0= BEZIER_MOVE). Note all points are returned in pixel resolution.
    """
    raise NotImplementedError()


def gimp_path_set_tattoo(image: Image, name: str, tattovalue: int):
    """
    Deprecated: Use 'gimp-vectors-set-tattoo' instead.

    Deprecated: Use 'gimp-vectors-set-tattoo' instead.

    :param image: The image
    :param name: the name of the path whose tattoo should be set
    :param tattovalue: The tattoo associated with the name path. Only values returned from 'path_get_tattoo' should be used here
    """
    raise NotImplementedError()


def gimp_path_stroke_current(image: Image):
    """
    Deprecated: Use 'gimp-edit-stroke-vectors' instead.

    Deprecated: Use 'gimp-edit-stroke-vectors' instead.

    :param image: The image which contains the path to stroke
    """
    raise NotImplementedError()


def gimp_path_to_selection(image: Image, name: str, op: int, antialias: int, feather: int, feather_radius_x: float, feather_radius_y: float):
    """
    Deprecated: Use 'gimp-vectors-to-selection' instead.

    Deprecated: Use 'gimp-vectors-to-selection' instead.

    :param image: The image
    :param name: The name of the path which should be made into selection.
    :param op: The desired operation with current selection { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialias selection. (TRUE or FALSE)
    :param feather: Feather selection. (TRUE or FALSE)
    :param feather_radius_x: Feather radius x.
    :param feather_radius_y: Feather radius y.
    """
    raise NotImplementedError()


def gimp_pattern_get_info(name: str) -> Tuple[int, int, int]:
    """
    Retrieve information about the specified pattern.

    This procedure retrieves information about the specified pattern. This includes the pattern extents (width and height).

    :param name: The pattern name.
    :return: width, height, bpp
    """
    raise NotImplementedError()


def gimp_pattern_get_pixels(name: str) -> Tuple[int, int, int, int, List[int]]:
    """
    Retrieve information about the specified pattern (including pixels).

    This procedure retrieves information about the specified. This includes the pattern extents (width and height), its bpp and its pixel data.

    :param name: The pattern name.
    :return: width, height, bpp, num_color_bytes, color_bytes
    """
    raise NotImplementedError()


def gimp_patterns_close_popup(pattern_callback: str):
    """
    Close the pattern selection dialog.

    This procedure closes an opened pattern selection dialog.

    :param pattern_callback: The name of the callback registered for this pop-up
    """
    raise NotImplementedError()


def gimp_patterns_get_list(filter: str) -> Tuple[int, List[str]]:
    """
    Retrieve a complete listing of the available patterns.

    This procedure returns a complete listing of available GIMP patterns. Each name returned can be used as input to the 'gimp-context-set-pattern'.

    :param filter: An optional regular expression used to filter the list
    :return: num_patterns, pattern_list
    """
    raise NotImplementedError()


def gimp_patterns_get_pattern() -> Tuple[str, int, int]:
    """
    Deprecated: Use 'gimp-context-get-pattern' instead.

    Deprecated: Use 'gimp-context-get-pattern' instead.
    :return: name, width, height
    """
    raise NotImplementedError()


def gimp_patterns_get_pattern_data(name: str) -> Tuple[str, int, int, int, int, List[int]]:
    """
    Deprecated: Use 'gimp-pattern-get-pixels' instead.

    Deprecated: Use 'gimp-pattern-get-pixels' instead.

    :param name: The pattern name ("" means currently active pattern)
    :return: actual_name, width, height, mask_bpp, length, mask_data
    """
    raise NotImplementedError()


def gimp_patterns_list(filter: str) -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-patterns-get-list' instead.

    This procedure is deprecated! Use 'gimp-patterns-get-list' instead.

    :param filter: An optional regular expression used to filter the list
    :return: num_patterns, pattern_list
    """
    raise NotImplementedError()


def gimp_patterns_popup(pattern_callback: str, popup_title: str, initial_pattern: str):
    """
    Invokes the Gimp pattern selection.

    This procedure opens the pattern selection dialog.

    :param pattern_callback: The callback PDB proc to call when pattern selection is made
    :param popup_title: Title of the pattern selection dialog
    :param initial_pattern: The name of the pattern to set as the first selected
    """
    raise NotImplementedError()


def gimp_patterns_refresh():
    """
    Refresh current patterns. This function always succeeds.

    This procedure retrieves all patterns currently in the user's pattern path and updates all pattern dialogs accordingly.
    """
    raise NotImplementedError()


def gimp_patterns_set_pattern(name: str):
    """
    This procedure is deprecated! Use 'gimp-context-set-pattern' instead.

    This procedure is deprecated! Use 'gimp-context-set-pattern' instead.

    :param name: The name of the pattern
    """
    raise NotImplementedError()


def gimp_patterns_set_popup(pattern_callback: str, pattern_name: str):
    """
    Sets the current pattern in a pattern selection dialog.

    Sets the current pattern in a pattern selection dialog.

    :param pattern_callback: The name of the callback registered for this pop-up
    :param pattern_name: The name of the pattern to set as selected
    """
    raise NotImplementedError()


def gimp_pencil(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Paint in the current brush without sub-pixel sampling.

    This tool is the standard pencil. It draws linearly interpolated lines through the specified stroke coordinates. It operates on the specified drawable in the foreground color with the active brush. The brush mask is treated as though it contains only black and white values. Any value below half is treated as black; any above half, as white.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_perspective(drawable: Drawable, interpolation: int, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-perspective' instead.

    Deprecated: Use 'gimp-item-transform-perspective' instead.

    :param drawable: The affected drawable
    :param interpolation: Whether to use interpolation (TRUE or FALSE)
    :param x0: The new x coordinate of upper-left corner of original bounding box
    :param y0: The new y coordinate of upper-left corner of original bounding box
    :param x1: The new x coordinate of upper-right corner of original bounding box
    :param y1: The new y coordinate of upper-right corner of original bounding box
    :param x2: The new x coordinate of lower-left corner of original bounding box
    :param y2: The new y coordinate of lower-left corner of original bounding box
    :param x3: The new x coordinate of lower-right corner of original bounding box
    :param y3: The new y coordinate of lower-right corner of original bounding box
    :return: drawable
    """
    raise NotImplementedError()


def gimp_plugin_domain_register(domain_name: str, domain_path: str):
    """
    Registers a textdomain for localisation.

    This procedure adds a textdomain to the list of domains Gimp searches for strings when translating its menu entries. There is no need to call this function for plug-ins that have their strings included in the 'gimp-std-plugins' domain as that is used by default. If the compiled message catalog is not in the standard location, you may specify an absolute path to another location. This procedure can only be called in the query function of a plug-in and it has to be called before any procedure is installed.

    :param domain_name: The name of the textdomain (must be unique)
    :param domain_path: The absolute path to the compiled message catalog (may be NULL)
    """
    raise NotImplementedError()


def gimp_plugin_get_pdb_error_handler() -> int:
    """
    Retrieves the active error handler for procedure calls.

    This procedure retrieves the currently active error handler for procedure calls made by the calling plug-in. See 'gimp-plugin-set-pdb-error-handler' for details.
    :return: handler
    """
    raise NotImplementedError()


def gimp_plugin_help_register(domain_name: str, domain_uri: str):
    """
    Register a help path for a plug-in.

    This procedure registers user documentation for the calling plug-in with the GIMP help system. The domain_uri parameter points to the root directory where the plug-in help is installed. For each supported language there should be a file called 'gimp-help.xml' that maps the help IDs to the actual help files.

    :param domain_name: The XML namespace of the plug-in's help pages
    :param domain_uri: The root URI of the plug-in's help pages
    """
    raise NotImplementedError()


def gimp_plugin_icon_register(procedure_name: str, icon_type: int, icon_data_length: int, icon_data: List[int]):
    """
    Register an icon for a plug-in procedure.

    This procedure installs an icon for the given procedure.

    :param procedure_name: The procedure for which to install the icon
    :param icon_type: The type of the icon { ICON-TYPE-STOCK-ID (0), ICON-TYPE-INLINE-PIXBUF (1), ICON-TYPE-IMAGE-FILE (2) }
    :param icon_data_length: The length of 'icon-data' (icon-data-length >= 1)
    :param icon_data: The procedure's icon. The format depends on the 'icon_type' parameter
    """
    raise NotImplementedError()


def gimp_plugin_menu_branch_register(menu_path: str, menu_name: str):
    """
    Register a sub-menu.

    This procedure installs a sub-menu which does not belong to any procedure. The menu-name should be the untranslated menu label. GIMP will look up the translation in the textdomain registered for the plug-in.

    :param menu_path: The sub-menu's menu path
    :param menu_name: The name of the sub-menu
    """
    raise NotImplementedError()


def gimp_plugin_menu_register(procedure_name: str, menu_path: str):
    """
    Register an additional menu path for a plug-in procedure.

    This procedure installs an additional menu entry for the given procedure.

    :param procedure_name: The procedure for which to install the menu path
    :param menu_path: The procedure's additional menu path
    """
    raise NotImplementedError()


def gimp_plugin_set_pdb_error_handler(handler: int):
    """
    Sets an error handler for procedure calls.

    This procedure changes the way that errors in procedure calls are handled. By default GIMP will raise an error dialog if a procedure call made by a plug-in fails. Using this procedure the plug-in can change this behavior. If the error handler is set to %GIMP_PDB_ERROR_HANDLER_PLUGIN, then the plug-in is responsible for calling 'gimp-get-pdb-error' and handling the error whenever one if its procedure calls fails. It can do this by displaying the error message or by forwarding it in its own return values.

    :param handler: Who is responsible for handling procedure call errors { PDB-ERROR-HANDLER-INTERNAL (0), PDB-ERROR-HANDLER-PLUGIN (1) }
    """
    raise NotImplementedError()


def gimp_plugins_query(search_string: str) -> Tuple[int, List[str], List[str], List[str], List[str], List[int], List[str]]:
    """
    Queries the plugin database for its contents.

    This procedure queries the contents of the plugin database.

    :param search_string: If not an empty string then use this as a search pattern
    :return: num_plugins, menu_path, plugin_accelerator, plugin_location, plugin_image_type, plugin_install_time, plugin_real_name
    """
    raise NotImplementedError()


def gimp_posterize(drawable: Drawable, levels: int):
    """
    Posterize the specified drawable.

    This procedures reduces the number of shades allows in each intensity channel to the specified 'levels' parameter.

    :param drawable: The drawable
    :param levels: Levels of posterization (2 <= levels <= 255)
    """
    raise NotImplementedError()


def gimp_procedural_db_dump(filename: str):
    """
    Dumps the current contents of the procedural database

    This procedure dumps the contents of the procedural database to the specified file. The file will contain all of the information provided for each registered procedure.

    :param filename: The dump filename
    """
    raise NotImplementedError()


def gimp_procedural_db_get_data(identifier: str) -> Tuple[int, List[int]]:
    """
    Returns data associated with the specified identifier.

    This procedure returns any data which may have been associated with the specified identifier. The data is a variable length array of bytes. If no data has been associated with the identifier, an error is returned.

    :param identifier: The identifier associated with data
    :return: bytes, data
    """
    raise NotImplementedError()


def gimp_procedural_db_get_data_size(identifier: str) -> int:
    """
    Returns size of data associated with the specified identifier.

    This procedure returns the size of any data which may have been associated with the specified identifier. If no data has been associated with the identifier, an error is returned.

    :param identifier: The identifier associated with data
    :return: bytes
    """
    raise NotImplementedError()


def gimp_procedural_db_proc_arg(procedure_name: str, arg_num: int) -> Tuple[int, str, str]:
    """
    Queries the procedural database for information on the specified procedure's argument.

    This procedure returns information on the specified procedure's argument. The argument type, name, and a description are retrieved.

    :param procedure_name: The procedure name
    :param arg_num: The argument number
    :return: arg_type, arg_name, arg_desc
    """
    raise NotImplementedError()


def gimp_procedural_db_proc_exists(procedure_name: str) -> int:
    """
    Checks if the specified procedure exists in the procedural database

    This procedure checks if the specified procedure is registered in the procedural database.

    :param procedure_name: The procedure name
    :return: exists
    """
    raise NotImplementedError()


def gimp_procedural_db_proc_info(procedure_name: str) -> Tuple[str, str, str, str, str, int, int, int]:
    """
    Queries the procedural database for information on the specified procedure.

    This procedure returns information on the specified procedure. A short blurb, detailed help, author(s), copyright information, procedure type, number of input, and number of return values are returned. For specific information on each input argument and return value, use the 'gimp-procedural-db-proc-arg' and 'gimp-procedural-db-proc-val' procedures.

    :param procedure_name: The procedure name
    :return: blurb, help, author, copyright, date, proc_type, num_args, num_values
    """
    raise NotImplementedError()


def gimp_procedural_db_proc_val(procedure_name: str, val_num: int) -> Tuple[int, str, str]:
    """
    Queries the procedural database for information on the specified procedure's return value.

    This procedure returns information on the specified procedure's return value. The return value type, name, and a description are retrieved.

    :param procedure_name: The procedure name
    :param val_num: The return value number
    :return: val_type, val_name, val_desc
    """
    raise NotImplementedError()


def gimp_procedural_db_query(name: str, blurb: str, help: str, author: str, copyright: str, date: str, proc_type: str) -> Tuple[int, List[str]]:
    """
    Queries the procedural database for its contents using regular expression matching.

    This procedure queries the contents of the procedural database. It is supplied with seven arguments matching procedures on { name, blurb, help, author, copyright, date, procedure type}. This is accomplished using regular expression matching. For instance, to find all procedures with "jpeg" listed in the blurb, all seven arguments can be supplied as ".*", except for the second, which can be supplied as ".*jpeg.*". There are two return arguments for this procedure. The first is the number of procedures matching the query. The second is a concatenated list of procedure names corresponding to those matching the query. If no matching entries are found, then the returned string is NULL and the number of entries is 0.

    :param name: The regex for procedure name
    :param blurb: The regex for procedure blurb
    :param help: The regex for procedure help
    :param author: The regex for procedure author
    :param copyright: The regex for procedure copyright
    :param date: The regex for procedure date
    :param proc_type: The regex for procedure type: { 'Internal GIMP procedure', 'GIMP Plug-In', 'GIMP Extension', 'Temporary Procedure' }
    :return: num_matches, procedure_names
    """
    raise NotImplementedError()


def gimp_procedural_db_set_data(identifier: str, bytes: int, data: List[int]):
    """
    Associates the specified identifier with the supplied data.

    This procedure associates the supplied data with the provided identifier. The data may be subsequently retrieved by a call to 'procedural-db-get-data'.

    :param identifier: The identifier associated with data
    :param bytes: The number of bytes in the data (bytes >= 1)
    :param data: A byte array containing data
    """
    raise NotImplementedError()


def gimp_procedural_db_temp_name() -> str:
    """
    Generates a unique temporary PDB name.

    This procedure generates a temporary PDB entry name that is guaranteed to be unique.
    :return: temp_name
    """
    raise NotImplementedError()


def gimp_progress_cancel(progress_callback: str):
    """
    Cancels a running progress.

    This function cancels the currently running progress.

    :param progress_callback: The name of the callback registered for this progress
    """
    raise NotImplementedError()


def gimp_progress_end():
    """
    Ends the progress bar for the current plug-in.

    Ends the progress display for the current plug-in. Most plug-ins don't need to call this, they just exit when the work is done. It is only valid to call this procedure from a plug-in.
    """
    raise NotImplementedError()


def gimp_progress_get_window_handle() -> int:
    """
    Returns the native window ID of the toplevel window this plug-in's progress is displayed in.

    This function returns the native window ID of the toplevel window this plug-in's progress is displayed in.
    :return: window
    """
    raise NotImplementedError()


def gimp_progress_init(message: str, gdisplay: Display):
    """
    Initializes the progress bar for the current plug-in.

    Initializes the progress bar for the current plug-in. It is only valid to call this procedure from a plug-in.

    :param message: Message to use in the progress dialog
    :param gdisplay: GimpDisplay to update progressbar in, or -1 for a seperate window
    """
    raise NotImplementedError()


def gimp_progress_install(progress_callback: str):
    """
    Installs a progress callback for the current plug-in.

    This function installs a temporary PDB procedure which will handle all progress calls made by this plug-in and any procedure it calls. Calling this function multiple times simply replaces the old progress callbacks.

    :param progress_callback: The callback PDB proc to call
    """
    raise NotImplementedError()


def gimp_progress_pulse():
    """
    Pulses the progress bar for the current plug-in.

    Updates the progress bar for the current plug-in. It is only valid to call this procedure from a plug-in. Use this function instead of 'gimp-progress-update' if you cannot tell how much progress has been made. This usually causes the the progress bar to enter "activity mode", where a block bounces back and forth.
    """
    raise NotImplementedError()


def gimp_progress_set_text(message: str):
    """
    Changes the text in the progress bar for the current plug-in.

    This function allows to change the text in the progress bar for the current plug-in. Unlike 'gimp-progress-init' it does not change the displayed value.

    :param message: Message to use in the progress dialog
    """
    raise NotImplementedError()


def gimp_progress_uninstall(progress_callback: str):
    """
    Uninstalls the progress callback for the current plug-in.

    This function uninstalls any progress callback installed with 'gimp-progress-install' before.

    :param progress_callback: The name of the callback registered for this progress
    """
    raise NotImplementedError()


def gimp_progress_update(percentage: float):
    """
    Updates the progress bar for the current plug-in.

    Updates the progress bar for the current plug-in. It is only valid to call this procedure from a plug-in.

    :param percentage: Percentage of progress completed which must be between 0.0 and 1.0
    """
    raise NotImplementedError()


def gimp_quit(force: int):
    """
    Causes GIMP to exit gracefully.

    If there are unsaved images in an interactive GIMP session, the user will be asked for confirmation. If force is TRUE, the application is quit without querying the user to save any dirty images.

    :param force: Force GIMP to quit without asking (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_rect_select(image: Image, x: float, y: float, width: float, height: float, operation: int, feather: int, feather_radius: float):
    """
    Deprecated: Use 'gimp-image-select-rectangle' instead.

    Deprecated: Use 'gimp-image-select-rectangle' instead.

    :param image: The image
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param width: The width of the rectangle (width >= 0)
    :param height: The height of the rectangle (height >= 0)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius: Radius for feather operation (feather-radius >= 0)
    """
    raise NotImplementedError()


def gimp_register_file_handler_mime(procedure_name: str, mime_type: str):
    """
    Associates a MIME type with a file handler procedure.

    Registers a MIME type for a file handler procedure. This allows GIMP to determine the MIME type of the file opened or saved using this procedure.

    :param procedure_name: The name of the procedure to associate a MIME type with.
    :param mime_type: A single MIME type, like for example "image/jpeg".
    """
    raise NotImplementedError()


def gimp_register_load_handler(procedure_name: str, extensions: str, prefixes: str):
    """
    Registers a file load handler procedure.

    Registers a procedural database procedure to be called to load files of a particular file format.

    :param procedure_name: The name of the procedure to be used for loading
    :param extensions: comma separated list of extensions this handler can load (i.e. "jpg,jpeg")
    :param prefixes: comma separated list of prefixes this handler can load (i.e. "http:,ftp:")
    """
    raise NotImplementedError()


def gimp_register_magic_load_handler(procedure_name: str, extensions: str, prefixes: str, magics: str):
    """
    Registers a file load handler procedure.

    Registers a procedural database procedure to be called to load files of a particular file format using magic file information.

    :param procedure_name: The name of the procedure to be used for loading
    :param extensions: comma separated list of extensions this handler can load (i.e. "jpg,jpeg")
    :param prefixes: comma separated list of prefixes this handler can load (i.e. "http:,ftp:")
    :param magics: comma separated list of magic file information this handler can load (i.e. "0,string,GIF")
    """
    raise NotImplementedError()


def gimp_register_save_handler(procedure_name: str, extensions: str, prefixes: str):
    """
    Registers a file save handler procedure.

    Registers a procedural database procedure to be called to save files in a particular file format.

    :param procedure_name: The name of the procedure to be used for saving
    :param extensions: comma separated list of extensions this handler can save (i.e. "jpg,jpeg")
    :param prefixes: comma separated list of prefixes this handler can save (i.e. "http:,ftp:")
    """
    raise NotImplementedError()


def gimp_register_thumbnail_loader(load_proc: str, thumb_proc: str):
    """
    Associates a thumbnail loader with a file load procedure.

    Some file formats allow for embedded thumbnails, other file formats contain a scalable image or provide the image data in different resolutions. A file plug-in for such a format may register a special procedure that allows GIMP to load a thumbnail preview of the image. This procedure is then associated with the standard load procedure using this function.

    :param load_proc: The name of the procedure the thumbnail loader with.
    :param thumb_proc: The name of the thumbnail load procedure.
    """
    raise NotImplementedError()


def gimp_rotate(drawable: Drawable, interpolation: int, angle: float) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-rotate' instead.

    Deprecated: Use 'gimp-item-transform-rotate' instead.

    :param drawable: The affected drawable
    :param interpolation: Whether to use interpolation (TRUE or FALSE)
    :param angle: The angle of rotation (radians)
    :return: drawable
    """
    raise NotImplementedError()


def gimp_round_rect_select(image: Image, x: float, y: float, width: float, height: float, corner_radius_x: float, corner_radius_y: float, operation: int, antialias: int, feather: int, feather_radius_x: float, feather_radius_y: float):
    """
    Deprecated: Use 'gimp-image-select-round-rectangle' instead.

    Deprecated: Use 'gimp-image-select-round-rectangle' instead.

    :param image: The image
    :param x: x coordinate of upper-left corner of rectangle
    :param y: y coordinate of upper-left corner of rectangle
    :param width: The width of the rectangle (width >= 0)
    :param height: The height of the rectangle (height >= 0)
    :param corner_radius_x: The corner radius in X direction (0 <= corner-radius-x <= 262144)
    :param corner_radius_y: The corner radius in Y direction (0 <= corner-radius-y <= 262144)
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialiasing (TRUE or FALSE)
    :param feather: Feather option for selections (TRUE or FALSE)
    :param feather_radius_x: Radius for feather operation in X direction (feather-radius-x >= 0)
    :param feather_radius_y: Radius for feather operation in Y direction (feather-radius-y >= 0)
    """
    raise NotImplementedError()


def gimp_scale(drawable: Drawable, interpolation: int, x0: float, y0: float, x1: float, y1: float) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-scale' instead.

    Deprecated: Use 'gimp-item-transform-scale' instead.

    :param drawable: The affected drawable
    :param interpolation: Whether to use interpolation (TRUE or FALSE)
    :param x0: The new x coordinate of the upper-left corner of the scaled region
    :param y0: The new y coordinate of the upper-left corner of the scaled region
    :param x1: The new x coordinate of the lower-right corner of the scaled region
    :param y1: The new y coordinate of the lower-right corner of the scaled region
    :return: drawable
    """
    raise NotImplementedError()


def gimp_selection_all(image: Image):
    """
    Select all of the image.

    This procedure sets the selection mask to completely encompass the image. Every pixel in the selection channel is set to 255.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_selection_border(image: Image, radius: int):
    """
    Border the image's selection

    This procedure borders the selection. Bordering creates a new selection which is defined along the boundary of the previous selection at every point within the specified radius.

    :param image: The image
    :param radius: Radius of border (in pixels) (radius >= 0)
    """
    raise NotImplementedError()


def gimp_selection_bounds(image: Image) -> Tuple[int, int, int, int, int]:
    """
    Find the bounding box of the current selection.

    This procedure returns whether there is a selection for the specified image. If there is one, the upper left and lower right corners of the bounding box are returned. These coordinates are relative to the image. Please note that the pixel specified by the lower righthand coordinate of the bounding box is not part of the selection. The selection ends at the upper left corner of this pixel. This means the width of the selection can be calculated as (x2 - x1), its height as (y2 - y1).

    :param image: The image
    :return: non_empty, x1, y1, x2, y2
    """
    raise NotImplementedError()


def gimp_selection_clear(image: Image):
    """
    This procedure is deprecated! Use 'gimp-selection-none' instead.

    This procedure is deprecated! Use 'gimp-selection-none' instead.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_selection_combine(channel: Channel, operation: int):
    """
    Deprecated: Use 'gimp-image-select-item' instead.

    Deprecated: Use 'gimp-image-select-item' instead.

    :param channel: The channel
    :param operation: The selection operation { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    """
    raise NotImplementedError()


def gimp_selection_feather(image: Image, radius: float):
    """
    Feather the image's selection

    This procedure feathers the selection. Feathering is implemented using a gaussian blur.

    :param image: The image
    :param radius: Radius of feather (in pixels) (radius >= 0)
    """
    raise NotImplementedError()


def gimp_selection_float(drawable: Drawable, offx: int, offy: int) -> Layer:
    """
    Float the selection from the specified drawable with initial offsets as specified.

    This procedure determines the region of the specified drawable that lies beneath the current selection. The region is then cut from the drawable and the resulting data is made into a new layer which is instantiated as a floating selection. The offsets allow initial positioning of the new floating selection.

    :param drawable: The drawable from which to float selection
    :param offx: x offset for translation
    :param offy: y offset for translation
    :return: layer
    """
    raise NotImplementedError()


def gimp_selection_grow(image: Image, steps: int):
    """
    Grow the image's selection

    This procedure grows the selection. Growing involves expanding the boundary in all directions by the specified pixel amount.

    :param image: The image
    :param steps: Steps of grow (in pixels) (steps >= 0)
    """
    raise NotImplementedError()


def gimp_selection_invert(image: Image):
    """
    Invert the selection mask.

    This procedure inverts the selection mask. For every pixel in the selection channel, its new value is calculated as (255 - old-value).

    :param image: The image
    """
    raise NotImplementedError()


def gimp_selection_is_empty(image: Image) -> int:
    """
    Determine whether the selection is empty.

    This procedure returns TRUE if the selection for the specified image is empty.

    :param image: The image
    :return: is_empty
    """
    raise NotImplementedError()


def gimp_selection_layer_alpha(layer: Layer):
    """
    Deprecated: Use 'gimp-image-select-item' instead.

    Deprecated: Use 'gimp-image-select-item' instead.

    :param layer: Layer with alpha
    """
    raise NotImplementedError()


def gimp_selection_load(channel: Channel):
    """
    Deprecated: Use 'gimp-image-select-item' instead.

    Deprecated: Use 'gimp-image-select-item' instead.

    :param channel: The channel
    """
    raise NotImplementedError()


def gimp_selection_none(image: Image):
    """
    Deselect the entire image.

    This procedure deselects the entire image. Every pixel in the selection channel is set to 0.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_selection_save(image: Image) -> Channel:
    """
    Copy the selection mask to a new channel.

    This procedure copies the selection mask and stores the content in a new channel. The new channel is automatically inserted into the image's list of channels.

    :param image: The image
    :return: channel
    """
    raise NotImplementedError()


def gimp_selection_sharpen(image: Image):
    """
    Sharpen the selection mask.

    This procedure sharpens the selection mask. For every pixel in the selection channel, if the value is > 127, the new pixel is assigned a value of 255. This removes any "anti-aliasing" that might exist in the selection mask's boundary.

    :param image: The image
    """
    raise NotImplementedError()


def gimp_selection_shrink(image: Image, steps: int):
    """
    Shrink the image's selection

    This procedure shrinks the selection. Shrinking invovles trimming the existing selection boundary on all sides by the specified number of pixels.

    :param image: The image
    :param steps: Steps of shrink (in pixels) (steps >= 0)
    """
    raise NotImplementedError()


def gimp_selection_translate(image: Image, offx: int, offy: int):
    """
    Translate the selection by the specified offsets.

    This procedure actually translates the selection for the specified image by the specified offsets. Regions that are translated from beyond the bounds of the image are set to empty. Valid regions of the selection which are translated beyond the bounds of the image because of this call are lost.

    :param image: The image
    :param offx: x offset for translation
    :param offy: y offset for translation
    """
    raise NotImplementedError()


def gimp_selection_value(image: Image, x: int, y: int) -> int:
    """
    Find the value of the selection at the specified coordinates.

    This procedure returns the value of the selection at the specified coordinates. If the coordinates lie out of bounds, 0 is returned.

    :param image: The image
    :param x: x coordinate of value
    :param y: y coordinate of value
    :return: value
    """
    raise NotImplementedError()


def gimp_shear(drawable: Drawable, interpolation: int, shear_type: int, magnitude: float) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-shear' instead.

    Deprecated: Use 'gimp-item-transform-shear' instead.

    :param drawable: The affected drawable
    :param interpolation: Whether to use interpolation (TRUE or FALSE)
    :param shear_type: Type of shear { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param magnitude: The magnitude of the shear
    :return: drawable
    """
    raise NotImplementedError()


def gimp_smudge(drawable: Drawable, pressure: float, num_strokes: int, strokes: List[float]):
    """
    Smudge image with varying pressure.

    This tool simulates a smudge using the current brush. High pressure results in a greater smudge of paint while low pressure results in a lesser smudge.

    :param drawable: The affected drawable
    :param pressure: The pressure of the smudge strokes (0 <= pressure <= 100)
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_smudge_default(drawable: Drawable, num_strokes: int, strokes: List[float]):
    """
    Smudge image with varying pressure.

    This tool simulates a smudge using the current brush. It behaves exactly the same as 'gimp-smudge' except that the pressure value is taken from the smudge tool options or the options default if the tools option dialog has not been activated.

    :param drawable: The affected drawable
    :param num_strokes: Number of stroke control points (count each coordinate as 2 points) (num-strokes >= 2)
    :param strokes: Array of stroke coordinates: { s1.x, s1.y, s2.x, s2.y, ..., sn.x, sn.y }
    """
    raise NotImplementedError()


def gimp_temp_PDB_name() -> str:
    """
    This procedure is deprecated! Use 'gimp-procedural-db-temp-name' instead.

    This procedure is deprecated! Use 'gimp-procedural-db-temp-name' instead.
    :return: temp_name
    """
    raise NotImplementedError()


def gimp_temp_name(extension: str) -> str:
    """
    Generates a unique filename.

    Generates a unique filename using the temp path supplied in the user's gimprc.

    :param extension: The extension the file will have
    :return: name
    """
    raise NotImplementedError()


def gimp_text(image: Image, drawable: Drawable, x: float, y: float, text: str, border: int, antialias: int, size: float, size_type: int, foundry: str, family: str, weight: str, slant: str, set_width: str, spacing: str, registry: str, encoding: str) -> Layer:
    """
    Deprecated: Use 'gimp-text-fontname' instead.

    Deprecated: Use 'gimp-text-fontname' instead.

    :param image: The image
    :param drawable: The affected drawable: (-1 for a new text layer)
    :param x: The x coordinate for the left of the text bounding box
    :param y: The y coordinate for the top of the text bounding box
    :param text: The text to generate (in UTF-8 encoding)
    :param border: The size of the border (border >= -1)
    :param antialias: Antialiasing (TRUE or FALSE)
    :param size: The size of text in either pixels or points (size >= 0)
    :param size_type: The units of specified size { PIXELS (0), POINTS (1) }
    :param foundry: The font foundry
    :param family: The font family
    :param weight: The font weight
    :param slant: The font slant
    :param set_width: The font set-width
    :param spacing: The font spacing
    :param registry: The font registry
    :param encoding: The font encoding
    :return: text_layer
    """
    raise NotImplementedError()


def gimp_text_fontname(image: Image, drawable: Drawable, x: float, y: float, text: str, border: int, antialias: int, size: float, size_type: int, fontname: str) -> Layer:
    """
    Add text at the specified location as a floating selection or a new layer.

    This tool requires a fontname matching an installed PangoFT2 font. You can specify the fontsize in units of pixels or points, and the appropriate metric is specified using the size_type argument. The x and y parameters together control the placement of the new text by specifying the upper left corner of the text bounding box. If the specified drawable parameter is valid, the text will be created as a floating selection attached to the drawable. If the drawable parameter is not valid (-1), the text will appear as a new layer. Finally, a border can be specified around the final rendered text. The border is measured in pixels. Parameter size-type is not used and is currently ignored. If you need to display a font in points, divide the size in points by 72.0 and multiply it by the image's vertical resolution.

    :param image: The image
    :param drawable: The affected drawable: (-1 for a new text layer)
    :param x: The x coordinate for the left of the text bounding box
    :param y: The y coordinate for the top of the text bounding box
    :param text: The text to generate (in UTF-8 encoding)
    :param border: The size of the border (border >= -1)
    :param antialias: Antialiasing (TRUE or FALSE)
    :param size: The size of text in either pixels or points (size >= 0)
    :param size_type: The units of specified size { PIXELS (0), POINTS (1) }
    :param fontname: The name of the font
    :return: text_layer
    """
    raise NotImplementedError()


def gimp_text_get_extents(text: str, size: float, size_type: int, foundry: str, family: str, weight: str, slant: str, set_width: str, spacing: str, registry: str, encoding: str) -> Tuple[int, int, int, int]:
    """
    Deprecated: Use 'gimp-text-get-extents-fontname' instead.

    Deprecated: Use 'gimp-text-get-extents-fontname' instead.

    :param text: The text to generate (in UTF-8 encoding)
    :param size: The size of text in either pixels or points (size >= 0)
    :param size_type: The units of specified size { PIXELS (0), POINTS (1) }
    :param foundry: The font foundry
    :param family: The font family
    :param weight: The font weight
    :param slant: The font slant
    :param set_width: The font set-width
    :param spacing: The font spacing
    :param registry: The font registry
    :param encoding: The font encoding
    :return: width, height, ascent, descent
    """
    raise NotImplementedError()


def gimp_text_get_extents_fontname(text: str, size: float, size_type: int, fontname: str) -> Tuple[int, int, int, int]:
    """
    Get extents of the bounding box for the specified text.

    This tool returns the width and height of a bounding box for the specified text string with the specified font information. Ascent and descent for the specified font are returned as well. Parameter size-type is not used and is currently ignored. If you need to display a font in points, divide the size in points by 72.0 and multiply it by the vertical resolution of the image you are taking into account.

    :param text: The text to generate (in UTF-8 encoding)
    :param size: The size of text in either pixels or points (size >= 0)
    :param size_type: The units of specified size { PIXELS (0), POINTS (1) }
    :param fontname: The name of the font
    :return: width, height, ascent, descent
    """
    raise NotImplementedError()


def gimp_text_layer_get_antialias(layer: Layer) -> int:
    """
    Check if antialiasing is used in the text layer.

    This procedure checks if antialiasing is enabled in the specified text layer.

    :param layer: The text layer
    :return: antialias
    """
    raise NotImplementedError()


def gimp_text_layer_get_base_direction(layer: Layer) -> int:
    """
    Get the base direction used for rendering the text layer.

    This procedure returns the base direction used for rendering the text in the text layer

    :param layer: The text layer.
    :return: direction
    """
    raise NotImplementedError()


def gimp_text_layer_get_color(layer: Layer) -> Color:
    """
    Get the color of the text in a text layer.

    This procedure returns the color of the text in a text layer.

    :param layer: The text layer.
    :return: color
    """
    raise NotImplementedError()


def gimp_text_layer_get_font(layer: Layer) -> str:
    """
    Get the font from a text layer as string.

    This procedure returns the name of the font from a text layer.

    :param layer: The text layer
    :return: font
    """
    raise NotImplementedError()


def gimp_text_layer_get_font_size(layer: Layer) -> Tuple[float, int]:
    """
    Get the font size from a text layer.

    This procedure returns the size of the font which is used in a text layer. You will receive the size as a float 'font-size' in 'unit' units.

    :param layer: The text layer
    :return: font_size, unit
    """
    raise NotImplementedError()


def gimp_text_layer_get_hint_style(layer: Layer) -> int:
    """
    Get information about hinting in the specified text layer.

    This procedure provides information about the hinting that is being used in a text layer. Hinting can be optimized for fidelity or contrast or it can be turned entirely off.

    :param layer: The text layer
    :return: style
    """
    raise NotImplementedError()


def gimp_text_layer_get_hinting(layer: Layer) -> Tuple[int, int]:
    """
    Deprecated: Use 'gimp-text-layer-get-hint-style' instead.

    Deprecated: Use 'gimp-text-layer-get-hint-style' instead.

    :param layer: The text layer
    :return: hinting, autohint
    """
    raise NotImplementedError()


def gimp_text_layer_get_indent(layer: Layer) -> float:
    """
    Get the line indentation of text layer.

    This procedure returns the indentation of the first line in a text layer.

    :param layer: The text layer.
    :return: indent
    """
    raise NotImplementedError()


def gimp_text_layer_get_justification(layer: Layer) -> int:
    """
    Get the text justification information of the text layer.

    This procedure returns the alignment of the lines in the text layer relative to each other.

    :param layer: The text layer.
    :return: justify
    """
    raise NotImplementedError()


def gimp_text_layer_get_kerning(layer: Layer) -> int:
    """
    Check if kerning is used in the text layer.

    This procedure checks if kerning is enabled in the specified text layer.

    :param layer: The text layer
    :return: kerning
    """
    raise NotImplementedError()


def gimp_text_layer_get_language(layer: Layer) -> str:
    """
    Get the language used in the text layer.

    This procedure returns the language string which is set for the text in the text layer.

    :param layer: The text layer.
    :return: language
    """
    raise NotImplementedError()


def gimp_text_layer_get_letter_spacing(layer: Layer) -> float:
    """
    Get the letter spacing used in a text layer.

    This procedure returns the additional spacing between the single glyps in a text layer.

    :param layer: The text layer.
    :return: letter_spacing
    """
    raise NotImplementedError()


def gimp_text_layer_get_line_spacing(layer: Layer) -> float:
    """
    Get the spacing between lines of text.

    This procedure returns the line-spacing between lines of text in a text layer.

    :param layer: The text layer.
    :return: line_spacing
    """
    raise NotImplementedError()


def gimp_text_layer_get_markup(layer: Layer) -> str:
    """
    Get the markup from a text layer as string.

    This procedure returns the markup of the styles from a text layer. The markup will be in the form of Pango's markup - See http://www.pango.org/ for more information about Pango and its markup. Note: Setting the markup of a text layer using Pango's markup is not supported for now.

    :param layer: The text layer
    :return: markup
    """
    raise NotImplementedError()


def gimp_text_layer_get_text(layer: Layer) -> str:
    """
    Get the text from a text layer as string.

    This procedure returns the text from a text layer as a string.

    :param layer: The text layer
    :return: text
    """
    raise NotImplementedError()


def gimp_text_layer_new(image: Image, text: str, fontname: str, size: float, unit: int) -> Layer:
    """
    Creates a new text layer.

    This procedure creates a new text layer. The arguments are kept as simple as necessary for the normal case. All text attributes, however, can be modified with the appropriate gimp_text_layer_set_*() procedures. The new layer still needs to be added to the image, as this is not automatic. Add the new layer using 'gimp-image-insert-layer'.

    :param image: The image
    :param text: The text to generate (in UTF-8 encoding)
    :param fontname: The name of the font
    :param size: The size of text in either pixels or points (0 <= size <= 8192)
    :param unit: The units of specified size
    :return: layer
    """
    raise NotImplementedError()


def gimp_text_layer_resize(layer: Layer, width: float, height: float):
    """
    Resize the box of a text layer.

    This procedure changes the width and height of a text layer while keeping it as a text layer and not converting it to a bitmap like 'gimp-layer-resize' would do.

    :param layer: The text layer
    :param width: The new box width in pixels (0 <= width <= 262144)
    :param height: The new box height in pixels (0 <= height <= 262144)
    """
    raise NotImplementedError()


def gimp_text_layer_set_antialias(layer: Layer, antialias: int):
    """
    Enable/disable anti-aliasing in a text layer.

    This procedure enables or disables anti-aliasing of the text in a text layer.

    :param layer: The text layer
    :param antialias: Enable/disable antialiasing of the text (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_text_layer_set_base_direction(layer: Layer, direction: int):
    """
    Set the base direction in the text layer.

    This procedure sets the base direction used in applying the Unicode bidirectional algorithm when rendering the text.

    :param layer: The text layer
    :param direction: The base direction of the text. { TEXT-DIRECTION-LTR (0), TEXT-DIRECTION-RTL (1) }
    """
    raise NotImplementedError()


def gimp_text_layer_set_color(layer: Layer, color: Color):
    """
    Set the color of the text in the text layer.

    This procedure sets the text color in the text layer 'layer'.

    :param layer: The text layer
    :param color: The color to use for the text
    """
    raise NotImplementedError()


def gimp_text_layer_set_font(layer: Layer, font: str):
    """
    Set the font of a text layer.

    This procedure modifies the font used in the specified text layer.

    :param layer: The text layer
    :param font: The new font to use
    """
    raise NotImplementedError()


def gimp_text_layer_set_font_size(layer: Layer, font_size: float, unit: int):
    """
    Set the font size.

    This procedure changes the font size of a text layer. The size of your font will be a double 'font-size' of 'unit' units.

    :param layer: The text layer
    :param font_size: The font size (0 <= font-size <= 8192)
    :param unit: The unit to use for the font size
    """
    raise NotImplementedError()


def gimp_text_layer_set_hint_style(layer: Layer, style: int):
    """
    Control how font outlines are hinted in a text layer.

    This procedure sets the hint style for font outlines in a text layer. This controls whether to fit font outlines to the pixel grid, and if so, whether to optimize for fidelity or contrast.

    :param layer: The text layer
    :param style: The new hint style { TEXT-HINT-STYLE-NONE (0), TEXT-HINT-STYLE-SLIGHT (1), TEXT-HINT-STYLE-MEDIUM (2), TEXT-HINT-STYLE-FULL (3) }
    """
    raise NotImplementedError()


def gimp_text_layer_set_hinting(layer: Layer, hinting: int, autohint: int):
    """
    Enable/disable the use of hinting in a text layer.

    This procedure enables or disables hinting on the text of a text layer. If you enable 'auto-hint', FreeType's automatic hinter will be used and hinting information from the font will be ignored.

    :param layer: The text layer
    :param hinting: Enable/disable the use of hinting on the text (TRUE or FALSE)
    :param autohint: Force the use of the autohinter provided through FreeType (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_text_layer_set_indent(layer: Layer, indent: float):
    """
    Set the indentation of the first line in a text layer.

    This procedure sets the indentation of the first line in the text layer.

    :param layer: The text layer
    :param indent: The indentation for the first line. (-8192 <= indent <= 8192)
    """
    raise NotImplementedError()


def gimp_text_layer_set_justification(layer: Layer, justify: int):
    """
    Set the justification of the text in a text layer.

    This procedure sets the alignment of the lines in the text layer relative to each other.

    :param layer: The text layer
    :param justify: The justification for your text. { TEXT-JUSTIFY-LEFT (0), TEXT-JUSTIFY-RIGHT (1), TEXT-JUSTIFY-CENTER (2), TEXT-JUSTIFY-FILL (3) }
    """
    raise NotImplementedError()


def gimp_text_layer_set_kerning(layer: Layer, kerning: int):
    """
    Enable/disable kerning in a text layer.

    This procedure enables or disables kerning in a text layer.

    :param layer: The text layer
    :param kerning: Enable/disable kerning in the text (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_text_layer_set_language(layer: Layer, language: str):
    """
    Set the language of the text layer.

    This procedure sets the language of the text in text layer. For some scripts the language has an influence of how the text is rendered.

    :param layer: The text layer
    :param language: The new language to use for the text layer
    """
    raise NotImplementedError()


def gimp_text_layer_set_letter_spacing(layer: Layer, letter_spacing: float):
    """
    Adjust the letter spacing in a text layer.

    This procedure sets the additional spacing between the single glyphs in a text layer.

    :param layer: The text layer
    :param letter_spacing: The additional letter spacing to use. (-8192 <= letter-spacing <= 8192)
    """
    raise NotImplementedError()


def gimp_text_layer_set_line_spacing(layer: Layer, line_spacing: float):
    """
    Adjust the line spacing in a text layer.

    This procedure sets the additional spacing used between lines a text layer.

    :param layer: The text layer
    :param line_spacing: The additional line spacing to use. (-8192 <= line-spacing <= 8192)
    """
    raise NotImplementedError()


def gimp_text_layer_set_text(layer: Layer, text: str):
    """
    Set the text of a text layer.

    This procedure changes the text of a text layer.

    :param layer: The text layer
    :param text: The new text to set
    """
    raise NotImplementedError()


def gimp_threshold(drawable: Drawable, low_threshold: int, high_threshold: int):
    """
    Threshold the specified drawable.

    This procedures generates a threshold map of the specified drawable. All pixels between the values of 'low_threshold' and 'high_threshold' are replaced with white, and all other pixels with black.

    :param drawable: The drawable
    :param low_threshold: The low threshold value (0 <= low-threshold <= 255)
    :param high_threshold: The high threshold value (0 <= high-threshold <= 255)
    """
    raise NotImplementedError()


def gimp_transform_2d(drawable: Drawable, interpolation: int, source_x: float, source_y: float, scale_x: float, scale_y: float, angle: float, dest_x: float, dest_y: float) -> Drawable:
    """
    Deprecated: Use 'gimp-item-transform-2d' instead.

    Deprecated: Use 'gimp-item-transform-2d' instead.

    :param drawable: The affected drawable
    :param interpolation: Whether to use interpolation (TRUE or FALSE)
    :param source_x: X coordinate of the transformation center
    :param source_y: Y coordinate of the transformation center
    :param scale_x: Amount to scale in x direction
    :param scale_y: Amount to scale in y direction
    :param angle: The angle of rotation (radians)
    :param dest_x: X coordinate of where the centre goes
    :param dest_y: Y coordinate of where the centre goes
    :return: drawable
    """
    raise NotImplementedError()


def gimp_undo_push_group_end(image: Image):
    """
    This procedure is deprecated! Use 'gimp-image-undo-group-end' instead.

    This procedure is deprecated! Use 'gimp-image-undo-group-end' instead.

    :param image: The ID of the image in which to close an undo group
    """
    raise NotImplementedError()


def gimp_undo_push_group_start(image: Image):
    """
    This procedure is deprecated! Use 'gimp-image-undo-group-start' instead.

    This procedure is deprecated! Use 'gimp-image-undo-group-start' instead.

    :param image: The ID of the image in which to open an undo group
    """
    raise NotImplementedError()


def gimp_unit_get_abbreviation(unit_id: int) -> str:
    """
    Returns the abbreviation of the unit.

    This procedure returns the abbreviation of the unit ("in" for inches).

    :param unit_id: The unit's integer ID
    :return: abbreviation
    """
    raise NotImplementedError()


def gimp_unit_get_deletion_flag(unit_id: int) -> int:
    """
    Returns the deletion flag of the unit.

    This procedure returns the deletion flag of the unit. If this value is TRUE the unit's definition will not be saved in the user's unitrc file on gimp exit.

    :param unit_id: The unit's integer ID
    :return: deletion_flag
    """
    raise NotImplementedError()


def gimp_unit_get_digits(unit_id: int) -> int:
    """
    Returns the number of digits of the unit.

    This procedure returns the number of digits you should provide in input or output functions to get approximately the same accuracy as with two digits and inches. Note that asking for the digits of "pixels" will produce an error.

    :param unit_id: The unit's integer ID
    :return: digits
    """
    raise NotImplementedError()


def gimp_unit_get_factor(unit_id: int) -> float:
    """
    Returns the factor of the unit.

    This procedure returns the unit's factor which indicates how many units make up an inch. Note that asking for the factor of "pixels" will produce an error.

    :param unit_id: The unit's integer ID
    :return: factor
    """
    raise NotImplementedError()


def gimp_unit_get_identifier(unit_id: int) -> str:
    """
    Returns the textual identifier of the unit.

    This procedure returns the textual identifier of the unit. For built-in units it will be the english singular form of the unit's name. For user-defined units this should equal to the singular form.

    :param unit_id: The unit's integer ID
    :return: identifier
    """
    raise NotImplementedError()


def gimp_unit_get_number_of_built_in_units() -> int:
    """
    Returns the number of built-in units.

    This procedure returns the number of defined units built-in to GIMP.
    :return: num_units
    """
    raise NotImplementedError()


def gimp_unit_get_number_of_units() -> int:
    """
    Returns the number of units.

    This procedure returns the number of defined units.
    :return: num_units
    """
    raise NotImplementedError()


def gimp_unit_get_plural(unit_id: int) -> str:
    """
    Returns the plural form of the unit.

    This procedure returns the plural form of the unit.

    :param unit_id: The unit's integer ID
    :return: plural
    """
    raise NotImplementedError()


def gimp_unit_get_singular(unit_id: int) -> str:
    """
    Returns the singular form of the unit.

    This procedure returns the singular form of the unit.

    :param unit_id: The unit's integer ID
    :return: singular
    """
    raise NotImplementedError()


def gimp_unit_get_symbol(unit_id: int) -> str:
    """
    Returns the symbol of the unit.

    This procedure returns the symbol of the unit ("''" for inches).

    :param unit_id: The unit's integer ID
    :return: symbol
    """
    raise NotImplementedError()


def gimp_unit_new(identifier: str, factor: float, digits: int, symbol: str, abbreviation: str, singular: str, plural: str) -> int:
    """
    Creates a new unit and returns it's integer ID.

    This procedure creates a new unit and returns it's integer ID. Note that the new unit will have it's deletion flag set to TRUE, so you will have to set it to FALSE with 'gimp-unit-set-deletion-flag' to make it persistent.

    :param identifier: The new unit's identifier
    :param factor: The new unit's factor
    :param digits: The new unit's digits
    :param symbol: The new unit's symbol
    :param abbreviation: The new unit's abbreviation
    :param singular: The new unit's singular form
    :param plural: The new unit's plural form
    :return: unit_id
    """
    raise NotImplementedError()


def gimp_unit_set_deletion_flag(unit_id: int, deletion_flag: int):
    """
    Sets the deletion flag of a unit.

    This procedure sets the unit's deletion flag. If the deletion flag of a unit is TRUE on gimp exit, this unit's definition will not be saved in the user's unitrc.

    :param unit_id: The unit's integer ID
    :param deletion_flag: The new deletion flag of the unit (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_vectors_bezier_stroke_conicto(vectors: Vectors, stroke_id: int, x0: float, y0: float, x1: float, y1: float):
    """
    Extends a bezier stroke with a conic bezier spline.

    Extends a bezier stroke with a conic bezier spline. Actually a cubic bezier spline gets added that realizes the shape of a conic bezier spline.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param x0: The x-coordinate of the control point
    :param y0: The y-coordinate of the control point
    :param x1: The x-coordinate of the end point
    :param y1: The y-coordinate of the end point
    """
    raise NotImplementedError()


def gimp_vectors_bezier_stroke_cubicto(vectors: Vectors, stroke_id: int, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float):
    """
    Extends a bezier stroke with a cubic bezier spline.

    Extends a bezier stroke with a cubic bezier spline.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param x0: The x-coordinate of the first control point
    :param y0: The y-coordinate of the first control point
    :param x1: The x-coordinate of the second control point
    :param y1: The y-coordinate of the second control point
    :param x2: The x-coordinate of the end point
    :param y2: The y-coordinate of the end point
    """
    raise NotImplementedError()


def gimp_vectors_bezier_stroke_lineto(vectors: Vectors, stroke_id: int, x0: float, y0: float):
    """
    Extends a bezier stroke with a lineto.

    Extends a bezier stroke with a lineto.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param x0: The x-coordinate of the lineto
    :param y0: The y-coordinate of the lineto
    """
    raise NotImplementedError()


def gimp_vectors_bezier_stroke_new_ellipse(vectors: Vectors, x0: float, y0: float, radius_x: float, radius_y: float, angle: float) -> int:
    """
    Adds a bezier stroke describing an ellipse the vectors object.

    Adds a bezier stroke describing an ellipse the vectors object.

    :param vectors: The vectors object
    :param x0: The x-coordinate of the center
    :param y0: The y-coordinate of the center
    :param radius_x: The radius in x direction
    :param radius_y: The radius in y direction
    :param angle: The angle the x-axis of the ellipse (radians, counterclockwise)
    :return: stroke_id
    """
    raise NotImplementedError()


def gimp_vectors_bezier_stroke_new_moveto(vectors: Vectors, x0: float, y0: float) -> int:
    """
    Adds a bezier stroke with a single moveto to the vectors object.

    Adds a bezier stroke with a single moveto to the vectors object.

    :param vectors: The vectors object
    :param x0: The x-coordinate of the moveto
    :param y0: The y-coordinate of the moveto
    :return: stroke_id
    """
    raise NotImplementedError()


def gimp_vectors_copy(vectors: Vectors) -> Vectors:
    """
    Copy a vectors object.

    This procedure copies the specified vectors object and returns the copy.

    :param vectors: The vectors object to copy
    :return: vectors_copy
    """
    raise NotImplementedError()


def gimp_vectors_export_to_file(image: Image, filename: str, vectors: Vectors):
    """
    save a path as an SVG file.

    This procedure creates an SVG file to save a Vectors object, that is, a path. The resulting file can be edited using a vector graphics application, or later reloaded into GIMP. If you pass 0 as the 'vectors' argument, then all paths in the image will be exported.

    :param image: The image
    :param filename: The name of the SVG file to create.
    :param vectors: The vectors object to be saved, or 0 for all in the image
    """
    raise NotImplementedError()


def gimp_vectors_export_to_string(image: Image, vectors: Vectors) -> str:
    """
    Save a path as an SVG string.

    This procedure works like 'gimp-vectors-export-to-file' but creates a string rather than a file. The contents are a NUL-terminated string that holds a complete XML document. If you pass 0 as the 'vectors' argument, then all paths in the image will be exported.

    :param image: The image
    :param vectors: The vectors object to save, or 0 for all in the image
    :return: string
    """
    raise NotImplementedError()


def gimp_vectors_get_image(item: Item) -> Image:
    """
    This procedure is deprecated! Use 'gimp-item-get-image' instead.

    This procedure is deprecated! Use 'gimp-item-get-image' instead.

    :param item: The item
    :return: image
    """
    raise NotImplementedError()


def gimp_vectors_get_linked(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    This procedure is deprecated! Use 'gimp-item-get-linked' instead.

    :param item: The item
    :return: linked
    """
    raise NotImplementedError()


def gimp_vectors_get_name(item: Item) -> str:
    """
    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    This procedure is deprecated! Use 'gimp-item-get-name' instead.

    :param item: The item
    :return: name
    """
    raise NotImplementedError()


def gimp_vectors_get_strokes(vectors: Vectors) -> Tuple[int, List[int]]:
    """
    List the strokes associated with the passed path.

    Returns an Array with the stroke-IDs associated with the passed path.

    :param vectors: The vectors object
    :return: num_strokes, stroke_ids
    """
    raise NotImplementedError()


def gimp_vectors_get_tattoo(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-get-tattoo' instead.

    :param item: The item
    :return: tattoo
    """
    raise NotImplementedError()


def gimp_vectors_get_visible(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    This procedure is deprecated! Use 'gimp-item-get-visible' instead.

    :param item: The item
    :return: visible
    """
    raise NotImplementedError()


def gimp_vectors_import_from_file(image: Image, filename: str, merge: int, scale: int) -> Tuple[int, List[int]]:
    """
    Import paths from an SVG file.

    This procedure imports paths from an SVG file. SVG elements other than paths and basic shapes are ignored.

    :param image: The image
    :param filename: The name of the SVG file to import.
    :param merge: Merge paths into a single vectors object. (TRUE or FALSE)
    :param scale: Scale the SVG to image dimensions. (TRUE or FALSE)
    :return: num_vectors, vectors_ids
    """
    raise NotImplementedError()


def gimp_vectors_import_from_string(image: Image, string: str, length: int, merge: int, scale: int) -> Tuple[int, List[int]]:
    """
    Import paths from an SVG string.

    This procedure works like 'gimp-vectors-import-from-file' but takes a string rather than reading the SVG from a file. This allows you to write scripts that generate SVG and feed it to GIMP.

    :param image: The image
    :param string: A string that must be a complete and valid SVG document.
    :param length: Number of bytes in string or -1 if the string is NULL terminated.
    :param merge: Merge paths into a single vectors object. (TRUE or FALSE)
    :param scale: Scale the SVG to image dimensions. (TRUE or FALSE)
    :return: num_vectors, vectors_ids
    """
    raise NotImplementedError()


def gimp_vectors_is_valid(item: Item) -> int:
    """
    This procedure is deprecated! Use 'gimp-item-is-valid' instead.

    This procedure is deprecated! Use 'gimp-item-is-valid' instead.

    :param item: The item to check
    :return: valid
    """
    raise NotImplementedError()


def gimp_vectors_new(image: Image, name: str) -> Vectors:
    """
    Creates a new empty vectors object.

    Creates a new empty vectors object. The vectors object needs to be added to the image using 'gimp-image-insert-vectors'.

    :param image: The image
    :param name: the name of the new vector object.
    :return: vectors
    """
    raise NotImplementedError()


def gimp_vectors_new_from_text_layer(image: Image, layer: Layer) -> Vectors:
    """
    Creates a new vectors object from a text layer.

    Creates a new vectors object from a text layer. The vectors object needs to be added to the image using 'gimp-image-insert-vectors'.

    :param image: The image.
    :param layer: The text layer.
    :return: vectors
    """
    raise NotImplementedError()


def gimp_vectors_parasite_attach(item: Item, parasite: Parasite):
    """
    This procedure is deprecated! Use 'gimp-item-attach-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-attach-parasite' instead.

    :param item: The item
    :param parasite: The parasite to attach to the item
    """
    raise NotImplementedError()


def gimp_vectors_parasite_detach(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-detach-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-detach-parasite' instead.

    :param item: The item
    :param name: The name of the parasite to detach from the item.
    """
    raise NotImplementedError()


def gimp_vectors_parasite_find(item: Item, name: str) -> Parasite:
    """
    This procedure is deprecated! Use 'gimp-item-get-parasite' instead.

    This procedure is deprecated! Use 'gimp-item-get-parasite' instead.

    :param item: The item
    :param name: The name of the parasite to find
    :return: parasite
    """
    raise NotImplementedError()


def gimp_vectors_parasite_list(item: Item) -> Tuple[int, List[str]]:
    """
    This procedure is deprecated! Use 'gimp-item-get-parasite-list' instead.

    This procedure is deprecated! Use 'gimp-item-get-parasite-list' instead.

    :param item: The item
    :return: num_parasites, parasites
    """
    raise NotImplementedError()


def gimp_vectors_remove_stroke(vectors: Vectors, stroke_id: int):
    """
    remove the stroke from a vectors object.

    Remove the stroke from a vectors object.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    """
    raise NotImplementedError()


def gimp_vectors_set_linked(item: Item, linked: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    This procedure is deprecated! Use 'gimp-item-set-linked' instead.

    :param item: The item
    :param linked: The new item linked state (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_vectors_set_name(item: Item, name: str):
    """
    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    This procedure is deprecated! Use 'gimp-item-set-name' instead.

    :param item: The item
    :param name: The new item name
    """
    raise NotImplementedError()


def gimp_vectors_set_tattoo(item: Item, tattoo: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    This procedure is deprecated! Use 'gimp-item-set-tattoo' instead.

    :param item: The item
    :param tattoo: The new item tattoo
    """
    raise NotImplementedError()


def gimp_vectors_set_visible(item: Item, visible: int):
    """
    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    This procedure is deprecated! Use 'gimp-item-set-visible' instead.

    :param item: The item
    :param visible: The new item visibility (TRUE or FALSE)
    """
    raise NotImplementedError()


def gimp_vectors_stroke_close(vectors: Vectors, stroke_id: int):
    """
    closes the specified stroke.

    Closes the specified stroke.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    """
    raise NotImplementedError()


def gimp_vectors_stroke_flip(vectors: Vectors, stroke_id: int, flip_type: int, axis: float):
    """
    flips the given stroke.

    Rotates the given stroke around given center by angle (in degrees).

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param flip_type: Flip orientation, either vertical or horizontal { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param axis: axis coordinate about which to flip, in pixels
    """
    raise NotImplementedError()


def gimp_vectors_stroke_flip_free(vectors: Vectors, stroke_id: int, x1: float, y1: float, x2: float, y2: float):
    """
    flips the given stroke about an arbitrary axis.

    Flips the given stroke about an arbitrary axis. Axis is defined by two coordinates in the image (in pixels), through which the flipping axis passes.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param x1: X coordinate of the first point of the flipping axis
    :param y1: Y coordinate of the first point of the flipping axis
    :param x2: X coordinate of the second point of the flipping axis
    :param y2: Y coordinate of the second point of the flipping axis
    """
    raise NotImplementedError()


def gimp_vectors_stroke_get_length(vectors: Vectors, stroke_id: int, precision: float) -> float:
    """
    Measure the length of the given stroke.

    Measure the length of the given stroke.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param precision: The precision used for the approximation
    :return: length
    """
    raise NotImplementedError()


def gimp_vectors_stroke_get_point_at_dist(vectors: Vectors, stroke_id: int, dist: float, precision: float) -> Tuple[float, float, float, int]:
    """
    Get point at a specified distance along the stroke.

    This will return the x,y position of a point at a given distance along the stroke. The distance will be obtained by first digitizing the curve internally and then walking along the curve. For a closed stroke the start of the path is the first point on the path that was created. This might not be obvious. If the stroke is not long enough, a "valid" flag will be FALSE.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param dist: The given distance.
    :param precision: The precision used for the approximation
    :return: x_point, y_point, slope, valid
    """
    raise NotImplementedError()


def gimp_vectors_stroke_get_points(vectors: Vectors, stroke_id: int) -> Tuple[int, int, List[float], int]:
    """
    returns the control points of a stroke.

    returns the control points of a stroke. The interpretation of the coordinates returned depends on the type of the stroke. For Gimp 2.4 this is always a bezier stroke, where the coordinates are the control points.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :return: type, num_points, controlpoints, closed
    """
    raise NotImplementedError()


def gimp_vectors_stroke_interpolate(vectors: Vectors, stroke_id: int, precision: float) -> Tuple[int, List[float], int]:
    """
    returns polygonal approximation of the stroke.

    returns polygonal approximation of the stroke.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param precision: The precision used for the approximation
    :return: num_coords, coords, closed
    """
    raise NotImplementedError()


def gimp_vectors_stroke_new_from_points(vectors: Vectors, type: int, num_points: int, controlpoints: List[float], closed: int) -> int:
    """
    Adds a stroke of a given type to the vectors object.

    Adds a stroke of a given type to the vectors object. The coordinates of the control points can be specified. For now only strokes of the type GIMP_VECTORS_STROKE_TYPE_BEZIER are supported. The control points are specified as a pair of float values for the x- and y-coordinate. The Bezier stroke type needs a multiple of three control points. Each Bezier segment endpoint (anchor, A) has two additional control points (C) associated. They are specified in the order CACCACCAC...

    :param vectors: The vectors object
    :param type: type of the stroke (always GIMP_VECTORS_STROKE_TYPE_BEZIER for now). { VECTORS-STROKE-TYPE-BEZIER (0) }
    :param num_points: The number of elements in the array, i.e. the number of controlpoints in the stroke * 2 (x- and y-coordinate). (num-points >= 0)
    :param controlpoints: List of the x- and y-coordinates of the control points.
    :param closed: Whether the stroke is to be closed or not. (TRUE or FALSE)
    :return: stroke_id
    """
    raise NotImplementedError()


def gimp_vectors_stroke_rotate(vectors: Vectors, stroke_id: int, center_x: float, center_y: float, angle: float):
    """
    rotates the given stroke.

    Rotates the given stroke around given center by angle (in degrees).

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param center_x: X coordinate of the rotation center
    :param center_y: Y coordinate of the rotation center
    :param angle: angle to rotate about
    """
    raise NotImplementedError()


def gimp_vectors_stroke_scale(vectors: Vectors, stroke_id: int, scale_x: float, scale_y: float):
    """
    scales the given stroke.

    Scale the given stroke.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param scale_x: Scale factor in x direction
    :param scale_y: Scale factor in y direction
    """
    raise NotImplementedError()


def gimp_vectors_stroke_translate(vectors: Vectors, stroke_id: int, off_x: int, off_y: int):
    """
    translate the given stroke.

    Translate the given stroke.

    :param vectors: The vectors object
    :param stroke_id: The stroke ID
    :param off_x: Offset in x direction
    :param off_y: Offset in y direction
    """
    raise NotImplementedError()


def gimp_vectors_to_selection(vectors: Vectors, operation: int, antialias: int, feather: int, feather_radius_x: float, feather_radius_y: float):
    """
    Deprecated: Use 'gimp-image-select-item' instead.

    Deprecated: Use 'gimp-image-select-item' instead.

    :param vectors: The vectors object to render to the selection
    :param operation: The desired operation with current selection { CHANNEL-OP-ADD (0), CHANNEL-OP-SUBTRACT (1), CHANNEL-OP-REPLACE (2), CHANNEL-OP-INTERSECT (3) }
    :param antialias: Antialias selection. (TRUE or FALSE)
    :param feather: Feather selection. (TRUE or FALSE)
    :param feather_radius_x: Feather radius x.
    :param feather_radius_y: Feather radius y.
    """
    raise NotImplementedError()


def gimp_version() -> str:
    """
    Returns the host GIMP version.

    This procedure returns the version number of the currently running GIMP.
    :return: version
    """
    raise NotImplementedError()


def gimp_xcf_load(dummy_param: int, filename: str, raw_filename: str) -> Image:
    """
    Loads file saved in the .xcf file format

    The XCF file format has been designed specifically for loading and saving tiled and layered images in GIMP. This procedure will load the specified file.

    :param dummy_param: Dummy parameter
    :param filename: The name of the file to load, in the on-disk character set and encoding
    :param raw_filename: The basename of the file, in UTF-8
    :return: image
    """
    raise NotImplementedError()


def gimp_xcf_save(dummy_param: int, image: Image, drawable: Drawable, filename: str, raw_filename: str):
    """
    Saves file in the .xcf file format

    The XCF file format has been designed specifically for loading and saving tiled and layered images in GIMP. This procedure will save the specified image in the xcf file format.

    :param dummy_param: Dummy parameter
    :param image: Input image
    :param drawable: Active drawable of input image
    :param filename: The name of the file to save the image in, in the on-disk character set and encoding
    :param raw_filename: The basename of the file, in UTF-8
    """
    raise NotImplementedError()


def plug_in_alienmap2(image: Image, drawable: Drawable, redfrequency: float, redangle: float, greenfrequency: float, greenangle: float, bluefrequency: float, blueangle: float, colormodel: int, redmode: int, greenmode: int, bluemode: int):
    """
    Alter colors in various psychedelic ways

    No help yet. Just try it and you'll see!

    :param image: Input image
    :param drawable: Input drawable
    :param redfrequency: Red/hue component frequency factor
    :param redangle: Red/hue component angle factor (0-360)
    :param greenfrequency: Green/saturation component frequency factor
    :param greenangle: Green/saturation component angle factor (0-360)
    :param bluefrequency: Blue/luminance component frequency factor
    :param blueangle: Blue/luminance component angle factor (0-360)
    :param colormodel: Color model { RGB-MODEL (0), HSL-MODEL (1) }
    :param redmode: Red/hue application mode { TRUE, FALSE }
    :param greenmode: Green/saturation application mode { TRUE, FALSE }
    :param bluemode: Blue/luminance application mode { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_align_layers(image: Image, drawable: Drawable, link_after_alignment: int, use_bottom: int):
    """
    Align all visible layers of the image

    Align visible layers

    :param image: Input image
    :param drawable: Input drawable (not used)
    :param link_after_alignment: Link the visible layers after alignment { TRUE, FALSE }
    :param use_bottom: use the bottom layer as the base of alignment { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_animationoptimize(image: Image, drawable: Drawable) -> Image:
    """
    Modify image to reduce size when saved as GIF animation

    This procedure applies various optimizations to a GIMP layer-based animation in an attempt to reduce the final file size.  If a frame of the animation can use the 'combine' mode, this procedure attempts to maximize the number of ajdacent pixels having the same color, which improves the compression for some image formats such as GIF or MNG.

    :param image: Input image
    :param drawable: Input drawable (unused)
    :return: result
    """
    raise NotImplementedError()


def plug_in_animationoptimize_diff(image: Image, drawable: Drawable) -> Image:
    """
    Reduce file size where combining layers is possible

    This procedure applies various optimizations to a GIMP layer-based animation in an attempt to reduce the final file size.  If a frame of the animation can use the 'combine' mode, this procedure uses a simple difference between the frames.

    :param image: Input image
    :param drawable: Input drawable (unused)
    :return: result
    """
    raise NotImplementedError()


def plug_in_animationplay(image: Image, drawable: Drawable):
    """
    Preview a GIMP layer-based animation


    :param image: Input image
    :param drawable: Input drawable (unused)
    """
    raise NotImplementedError()


def plug_in_animationunoptimize(image: Image, drawable: Drawable) -> Image:
    """
    Remove optimization to make editing easier

    This procedure 'simplifies' a GIMP layer-based animation that has been optimized for animation. This makes editing the animation much easier.

    :param image: Input image
    :param drawable: Input drawable (unused)
    :return: result
    """
    raise NotImplementedError()


def plug_in_antialias(image: Image, drawable: Drawable):
    """
    Antialias using the Scale3X edge-extrapolation algorithm

    Help - write me

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_apply_canvas(image: Image, drawable: Drawable, direction: int, depth: int):
    """
    Add a canvas texture to the image

    This function applies a canvas texture map to the drawable.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param direction: Light direction (0 - 3)
    :param depth: Texture depth (1 - 50)
    """
    raise NotImplementedError()


def plug_in_applylens(image: Image, drawable: Drawable, refraction: float, keep_surroundings: int, set_background: int, set_transparent: int):
    """
    Simulate an elliptical lens over the image

    This plug-in uses Snell's law to draw an ellipsoid lens over the image

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param refraction: Lens refraction index
    :param keep_surroundings: Keep lens surroundings { TRUE, FALSE }
    :param set_background: Set lens surroundings to BG value { TRUE, FALSE }
    :param set_transparent: Set lens surroundings transparent { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_autocrop(image: Image, drawable: Drawable):
    """
    Remove empty borders from the image

    Crop the active layer of the input "image" based on empty borders of the input "drawable". The input drawable serves as a base for detecting cropping extents (transparency or background color), and is not necessarily the cropped layer (the current active layer).

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_autocrop_layer(image: Image, drawable: Drawable):
    """
    Remove empty borders from the layer


    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_autostretch_hsv(image: Image, drawable: Drawable):
    """
    Stretch image contrast to cover the maximum possible range

    This simple plug-in does an automatic contrast stretch.  For each channel in the image, it finds the minimum and maximum values... it uses those values to stretch the individual histograms to the full contrast range.  For some images it may do just what you want; for others it may be total crap :).  This version differs from Contrast Autostretch in that it works in HSV space, and preserves hue.

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_blinds(image: Image, drawable: Drawable, angle_dsp: int, num_segments: int, orientation: int, bg_transparent: int):
    """
    Simulate an image painted on window blinds

    More here later

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param angle_dsp: Angle of Displacement
    :param num_segments: Number of segments in blinds
    :param orientation: The orientation { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param bg_transparent: Background transparent { FALSE, TRUE }
    """
    raise NotImplementedError()


def plug_in_blur(image: Image, drawable: Drawable):
    """
    Simple blur, fast but not very strong

    This plug-in blurs the specified drawable, using a 3x3 blur. Indexed images are not supported.

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_borderaverage(image: Image, drawable: Drawable, thickness: int, bucket_exponent: int) -> Color:
    """
    Set foreground to the average color of the image border


    :param image: Input image (unused)
    :param drawable: Input drawable
    :param thickness: Border size to take in count
    :param bucket_exponent: Bits for bucket size (default=4: 16 Levels)
    :return: borderaverage
    """
    raise NotImplementedError()


def plug_in_bump_map(image: Image, drawable: Drawable, bumpmap: Drawable, azimuth: float, elevation: float, depth: int, xofs: int, yofs: int, waterlevel: int, ambient: int, compensate: int, invert: int, type: int):
    """
    Create an embossing effect using a bump map

    This plug-in uses the algorithm described by John Schlag, "Fast Embossing Effects on Raster Image Data" in Graphics GEMS IV (ISBN 0-12-336155-9). It takes a drawable to be applied as a bump map to another image and produces a nice embossing effect.

    :param image: Input image
    :param drawable: Input drawable
    :param bumpmap: Bump map drawable
    :param azimuth: Azimuth
    :param elevation: Elevation
    :param depth: Depth
    :param xofs: X offset
    :param yofs: Y offset
    :param waterlevel: Level that full transparency should represent
    :param ambient: Ambient lighting factor
    :param compensate: Compensate for darkening { TRUE, FALSE }
    :param invert: Invert bumpmap { TRUE, FALSE }
    :param type: Type of map { LINEAR (0), SPHERICAL (1), SINUSOIDAL (2) }
    """
    raise NotImplementedError()


def plug_in_bump_map_tiled(image: Image, drawable: Drawable, bumpmap: Drawable, azimuth: float, elevation: float, depth: int, xofs: int, yofs: int, waterlevel: int, ambient: int, compensate: int, invert: int, type: int):
    """
    Create an embossing effect using a tiled image as a bump map

    This plug-in uses the algorithm described by John Schlag, "Fast Embossing Effects on Raster Image Data" in Graphics GEMS IV (ISBN 0-12-336155-9). It takes a drawable to be tiled and applied as a bump map to another image and produces a nice embossing effect.

    :param image: Input image
    :param drawable: Input drawable
    :param bumpmap: Bump map drawable
    :param azimuth: Azimuth
    :param elevation: Elevation
    :param depth: Depth
    :param xofs: X offset
    :param yofs: Y offset
    :param waterlevel: Level that full transparency should represent
    :param ambient: Ambient lighting factor
    :param compensate: Compensate for darkening { TRUE, FALSE }
    :param invert: Invert bumpmap { TRUE, FALSE }
    :param type: Type of map { LINEAR (0), SPHERICAL (1), SINUSOIDAL (2) }
    """
    raise NotImplementedError()


def plug_in_c_astretch(image: Image, drawable: Drawable):
    """
    Stretch contrast to cover the maximum possible range

    This simple plug-in does an automatic contrast stretch.  For each channel in the image, it finds the minimum and maximum values... it uses those values to stretch the individual histograms to the full contrast range.  For some images it may do just what you want; for others it may not work that well.

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_cartoon(image: Image, drawable: Drawable, mask_radius: float, pct_black: float):
    """
    Simulate a cartoon by enhancing edges

    Propagates dark values in an image based on each pixel's relative darkness to a neighboring average. The idea behind this filter is to give the look of a black felt pen drawing subsequently shaded with color. This is achieved by darkening areas of the image which are measured to be darker than a neighborhood average. In this way, sufficiently large shifts in intensity are darkened to black. The rate at which they are darkened to black is determined by the second pct_black parameter. The mask_radius parameter controls the size of the pixel neighborhood over which the average intensity is computed and then compared to each pixel in the neighborhood to decide whether or not to darken it to black. Large values for mask_radius result in very thick black areas bordering the shaded regions of color and much less detail for black areas everywhere including inside regions of color. Small values result in more subtle pen strokes and detail everywhere. Small values for the pct_black make the blend from the color regions to the black border lines smoother and the lines themselves thinner and less noticable; larger values achieve the opposite effect.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param mask_radius: Cartoon mask radius (radius of pixel neighborhood)
    :param pct_black: Percentage of darkened pixels to set to black (0.0 - 1.0)
    """
    raise NotImplementedError()


def plug_in_ccanalyze(image: Image, drawable: Drawable) -> int:
    """
    Analyze the set of colors in the image

    Analyze colorcube and print some information about the current image (also displays a color-histogram)

    :param image: Input image
    :param drawable: Input drawable
    :return: num_colors
    """
    raise NotImplementedError()


def plug_in_checkerboard(image: Image, drawable: Drawable, check_mode: int, check_size: int):
    """
    Create a checkerboard pattern

    More here later

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param check_mode: Check mode { REGULAR (0), PSYCHOBILY (1) }
    :param check_size: Size of the checks
    """
    raise NotImplementedError()


def plug_in_cml_explorer(ru__mode: int, image: Image, drawable: Drawable, parameter_filename: str):
    """
    Create abstract Coupled-Map Lattice patterns

    Make an image of Coupled-Map Lattice (CML). CML is a kind of Cellula Automata on continuous (value) domain. In GIMP_RUN_NONINTERACTIVE, the name of a prameter file is passed as the 4th arg. You can control CML_explorer via parameter file.

    :param ru__mode: The run mode { RUN-INTERACTIVE (0), RUN-NONINTERACTIVE (1) }
    :param image: Input image (not used)
    :param drawable: Input drawable
    :param parameter_filename: The name of parameter file. CML_explorer makes an image with its settings.
    """
    raise NotImplementedError()


def plug_in_color_enhance(image: Image, drawable: Drawable):
    """
    Stretch color saturation to cover maximum possible range

    This simple plug-in does an automatic saturation stretch.  For each channel in the image, it finds the minimum and maximum values... it uses those values to stretch the individual histograms to the full range.  For some images it may do just what you want; for others it may not work that well.  This version differs from Contrast Autostretch in that it works in HSV space, and preserves hue.

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_colorify(image: Image, drawable: Drawable, color: Color):
    """
    Replace all colors with shades of a specified color

    Makes an average of the RGB channels and uses it to set the color

    :param image: Input image
    :param drawable: Input drawable
    :param color: Color to apply
    """
    raise NotImplementedError()


def plug_in_colormap_remap(image: Image, drawable: Drawable, num_colors: int, map: List[int]):
    """
    Rearrange the colormap

    This procedure takes an indexed image and lets you alter the positions of colors in the colormap without visually changing the image.

    :param image: Input image
    :param drawable: Input drawable
    :param num_colors: Length of 'map' argument (should be equal to colormap size)
    :param map: Remap array for the colormap
    """
    raise NotImplementedError()


def plug_in_colormap_swap(image: Image, drawable: Drawable, index1: int, index2: int):
    """
    Swap two colors in the colormap

    This procedure takes an indexed image and lets you swap the positions of two colors in the colormap without visually changing the image.

    :param image: Input image
    :param drawable: Input drawable
    :param index1: First index in the colormap
    :param index2: Second (other) index in the colormap
    """
    raise NotImplementedError()


def plug_in_colors_channel_mixer(image: Image, drawable: Drawable, monochrome: int, rr_gain: float, rg_gain: float, rb_gain: float, gr_gain: float, gg_gain: float, gb_gain: float, br_gain: float, bg_gain: float, bb_gain: float):
    """
    Alter colors by mixing RGB Channels

    This plug-in mixes the RGB channels.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param monochrome: Monochrome { TRUE, FALSE }
    :param rr_gain: Set the red gain for the red channel
    :param rg_gain: Set the green gain for the red channel
    :param rb_gain: Set the blue gain for the red channel
    :param gr_gain: Set the red gain for the green channel
    :param gg_gain: Set the green gain for the green channel
    :param gb_gain: Set the blue gain for the green channel
    :param br_gain: Set the red gain for the blue channel
    :param bg_gain: Set the green gain for the blue channel
    :param bb_gain: Set the blue gain for the blue channel
    """
    raise NotImplementedError()


def plug_in_colortoalpha(image: Image, drawable: Drawable, color: Color):
    """
    Convert a specified color to transparency

    This replaces as much of a given color as possible in each pixel with a corresponding amount of alpha, then readjusts the color accordingly.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param color: Color to remove
    """
    raise NotImplementedError()


def plug_in_compose(image1: Image, drawable: Drawable, image2: Image, image3: Image, image4: Image, compose_type: str) -> Image:
    """
    Create an image using multiple gray images as color channels

    This function creates a new image from multiple gray images

    :param image1: First input image
    :param drawable: Input drawable (not used)
    :param image2: Second input image
    :param image3: Third input image
    :param image4: Fourth input image
    :param compose_type: What to compose: "RGB", "RGBA", "HSV", "HSL", "CMY", "CMYK", "LAB", "YCbCr_ITU_R470", "YCbCr_ITU_R709", "YCbCr_ITU_R470_256", "YCbCr_ITU_R709_256"
    :return: new_image
    """
    raise NotImplementedError()


def plug_in_convmatrix(image: Image, drawable: Drawable, argc_matrix: int, matrix: List[float], alpha_alg: int, divisor: float, offset: float, argc_channels: int, channels: List[int], bmode: int):
    """
    Apply a generic 5x5 convolution matrix


    :param image: Input image (unused)
    :param drawable: Input drawable
    :param argc_matrix: The number of elements in the following array. Should be always 25.
    :param matrix: The 5x5 convolution matrix
    :param alpha_alg: Enable weighting by alpha channel
    :param divisor: Divisor
    :param offset: Offset
    :param argc_channels: The number of elements in following array. Should be always 5.
    :param channels: Mask of the channels to be filtered
    :param bmode: Mode for treating image borders { EXTEND (0), WRAP (1), CLEAR (2) }
    """
    raise NotImplementedError()


def plug_in_cubism(image: Image, drawable: Drawable, tile_size: float, tile_saturation: float, bg_color: int):
    """
    Convert the image into randomly rotated square blobs

    Help not yet written for this plug-in

    :param image: Input image
    :param drawable: Input drawable
    :param tile_size: Average diameter of each tile (in pixels)
    :param tile_saturation: Expand tiles by this amount
    :param bg_color: Background color { BLACK (0), BG (1) }
    """
    raise NotImplementedError()


def plug_in_curve_bend(image: Image, drawable: Drawable, rotation: float, smoothing: int, antialias: int, work_on_copy: int, curve_type: int, argc_upper_point_x: int, upper_point_x: List[float], argc_upper_point_y: int, upper_point_y: List[float], argc_lower_point_x: int, lower_point_x: List[float], argc_lower_point_y: int, lower_point_y: List[float], argc_upper_val_y: int, upper_val_y: List[int], argc_lower_val_y: int, lower_val_y: List[int]) -> Layer:
    """
    Bend the image using two control curves

    This plug-in does bend the active layer If there is a current selection it is copied to floating selection and the curve_bend distortion is done on the floating selection. If work_on_copy parameter is TRUE, the curve_bend distortion is done on a copy of the active layer (or floating selection). The upper and lower edges are bent in shape of 2 spline curves. both (upper and lower) curves are determined by upto 17 points or by 256 Y-Values if curve_type == 1 (freehand mode) If rotation is not 0, the layer is rotated before and rotated back after the bend operation. This enables bending in other directions than vertical. bending usually changes the size of the handled layer. this plugin sets the offsets of the handled layer to keep its center at the same position

    :param image: Input image
    :param drawable: Input drawable (must be a layer without layermask)
    :param rotation: Direction {angle 0 to 360 degree } of the bend effect
    :param smoothing: Smoothing { TRUE, FALSE }
    :param antialias: Antialias { TRUE, FALSE }
    :param work_on_copy: { TRUE, FALSE } TRUE: copy the drawable and bend the copy
    :param curve_type:  { 0, 1 } 0 == smooth (use 17 points), 1 == freehand (use 256 val_y) 
    :param argc_upper_point_x: {2 <= argc <= 17} 
    :param upper_point_x: array of 17 x point_koords { 0.0 <= x <= 1.0 or -1 for unused point }
    :param argc_upper_point_y: {2 <= argc <= 17} 
    :param upper_point_y: array of 17 y point_koords { 0.0 <= y <= 1.0 or -1 for unused point }
    :param argc_lower_point_x: {2 <= argc <= 17} 
    :param lower_point_x: array of 17 x point_koords { 0.0 <= x <= 1.0 or -1 for unused point }
    :param argc_lower_point_y: {2 <= argc <= 17} 
    :param lower_point_y: array of 17 y point_koords { 0.0 <= y <= 1.0 or -1 for unused point }
    :param argc_upper_val_y: { 256 } 
    :param upper_val_y: array of 256 y freehand koord { 0 <= y <= 255 }
    :param argc_lower_val_y: { 256 } 
    :param lower_val_y: array of 256 y freehand koord { 0 <= y <= 255 }
    :return: bent_layer
    """
    raise NotImplementedError()


def plug_in_curve_bend_Iterator(total_steps: int, current_step: float, len_struct: int):
    """
    This procedure calculates the modified values for one iterationstep for the call of plug_in_curve_bend


    :param total_steps: total number of steps (# of layers-1 to apply the related plug-in)
    :param current_step: current (for linear iterations this is the layerstack position, otherwise some value inbetween)
    :param len_struct: length of stored data structure with id is equal to the plug_in  proc_name
    """
    raise NotImplementedError()


def plug_in_dbbrowser():
    """
    List available procedures in the PDB

    """
    raise NotImplementedError()


def plug_in_decompose(image: Image, drawable: Drawable, decompose_type: str, layers_mode: int) -> Image:
    """
    Decompose an image into separate colorspace components

    This function creates new gray images with different channel information in each of them

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param decompose_type: What to decompose: "RGB", "Red", "Green", "Blue", "RGBA", "HSV", "Hue", "Saturation", "Value", "HSL", "Hue (HSL)", "Saturation (HSL)", "Lightness", "CMY", "Cyan", "Magenta", "Yellow", "CMYK", "Cyan_K", "Magenta_K", "Yellow_K", "Alpha", "LAB", "YCbCr_ITU_R470", "YCbCr_ITU_R709", "YCbCr_ITU_R470_256", "YCbCr_ITU_R709_256"
    :param layers_mode: Create channels as layers in a single image
    :return: new_image
    """
    raise NotImplementedError()


def plug_in_decompose_registered(image: Image, drawable: Drawable, decompose_type: str, layers_mode: int) -> Image:
    """
    Decompose an image into separate colorspace components

    This function creates new gray images with different channel information in each of them. Pixels in the foreground color will appear black in all output images.  This can be used for things like crop marks that have to show up on all channels.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param decompose_type: What to decompose: "RGB", "Red", "Green", "Blue", "RGBA", "HSV", "Hue", "Saturation", "Value", "HSL", "Hue (HSL)", "Saturation (HSL)", "Lightness", "CMY", "Cyan", "Magenta", "Yellow", "CMYK", "Cyan_K", "Magenta_K", "Yellow_K", "Alpha", "LAB", "YCbCr_ITU_R470", "YCbCr_ITU_R709", "YCbCr_ITU_R470_256", "YCbCr_ITU_R709_256"
    :param layers_mode: Create channels as layers in a single image
    :return: new_image
    """
    raise NotImplementedError()


def plug_in_deinterlace(image: Image, drawable: Drawable, evenodd: int):
    """
    Fix images where every other row is missing

    Deinterlace is useful for processing images from video capture cards. When only the odd or even fields get captured, deinterlace can be used to interpolate between the existing fields to correct this.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param evenodd: Which lines to keep { KEEP-ODD (0), KEEP-EVEN (1) }
    """
    raise NotImplementedError()


def plug_in_depth_merge(image: Image, result: Drawable, source1: Drawable, source2: Drawable, depthMap1: Drawable, depthMap2: Drawable, overlap: float, offset: float, scale1: float, scale2: float):
    """
    Combine two images using depth maps (z-buffers)

    Taking as input two full-color, full-alpha images and two corresponding grayscale depth maps, this plug-in combines the images based on which is closer (has a lower depth map value) at each point.

    :param image: Input image (unused)
    :param result: Result
    :param source1: Source 1
    :param source2: Source 2
    :param depthMap1: Depth map 1
    :param depthMap2: Depth map 2
    :param overlap: Overlap
    :param offset: Depth relative offset
    :param scale1: Depth relative scale 1
    :param scale2: Depth relative scale 2
    """
    raise NotImplementedError()


def plug_in_despeckle(image: Image, drawable: Drawable, radius: int, type: int, black: int, white: int):
    """
    Remove speckle noise from the image

    This plug-in selectively performs a median or adaptive box filter on an image.

    :param image: Input image
    :param drawable: Input drawable
    :param radius: Filter box radius (default = 3)
    :param type: Filter type { MEDIAN (0), ADAPTIVE (1), RECURSIVE-MEDIAN (2), RECURSIVE-ADAPTIVE (3) }
    :param black: Black level (-1 to 255)
    :param white: White level (0 to 256)
    """
    raise NotImplementedError()


def plug_in_destripe(image: Image, drawable: Drawable, avg_width: int):
    """
    Remove vertical stripe artifacts from the image

    This plug-in tries to remove vertical stripes from an image.

    :param image: Input image
    :param drawable: Input drawable
    :param avg_width: Averaging filter width (default = 36)
    """
    raise NotImplementedError()


def plug_in_diffraction(image: Image, drawable: Drawable, lam_r: float, lam_g: float, lam_b: float, contour_r: float, contour_g: float, contour_b: float, edges_r: float, edges_g: float, edges_b: float, brightness: float, scattering: float, polarization: float):
    """
    Generate diffraction patterns

    Help?  What help?  Real men do not need help :-)

    :param image: Input image
    :param drawable: Input drawable
    :param lam_r: Light frequency (red)
    :param lam_g: Light frequency (green)
    :param lam_b: Light frequency (blue)
    :param contour_r: Number of contours (red)
    :param contour_g: Number of contours (green)
    :param contour_b: Number of contours (blue)
    :param edges_r: Number of sharp edges (red)
    :param edges_g: Number of sharp edges (green)
    :param edges_b: Number of sharp edges (blue)
    :param brightness: Brightness and shifting/fattening of contours
    :param scattering: Scattering (Speed vs. quality)
    :param polarization: Polarization
    """
    raise NotImplementedError()


def plug_in_dilate(image: Image, drawable: Drawable, propagate_mode: int, propagating_channel: int, propagating_rate: float, direction_mask: int, lower_limit: int, upper_limit: int):
    """
    Grow lighter areas of the image

    Dilate image

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param propagate_mode: propagate 0:white, 1:black, 2:middle value 3:foreground to peak, 4:foreground, 5:background, 6:opaque, 7:transparent
    :param propagating_channel: channels which values are propagated
    :param propagating_rate: 0.0 <= propagatating_rate <= 1.0
    :param direction_mask: 0 <= direction-mask <= 15
    :param lower_limit: 0 <= lower-limit <= 255
    :param upper_limit: 0 <= upper-limit <= 255
    """
    raise NotImplementedError()


def plug_in_displace(image: Image, drawable: Drawable, amount_x: float, amount_y: float, do_x: int, do_y: int, displace_map_x: Drawable, displace_map_y: Drawable, displace_type: int):
    """
    Displace pixels as indicated by displacement maps

    Displaces the contents of the specified drawable by the amounts specified by 'amount-x' and 'amount-y' multiplied by the luminance of corresponding pixels in the 'displace-map' drawables.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param amount_x: Displace multiplier for X or radial direction
    :param amount_y: Displace multiplier for Y or tangent (degrees) direction
    :param do_x: Displace in X or radial direction?
    :param do_y: Displace in Y or tangent direction?
    :param displace_map_x: Displacement map for X or radial direction
    :param displace_map_y: Displacement map for Y or tangent direction
    :param displace_type: Edge behavior { WRAP (1), SMEAR (2), BLACK (3) }
    """
    raise NotImplementedError()


def plug_in_displace_polar(image: Image, drawable: Drawable, amount_x: float, amount_y: float, do_x: int, do_y: int, displace_map_x: Drawable, displace_map_y: Drawable, displace_type: int):
    """
    Displace the contents of the specified drawable

    Just like plug-in-displace but working in polar coordinates. The drawable is whirled and pinched according to the map.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param amount_x: Displace multiplier for X or radial direction
    :param amount_y: Displace multiplier for Y or tangent (degrees) direction
    :param do_x: Displace in X or radial direction?
    :param do_y: Displace in Y or tangent direction?
    :param displace_map_x: Displacement map for X or radial direction
    :param displace_map_y: Displacement map for Y or tangent direction
    :param displace_type: Edge behavior { WRAP (1), SMEAR (2), BLACK (3) }
    """
    raise NotImplementedError()


def plug_in_dog(image: Image, drawable: Drawable, inner: float, outer: float, normalize: int, invert: int):
    """
    Edge detection with control of edge thickness

    Applies two Gaussian blurs to the drawable, and subtracts the results.  This is robust and widely used method for detecting edges.

    :param image: Input image
    :param drawable: Input drawable
    :param inner: Radius of inner gaussian blur (in pixels, > 0.0)
    :param outer: Radius of outer gaussian blur (in pixels, > 0.0)
    :param normalize: Normalize { TRUE, FALSE }
    :param invert: Invert { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_drawable_compose(image1: Image, drawable1: Drawable, drawable2: Drawable, drawable3: Drawable, drawable4: Drawable, compose_type: str) -> Image:
    """
    Compose an image from multiple drawables of gray images

    This function creates a new image from multiple drawables of gray images

    :param image1: First input image (not used)
    :param drawable1: First input drawable
    :param drawable2: Second input drawable
    :param drawable3: Third input drawable
    :param drawable4: Fourth input drawable
    :param compose_type: What to compose: "RGB", "RGBA", "HSV", "HSL", "CMY", "CMYK", "LAB", "YCbCr_ITU_R470", "YCbCr_ITU_R709", "YCbCr_ITU_R470_256", "YCbCr_ITU_R709_256"
    :return: new_image
    """
    raise NotImplementedError()


def plug_in_edge(image: Image, drawable: Drawable, amount: float, wrapmode: int, edgemode: int):
    """
    Several simple methods for detecting edges

    Perform edge detection on the contents of the specified drawable.AMOUNT is an arbitrary constant, WRAPMODE is like displace plug-in (useful for tilable image). EDGEMODE sets the kind of matrix transform applied to the pixels, SOBEL was the method used in older versions.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param amount: Edge detection amount
    :param wrapmode: Edge detection behavior { WRAP (1), SMEAR (2), BLACK (3) }
    :param edgemode: Edge detection algorithm { SOBEL (0), PREWITT (1), GRADIENT (2), ROBERTS (3), DIFFERENTIAL (4), LAPLACE (5) }
    """
    raise NotImplementedError()


def plug_in_emboss(image: Image, drawable: Drawable, azimuth: float, elevation: float, depth: int, emboss: int):
    """
    Simulate an image created by embossing

    Emboss or Bumpmap the given drawable, specifying the angle and elevation for the light source.

    :param image: The Image
    :param drawable: The Drawable
    :param azimuth: The Light Angle (degrees)
    :param elevation: The Elevation Angle (degrees)
    :param depth: The Filter Width
    :param emboss: Emboss or Bumpmap
    """
    raise NotImplementedError()


def plug_in_engrave(image: Image, drawable: Drawable, height: int, limit: int):
    """
    Simulate an antique engraving

    Creates a black-and-white 'engraved' version of an image as seen in old illustrations

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param height: Resolution in pixels
    :param limit: Limit line width { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_erode(image: Image, drawable: Drawable, propagate_mode: int, propagating_channel: int, propagating_rate: float, direction_mask: int, lower_limit: int, upper_limit: int):
    """
    Shrink lighter areas of the image

    Erode image

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param propagate_mode: propagate 0:white, 1:black, 2:middle value 3:foreground to peak, 4:foreground, 5:background, 6:opaque, 7:transparent
    :param propagating_channel: channels which values are propagated
    :param propagating_rate: 0.0 <= propagatating_rate <= 1.0
    :param direction_mask: 0 <= direction-mask <= 15
    :param lower_limit: 0 <= lower-limit <= 255
    :param upper_limit: 0 <= upper-limit <= 255
    """
    raise NotImplementedError()


def plug_in_exchange(image: Image, drawable: Drawable, from_red: int, from_green: int, from_blue: int, to_red: int, to_green: int, to_blue: int, red_threshold: int, green_threshold: int, blue_threshold: int):
    """
    Swap one color with another

    Exchange one color with another, optionally setting a threshold to convert from one shade to another

    :param image: Input image
    :param drawable: Input drawable
    :param from_red: Red value (from)
    :param from_green: Green value (from)
    :param from_blue: Blue value (from)
    :param to_red: Red value (to)
    :param to_green: Green value (to)
    :param to_blue: Blue value (to)
    :param red_threshold: Red threshold
    :param green_threshold: Green threshold
    :param blue_threshold: Blue threshold
    """
    raise NotImplementedError()


def plug_in_film(image: Image, drawable: Drawable, film_height: int, film_color: Color, number_start: int, number_font: str, number_color: Color, at_top: int, at_bottom: int, num_images: int, image_ids: List[int]) -> Image:
    """
    Combine several images on a film strip

    Compose several images to a roll film

    :param image: Input image (only used as default image in interactive mode)
    :param drawable: Input drawable (not used)
    :param film_height: Height of film (0: fit to images)
    :param film_color: Color of the film
    :param number_start: Start index for numbering
    :param number_font: Font for drawing numbers
    :param number_color: Color for numbers
    :param at_top: Flag for drawing numbers at top of film
    :param at_bottom: Flag for drawing numbers at bottom of film
    :param num_images: Number of images to be used for film
    :param image_ids: num-images image IDs to be used for film
    :return: new_image
    """
    raise NotImplementedError()


def plug_in_filter_pack(image: Image, drawable: Drawable):
    """
    Interactively modify the image colors

    Interactively modify the image colors.

    :param image: Input image (used for indexed images)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_flame(image: Image, drawable: Drawable):
    """
    Create cosmic recursive fractal flames

    Create cosmic recursive fractal flames

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_flarefx(image: Image, drawable: Drawable, pos_x: int, pos_y: int):
    """
    Add a lens flare effect

    Adds a lens flare effects.  Makes your image look like it was snapped with a cheap camera with a lot of lens :)

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param pos_x: X-position
    :param pos_y: Y-position
    """
    raise NotImplementedError()


def plug_in_fractal_trace(image: Image, drawable: Drawable, xmin: float, xmax: float, ymin: float, ymax: float, depth: int, outside_type: int):
    """
    Transform image with the Mandelbrot Fractal

    transform image with the Mandelbrot Fractal

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param xmin: xmin fractal image delimiter
    :param xmax: xmax fractal image delimiter
    :param ymin: ymin fractal image delimiter
    :param ymax: ymax fractal image delimiter
    :param depth: Trace depth
    :param outside_type: Outside type { WRAP (0), TRANS (1), BLACK (2), WHITE (3) }
    """
    raise NotImplementedError()


def plug_in_fractalexplorer(image: Image, drawable: Drawable, fractaltype: int, xmin: float, xmax: float, ymin: float, ymax: float, iter: float, cx: float, cy: float, colormode: int, redstretch: float, greenstretch: float, bluestretch: float, redmode: int, greenmode: int, bluemode: int, redinvert: int, greeninvert: int, blueinvert: int, ncolors: int):
    """
    Render fractal art

    No help yet.

    :param image: Input image
    :param drawable: Input drawable
    :param fractaltype: 0: Mandelbrot; 1: Julia; 2: Barnsley 1; 3: Barnsley 2; 4: Barnsley 3; 5: Spider; 6: ManOWar; 7: Lambda; 8: Sierpinski
    :param xmin: xmin fractal image delimiter
    :param xmax: xmax fractal image delimiter
    :param ymin: ymin fractal image delimiter
    :param ymax: ymax fractal image delimiter
    :param iter: Iteration value
    :param cx: cx value ( only Julia)
    :param cy: cy value ( only Julia)
    :param colormode: 0: Apply colormap as specified by the parameters below; 1: Apply active gradient to final image
    :param redstretch: Red stretching factor
    :param greenstretch: Green stretching factor
    :param bluestretch: Blue stretching factor
    :param redmode: Red application mode (0:SIN;1:COS;2:NONE)
    :param greenmode: Green application mode (0:SIN;1:COS;2:NONE)
    :param bluemode: Blue application mode (0:SIN;1:COS;2:NONE)
    :param redinvert: Red inversion mode (1: enabled; 0: disabled)
    :param greeninvert: Green inversion mode (1: enabled; 0: disabled)
    :param blueinvert: Green inversion mode (1: enabled; 0: disabled)
    :param ncolors: Number of Colors for mapping (2<=ncolors<=8192)
    """
    raise NotImplementedError()


def plug_in_gauss(image: Image, drawable: Drawable, horizontal: float, vertical: float, method: int):
    """
    Simplest, most commonly used way of blurring

    Applies a gaussian blur to the drawable, with specified radius of affect.  The standard deviation of the normal distribution used to modify pixel values is calculated based on the supplied radius.  Horizontal and vertical blurring can be independently invoked by specifying only one to run.  The IIR gaussian blurring works best for large radius values and for images which are not computer-generated.

    :param image: Input image
    :param drawable: Input drawable
    :param horizontal: Horizontal radius of gaussian blur (in pixels, > 0.0)
    :param vertical: Vertical radius of gaussian blur (in pixels, > 0.0)
    :param method: Blur method { IIR (0), RLE (1) }
    """
    raise NotImplementedError()


def plug_in_gauss_iir(image: Image, drawable: Drawable, radius: float, horizontal: int, vertical: int):
    """
    Apply a gaussian blur

    Applies a gaussian blur to the drawable, with specified radius of affect.  The standard deviation of the normal distribution used to modify pixel values is calculated based on the supplied radius.  Horizontal and vertical blurring can be independently invoked by specifying only one to run.  The IIR gaussian blurring works best for large radius values and for images which are not computer-generated.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param radius: Radius of gaussian blur (in pixels, > 0.0)
    :param horizontal: Blur in horizontal direction
    :param vertical: Blur in vertical direction
    """
    raise NotImplementedError()


def plug_in_gauss_iir2(image: Image, drawable: Drawable, horizontal: float, vertical: float):
    """
    Apply a gaussian blur

    Applies a gaussian blur to the drawable, with specified radius of affect.  The standard deviation of the normal distribution used to modify pixel values is calculated based on the supplied radius.  This radius can be specified indepently on for the horizontal and the vertical direction. The IIR gaussian blurring works best for large radius values and for images which are not computer-generated.

    :param image: Input image
    :param drawable: Input drawable
    :param horizontal: Horizontal radius of gaussian blur (in pixels, > 0.0)
    :param vertical: Vertical radius of gaussian blur (in pixels, > 0.0)
    """
    raise NotImplementedError()


def plug_in_gauss_rle(image: Image, drawable: Drawable, radius: float, horizontal: int, vertical: int):
    """
    Apply a gaussian blur

    Applies a gaussian blur to the drawable, with specified radius of affect.  The standard deviation of the normal distribution used to modify pixel values is calculated based on the supplied radius.  Horizontal and vertical blurring can be independently invoked by specifying only one to run.  The RLE gaussian blurring performs most efficiently on computer-generated images or images with large areas of constant intensity.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param radius: Radius of gaussian blur (in pixels, > 0.0)
    :param horizontal: Blur in horizontal direction
    :param vertical: Blur in vertical direction
    """
    raise NotImplementedError()


def plug_in_gauss_rle2(image: Image, drawable: Drawable, horizontal: float, vertical: float):
    """
    Apply a gaussian blur

    Applies a gaussian blur to the drawable, with specified radius of affect.  The standard deviation of the normal distribution used to modify pixel values is calculated based on the supplied radius.  This radius can be specified indepently on for the horizontal and the vertical direction. The RLE gaussian blurring performs most efficiently on computer-generated images or images with large areas of constant intensity.

    :param image: Input image
    :param drawable: Input drawable
    :param horizontal: Horizontal radius of gaussian blur (in pixels, > 0.0)
    :param vertical: Vertical radius of gaussian blur (in pixels, > 0.0)
    """
    raise NotImplementedError()


def plug_in_gfig(image: Image, drawable: Drawable, dummy: int):
    """
    Create geometric shapes

    Draw Vector Graphics and paint them onto your images.  Gfig allows you to draw many types of objects including Lines, Circles, Ellipses, Curves, Polygons, pointed stars, Bezier curves, and Spirals.  Objects can be painted using Brushes or other toolsor filled using colours or patterns.  Gfig objects can also be used to create selections.  

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param dummy: dummy
    """
    raise NotImplementedError()


def plug_in_gflare(image: Image, drawable: Drawable, gflare_name: str, xcenter: int, ycenter: int, radius: float, rotation: float, hue: float, vangle: float, vlength: float, use_asupsample: int, asupsample_max_depth: int, asupsample_threshold: float):
    """
    Produce a lense flare effect using gradients

    This plug-in produces a lense flare effect using custom gradients. In interactive call, the user can edit his/her own favorite lense flare (GFlare) and render it. Edited gflare is saved automatically to the folder in gflare-path, if it is defined in gimprc. In non-interactive call, the user can only render one of GFlare which has been stored in gflare-path already.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param gflare_name: The name of GFlare
    :param xcenter: X coordinate of center of GFlare
    :param ycenter: Y coordinate of center of GFlare
    :param radius: Radius of GFlare (pixel)
    :param rotation: Rotation of GFlare (degree)
    :param hue: Hue rotation of GFlare (degree)
    :param vangle: Vector angle for second flares (degree)
    :param vlength: Vector length for second flares (percentage to Radius)
    :param use_asupsample: Whether it uses or not adaptive supersampling while rendering (boolean)
    :param asupsample_max_depth: Max depth for adaptive supersampling
    :param asupsample_threshold: Threshold for adaptive supersampling
    """
    raise NotImplementedError()


def plug_in_gimpressionist(image: Image, drawable: Drawable, preset: str):
    """
    Performs various artistic operations

    Performs various artistic operations on an image

    :param image: Input image
    :param drawable: Input drawable
    :param preset: Preset Name
    """
    raise NotImplementedError()


def plug_in_glasstile(image: Image, drawable: Drawable, tilex: int, tiley: int):
    """
    Simulate distortion caused by square glass tiles

    Divide the image into square glassblocks in which the image is refracted.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param tilex: Tile width (10 - 50)
    :param tiley: Tile height (10 - 50)
    """
    raise NotImplementedError()


def plug_in_gradmap(image: Image, drawable: Drawable):
    """
    Recolor the image using colors from the active gradient

    This plug-in maps the contents of the specified drawable with active gradient. It calculates luminosity of each pixel and replaces the pixel by the sample of active gradient at the position proportional to that luminosity. Complete black pixel becomes the leftmost color of the gradient, and complete white becomes the rightmost. Works on both Grayscale and RGB image with/without alpha channel.

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_grid(image: Image, drawable: Drawable, hwidth: int, hspace: int, hoffset: int, hcolor: Color, hopacity: int, vwidth: int, vspace: int, voffset: int, vcolor: Color, vopacity: int, iwidth: int, ispace: int, ioffset: int, icolor: Color, iopacity: int):
    """
    Draw a grid on the image

    Draws a grid using the specified colors. The grid origin is the upper left corner.

    :param image: Input image
    :param drawable: Input drawable
    :param hwidth: Horizontal Width   (>= 0)
    :param hspace: Horizontal Spacing (>= 1)
    :param hoffset: Horizontal Offset  (>= 0)
    :param hcolor: Horizontal Colour
    :param hopacity: Horizontal Opacity (0...255)
    :param vwidth: Vertical Width   (>= 0)
    :param vspace: Vertical Spacing (>= 1)
    :param voffset: Vertical Offset  (>= 0)
    :param vcolor: Vertical Colour
    :param vopacity: Vertical Opacity (0...255)
    :param iwidth: Intersection Width   (>= 0)
    :param ispace: Intersection Spacing (>= 0)
    :param ioffset: Intersection Offset  (>= 0)
    :param icolor: Intersection Colour
    :param iopacity: Intersection Opacity (0...255)
    """
    raise NotImplementedError()


def plug_in_guillotine(image: Image, drawable: Drawable) -> Tuple[int, List[int]]:
    """
    Slice the image into subimages using guides

    This function takes an image and slices it along its guides, creating new images. The original image is not modified.

    :param image: Input image
    :param drawable: Input drawable (unused)
    :return: image_count, image_ids
    """
    raise NotImplementedError()


def plug_in_hot(image: Image, drawable: Drawable, mode: int, action: int, new_layer: int):
    """
    Find and fix pixels that may be unsafely bright

    hot scans an image for pixels that will give unsave values of chrominance or composite signale amplitude when encoded into an NTSC or PAL signal.  Three actions can be performed on these ``hot'' pixels. (0) reduce luminance, (1) reduce saturation, or (2) Blacken.

    :param image: The Image
    :param drawable: The Drawable
    :param mode: Mode { NTSC (0), PAL (1) }
    :param action: The action to perform
    :param new_layer: Create a new layer { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_hsv_noise(image: Image, drawable: Drawable, holdness: int, hue_distance: int, saturation_distance: int, value_distance: int):
    """
    Randomize hue/saturation/value independently

    Scattering pixel values in HSV space

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param holdness: convolution strength
    :param hue_distance: scattering of hue angle [0,180]
    :param saturation_distance: distribution distance on saturation axis [0,255]
    :param value_distance: distribution distance on value axis [0,255]
    """
    raise NotImplementedError()


def plug_in_icc_profile_apply(image: Image, profile: str, intent: int, bpc: int):
    """
    Apply a color profile on the image

    This procedure transform from the image's color profile (or the default RGB profile if none is set) to the given ICC color profile. Only RGB color profiles are accepted. The profile is then set on the image using the 'icc-profile' parasite.

    :param image: Input image
    :param profile: Filename of an ICC color profile
    :param intent: Rendering intent (enum GimpColorRenderingIntent)
    :param bpc: Black point compensation
    """
    raise NotImplementedError()


def plug_in_icc_profile_apply_rgb(image: Image, intent: int, bpc: int):
    """
    Apply default RGB color profile on the image

    This procedure transform from the image's color profile (or the default RGB profile if none is set) to the configured default RGB color profile.  The profile is then set on the image using the 'icc-profile' parasite.  If no RGB color profile is configured, sRGB is assumed and the parasite is unset.

    :param image: Input image
    :param intent: Rendering intent (enum GimpColorRenderingIntent)
    :param bpc: Black point compensation
    """
    raise NotImplementedError()


def plug_in_icc_profile_file_info(profile: str) -> Tuple[str, str, str]:
    """
    Retrieve information about a color profile

    This procedure returns information about an ICC color profile on disk.

    :param profile: Filename of an ICC color profile
    :return: profile_name, profile_desc, profile_info
    """
    raise NotImplementedError()


def plug_in_icc_profile_info(image: Image) -> Tuple[str, str, str]:
    """
    Retrieve information about an image's color profile

    This procedure returns information about the RGB color profile attached to an image. If no RGB color profile is attached, sRGB is assumed.

    :param image: Input image
    :return: profile_name, profile_desc, profile_info
    """
    raise NotImplementedError()


def plug_in_icc_profile_set(image: Image, profile: str):
    """
    Set a color profile on the image

    This procedure sets an ICC color profile on an image using the 'icc-profile' parasite. It does not do any color conversion.

    :param image: Input image
    :param profile: Filename of an ICC color profile
    """
    raise NotImplementedError()


def plug_in_icc_profile_set_rgb(image: Image):
    """
    Set the default RGB color profile on the image

    This procedure sets the user-configured RGB profile on an image using the 'icc-profile' parasite. If no RGB profile is configured, sRGB is assumed and the parasite is unset. This procedure does not do any color conversion.

    :param image: Input image
    """
    raise NotImplementedError()


def plug_in_ifscompose(image: Image, drawable: Drawable):
    """
    Create an Iterated Function System (IFS) fractal

    Interactively create an Iterated Function System fractal. Use the window on the upper left to adjust the component transformations of the fractal. The operation that is performed is selected by the buttons underneath the window, or from a menu popped up by the right mouse button. The fractal will be rendered with a transparent background if the current image has an alpha channel.

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_illusion(image: Image, drawable: Drawable, division: int, type: int):
    """
    Superimpose many altered copies of the image

    produce illusion

    :param image: Input image
    :param drawable: Input drawable
    :param division: The number of divisions
    :param type: Illusion type { TYPE1 (0), TYPE2 (1) }
    """
    raise NotImplementedError()


def plug_in_imagemap(image: Image, drawable: Drawable):
    """
    Create a clickable imagemap


    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_iwarp(image: Image, drawable: Drawable):
    """
    Use mouse control to warp image areas

    Interactive warping of the specified drawable

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_jigsaw(image: Image, drawable: Drawable, x: int, y: int, style: int, blend_lines: int, blend_amount: float):
    """
    Add a jigsaw-puzzle pattern to the image

    Jigsaw puzzle look

    :param image: Input image
    :param drawable: Input drawable
    :param x: Number of tiles across > 0
    :param y: Number of tiles down > 0
    :param style: The style/shape of the jigsaw puzzle { 0, 1 }
    :param blend_lines: Number of lines for shading bevels >= 0
    :param blend_amount: The power of the light highlights 0 =< 5
    """
    raise NotImplementedError()


def plug_in_laplace(image: Image, drawable: Drawable):
    """
    High-resolution edge detection

    This plugin creates one-pixel wide edges from the image, with the value proportional to the gradient. It uses the Laplace operator (a 3x3 kernel with -8 in the middle). The image has to be laplacered to get useful results, a gauss_iir with 1.5 - 5.0 depending on the noise in the image is best.

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_lens_distortion(image: Image, drawable: Drawable, offset_x: float, offset_y: float, main_adjust: float, edge_adjust: float, rescale: float, brighten: float):
    """
    Corrects lens distortion

    Corrects barrel or pincushion lens distortion.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param offset_x: Effect centre offset in X
    :param offset_y: Effect centre offset in Y
    :param main_adjust: Amount of second-order distortion
    :param edge_adjust: Amount of fourth-order distortion
    :param rescale: Rescale overall image size
    :param brighten: Adjust brightness in corners
    """
    raise NotImplementedError()


def plug_in_lic(image: Image, drawable: Drawable):
    """
    Special effects that nobody understands

    No help yet

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_lighting(image: Image, drawable: Drawable, bumpdrawable: Drawable, envdrawable: Drawable, dobumpmap: int, doenvmap: int, bumpmaptype: int, lighttype: int, lightcolor: Color, lightposition_x: float, lightposition_y: float, lightposition_z: float, lightdirection_x: float, lightdirection_y: float, lightdirection_z: float, ambient_intensity: float, diffuse_intensity: float, diffuse_reflectivity: float, specular_reflectivity: float, highlight: float, antialiasing: int, newimage: int, transparentbackground: int):
    """
    Apply various lighting effects to an image

    No help yet

    :param image: Input image
    :param drawable: Input drawable
    :param bumpdrawable: Bumpmap drawable (set to 0 if disabled)
    :param envdrawable: Environmentmap drawable (set to 0 if disabled)
    :param dobumpmap: Enable bumpmapping (TRUE/FALSE)
    :param doenvmap: Enable envmapping (TRUE/FALSE)
    :param bumpmaptype: Type of mapping (0=linear,1=log, 2=sinusoidal, 3=spherical)
    :param lighttype: Type of lightsource (0=point,1=directional,3=spot,4=none)
    :param lightcolor: Lightsource color (r,g,b)
    :param lightposition_x: Lightsource position (x,y,z)
    :param lightposition_y: Lightsource position (x,y,z)
    :param lightposition_z: Lightsource position (x,y,z)
    :param lightdirection_x: Lightsource direction [x,y,z]
    :param lightdirection_y: Lightsource direction [x,y,z]
    :param lightdirection_z: Lightsource direction [x,y,z]
    :param ambient_intensity: Material ambient intensity (0..1)
    :param diffuse_intensity: Material diffuse intensity (0..1)
    :param diffuse_reflectivity: Material diffuse reflectivity (0..1)
    :param specular_reflectivity: Material specular reflectivity (0..1)
    :param highlight: Material highlight (0..->), note: it's expotential
    :param antialiasing: Apply antialiasing (TRUE/FALSE)
    :param newimage: Create a new image (TRUE/FALSE)
    :param transparentbackground: Make background transparent (TRUE/FALSE)
    """
    raise NotImplementedError()


def plug_in_mail_image(image: Image, drawable: Drawable, filename: str, to_address: str, from_address: str, subject: str, comment: str, encapsulation: int):
    """
    Send the image by email

    You need to have sendmail installed

    :param image: Input image
    :param drawable: Drawable to save
    :param filename: The name of the file to save the image in
    :param to_address: The email address to send to
    :param from_address: The email address for the From: field
    :param subject: The subject
    :param comment: The Comment
    :param encapsulation: ignored
    """
    raise NotImplementedError()


def plug_in_make_seamless(image: Image, drawable: Drawable):
    """
    Alters edges to make the image seamlessly tileable

    This plugin creates a seamless tileable from the input drawable

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_map_object(image: Image, drawable: Drawable, maptype: int, viewpoint_x: float, viewpoint_y: float, viewpoint_z: float, position_x: float, position_y: float, position_z: float, firstaxis_x: float, firstaxis_y: float, firstaxis_z: float, secondaxis_x: float, secondaxis_y: float, secondaxis_z: float, rotationangle_x: float, rotationangle_y: float, rotationangle_z: float, lighttype: int, lightcolor: Color, lightposition_x: float, lightposition_y: float, lightposition_z: float, lightdirection_x: float, lightdirection_y: float, lightdirection_z: float, ambient_intensity: float, diffuse_intensity: float, diffuse_reflectivity: float, specular_reflectivity: float, highlight: float, antialiasing: int, tiled: int, newimage: int, transparentbackground: int, radius: float, x_scale: float, y_scale: float, z_scale: float, cylinder_length: float, box_front_drawable: Drawable, box_back_drawable: Drawable, box_top_drawable: Drawable, box_bottom_drawable: Drawable, box_left_drawable: Drawable, box_right_drawable: Drawable, cyl_top_drawable: Drawable, cyl_bottom_drawable: Drawable):
    """
    Map the image to an object (plane, sphere, box or cylinder)

    No help yet

    :param image: Input image
    :param drawable: Input drawable
    :param maptype: Type of mapping (0=plane,1=sphere,2=box,3=cylinder)
    :param viewpoint_x: Position of viewpoint (x,y,z)
    :param viewpoint_y: Position of viewpoint (x,y,z)
    :param viewpoint_z: Position of viewpoint (x,y,z)
    :param position_x: Object position (x,y,z)
    :param position_y: Object position (x,y,z)
    :param position_z: Object position (x,y,z)
    :param firstaxis_x: First axis of object [x,y,z]
    :param firstaxis_y: First axis of object [x,y,z]
    :param firstaxis_z: First axis of object [x,y,z]
    :param secondaxis_x: Second axis of object [x,y,z]
    :param secondaxis_y: Second axis of object [x,y,z]
    :param secondaxis_z: Second axis of object [x,y,z]
    :param rotationangle_x: Rotation about X axis in degrees
    :param rotationangle_y: Rotation about Y axis in degrees
    :param rotationangle_z: Rotation about Z axis in degrees
    :param lighttype: Type of lightsource (0=point,1=directional,2=none)
    :param lightcolor: Lightsource color (r,g,b)
    :param lightposition_x: Lightsource position (x,y,z)
    :param lightposition_y: Lightsource position (x,y,z)
    :param lightposition_z: Lightsource position (x,y,z)
    :param lightdirection_x: Lightsource direction [x,y,z]
    :param lightdirection_y: Lightsource direction [x,y,z]
    :param lightdirection_z: Lightsource direction [x,y,z]
    :param ambient_intensity: Material ambient intensity (0..1)
    :param diffuse_intensity: Material diffuse intensity (0..1)
    :param diffuse_reflectivity: Material diffuse reflectivity (0..1)
    :param specular_reflectivity: Material specular reflectivity (0..1)
    :param highlight: Material highlight (0..->), note: it's expotential
    :param antialiasing: Apply antialiasing (TRUE/FALSE)
    :param tiled: Tile source image (TRUE/FALSE)
    :param newimage: Create a new image (TRUE/FALSE)
    :param transparentbackground: Make background transparent (TRUE/FALSE)
    :param radius: Sphere/cylinder radius (only used when maptype=1 or 3)
    :param x_scale: Box x size (0..->)
    :param y_scale: Box y size (0..->)
    :param z_scale: Box z size (0..->)
    :param cylinder_length: Cylinder length (0..->)
    :param box_front_drawable: Box front face (set these to -1 if not used)
    :param box_back_drawable: Box back face
    :param box_top_drawable: Box top face
    :param box_bottom_drawable: Box bottom face
    :param box_left_drawable: Box left face
    :param box_right_drawable: Box right face
    :param cyl_top_drawable: Cylinder top face (set these to -1 if not used)
    :param cyl_bottom_drawable: Cylinder bottom face
    """
    raise NotImplementedError()


def plug_in_max_rgb(image: Image, drawable: Drawable, max_p: int):
    """
    Reduce image to pure red, green, and blue

    There's no help yet.

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param max_p: { MINIMIZE (0), MAXIMIZE (1) }
    """
    raise NotImplementedError()


def plug_in_maze(image: Image, drawable: Drawable, width: int, height: int, tileable: int, algorithm: int, seed: int, multiple: int, offset: int):
    """
    Draw a labyrinth

    Generates a maze using either the depth-first search method or Prim's algorithm.  Can make tileable mazes too.

    :param image: (unused)
    :param drawable: ID of drawable
    :param width: Width of the passages
    :param height: Height of the passages
    :param tileable: Tileable maze?
    :param algorithm: Generation algorithm(0=DEPTH FIRST, 1=PRIM'S ALGORITHM)
    :param seed: Random Seed
    :param multiple: Multiple (use 57)
    :param offset: Offset (use 1)
    """
    raise NotImplementedError()


def plug_in_mblur(image: Image, drawable: Drawable, type: int, length: int, angle: int, center_x: float, center_y: float):
    """
    Simulate movement using directional blur

    This plug-in simulates the effect seen when photographing a moving object at a slow shutter speed. Done by adding multiple displaced copies.

    :param image: Input image
    :param drawable: Input drawable
    :param type: Type of motion blur { LINEAR (0), RADIAL (1), ZOOM (2) }
    :param length: Length
    :param angle: Angle
    :param center_x: Center X (optional)
    :param center_y: Center Y (optional)
    """
    raise NotImplementedError()


def plug_in_mblur_inward(image: Image, drawable: Drawable, type: int, length: int, angle: int, center_x: float, center_y: float):
    """
    Simulate movement using directional blur

    This procedure is equivalent to plug-in-mblur but performs the zoom blur inward instead of outward.

    :param image: Input image
    :param drawable: Input drawable
    :param type: Type of motion blur { LINEAR (0), RADIAL (1), ZOOM (2) }
    :param length: Length
    :param angle: Angle
    :param center_x: Center X (optional)
    :param center_y: Center Y (optional)
    """
    raise NotImplementedError()


def plug_in_metadata_decode_exif(image: Image, exif_size: int, exif: List[int]):
    """
    Decode an EXIF block

    Parse an EXIF block and merge the results with any metadata already attached to the image.  This should be used when an EXIF block is read from an image file.

    :param image: Input image
    :param exif_size: size of the EXIF block
    :param exif: EXIF block
    """
    raise NotImplementedError()


def plug_in_metadata_decode_xmp(image: Image, xmp: str):
    """
    Decode an XMP packet

    Parse an XMP packet and merge the results with any metadata already attached to the image.  This should be used when an XMP packet is read from an image file.

    :param image: Input image
    :param xmp: XMP packet
    """
    raise NotImplementedError()


def plug_in_metadata_editor(image: Image, drawable: Drawable):
    """
    View and edit metadata (EXIF, IPTC, XMP)

    View and edit metadata information attached to the current image.  This can include EXIF, IPTC and/or XMP information.  Some or all of this metadata will be saved in the file, depending on the output file format.

    :param image: Input image
    :param drawable: Input drawable (unused)
    """
    raise NotImplementedError()


def plug_in_metadata_encode_xmp(image: Image) -> str:
    """
    Encode metadata into an XMP packet

    Generate an XMP packet from the metadata information attached to the image.  The new XMP packet can then be saved into a file.

    :param image: Input image
    :return: xmp
    """
    raise NotImplementedError()


def plug_in_metadata_export(image: Image, filename: str, overwrite: int):
    """
    Export XMP from the current image to a file

    Export the metadata associated with the current image into a file.  The metadata will be saved as an XMP packet.  If overwrite is TRUE, then any existing file will be overwritten without warning. If overwrite is FALSE, then an error will occur if the file already exists.

    :param image: Input image
    :param filename: The name of the file to save the XMP packet in
    :param overwrite: Overwrite existing file: { FALSE (0), TRUE (1) }
    """
    raise NotImplementedError()


def plug_in_metadata_get(image: Image, schema: str, property: str) -> Tuple[int, int, List[str]]:
    """
    Retrieve the values of an XMP property

    Retrieve the list of values associated with an XMP property.

    :param image: Input image
    :param schema: XMP schema prefix or URI
    :param property: XMP property name
    :return: type, num_vals, vals
    """
    raise NotImplementedError()


def plug_in_metadata_get_simple(image: Image, schema: str, property: str) -> str:
    """
    Retrieve the value of an XMP property

    Retrieve value associated with a scalar XMP property.  This can only be done for simple property types such as text or integers.  Structured types must be retrieved with plug_in_metadata_get().

    :param image: Input image
    :param schema: XMP schema prefix or URI
    :param property: XMP property name
    :return: value
    """
    raise NotImplementedError()


def plug_in_metadata_import(image: Image, filename: str):
    """
    Import XMP from a file into the current image

    Load an XMP packet from a file and import it into the current image.  This can be used to add a license statement or some other predefined metadata to an image

    :param image: Input image
    :param filename: The name of the XMP file to import
    """
    raise NotImplementedError()


def plug_in_metadata_set(image: Image, schema: str, property: str, type: int, num_vals: int, vals: List[str]):
    """
    Set the values of an XMP property

    Set the list of values associated with an XMP property.  If a property with the same name already exists, it will be replaced.

    :param image: Input image
    :param schema: XMP schema prefix or URI
    :param property: XMP property name
    :param type: XMP property type
    :param num_vals: number of values
    :param vals: XMP property values
    """
    raise NotImplementedError()


def plug_in_metadata_set_simple(image: Image, schema: str, property: str, value: str):
    """
    Set the value of an XMP property

    Set the value of a scalar XMP property.  This can only be done for simple property types such as text or integers.  Structured types need to be set with plug_in_metadata_set().

    :param image: Input image
    :param schema: XMP schema prefix or URI
    :param property: XMP property name
    :param value: XMP property value
    """
    raise NotImplementedError()


def plug_in_mosaic(image: Image, drawable: Drawable, tile_size: float, tile_height: float, tile_spacing: float, tile_neatness: float, tile_allow_split: int, light_dir: float, color_variation: float, antialiasing: int, color_averaging: int, tile_type: int, tile_surface: int, grout_color: int):
    """
    Convert the image into irregular tiles

    Help not yet written for this plug-in

    :param image: Input image
    :param drawable: Input drawable
    :param tile_size: Average diameter of each tile (in pixels)
    :param tile_height: Apparent height of each tile (in pixels)
    :param tile_spacing: Inter-tile spacing (in pixels)
    :param tile_neatness: Deviation from perfectly formed tiles (0.0 - 1.0)
    :param tile_allow_split: Allows splitting tiles at hard edges
    :param light_dir: Direction of light-source (in degrees)
    :param color_variation: Magnitude of random color variations (0.0 - 1.0)
    :param antialiasing: Enables smoother tile output at the cost of speed
    :param color_averaging: Tile color based on average of subsumed pixels
    :param tile_type: Tile geometry { SQUARES (0), HEXAGONS (1), OCTAGONS (2), TRIANGLES (3) }
    :param tile_surface: Surface characteristics { SMOOTH (0), ROUGH (1) }
    :param grout_color: Grout color (black/white or fore/background) { BW (0), FG-BG (1) }
    """
    raise NotImplementedError()


def plug_in_neon(image: Image, drawable: Drawable, radius: float, amount: float):
    """
    Simulate the glowing boundary of a neon light

    This filter works in a manner similar to the edge plug-in, but uses the first derivative of the gaussian operator to achieve resolution independence. The IIR method of calculating the effect is utilized to keep the processing time constant between large and small standard deviations.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param radius: Radius of neon effect (in pixels)
    :param amount: Effect enhancement variable (0.0 - 1.0)
    """
    raise NotImplementedError()


def plug_in_newsprint(image: Image, drawable: Drawable, cell_width: int, colorspace: int, k_pullout: int, gry_ang: float, gry_spotfn: int, red_ang: float, red_spotfn: int, grn_ang: float, grn_spotfn: int, blu_ang: float, blu_spotfn: int, oversample: int):
    """
    Halftone the image to give newspaper-like effect

    Halftone the image, trading off resolution to represent colors or grey levels using the process described both in the PostScript language definition, and also by Robert Ulichney, "Digital halftoning", MIT Press, 1987.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param cell_width: Screen cell width in pixels
    :param colorspace: Separate to { GRAYSCALE (0), RGB (1), CMYK (2), LUMINANCE (3) }
    :param k_pullout: Percentage of black to pullout (CMYK only)
    :param gry_ang: Grey/black screen angle (degrees)
    :param gry_spotfn: Grey/black spot function { DOTS (0), LINES (1), DIAMONDS (2), EUCLIDIAN-DOT (3), PS-DIAMONDS (4) }
    :param red_ang: Red/cyan screen angle (degrees)
    :param red_spotfn: Red/cyan spot function (values as gry-spotfn)
    :param grn_ang: Green/magenta screen angle (degrees)
    :param grn_spotfn: Green/magenta spot function (values as gry-spotfn)
    :param blu_ang: Blue/yellow screen angle (degrees)
    :param blu_spotfn: Blue/yellow spot function (values as gry-spotfn)
    :param oversample: how many times to oversample spot fn
    """
    raise NotImplementedError()


def plug_in_nlfilt(img: Image, drw: Drawable, alpha: float, radius: float, filter: int):
    """
    Nonlinear swiss army knife filter

    This is the pnmnlfilt, in gimp's clothing.  See the pnmnlfilt manpage for details.

    :param img: The Image to Filter
    :param drw: The Drawable
    :param alpha: The amount of the filter to apply
    :param radius: The filter radius
    :param filter: The Filter to Run, 0 - alpha trimmed mean; 1 - optimal estimation (alpha controls noise variance); 2 - edge enhancement
    """
    raise NotImplementedError()


def plug_in_noisify(image: Image, drawable: Drawable, independent: int, noise_1: float, noise_2: float, noise_3: float, noise_4: float):
    """
    Adds random noise to image channels 

    Add normally distributed random values to image channels. For colour images each colour channel may be treated together or independently.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param independent: Noise in channels independent
    :param noise_1: Noise in the first channel (red, gray)
    :param noise_2: Noise in the second channel (green, gray_alpha)
    :param noise_3: Noise in the third channel (blue)
    :param noise_4: Noise in the fourth channel (alpha)
    """
    raise NotImplementedError()


def plug_in_normalize(image: Image, drawable: Drawable):
    """
    Stretch brightness values to cover the full range

    This plugin performs almost the same operation as the 'contrast autostretch' plugin, except that it won't allow the color channels to normalize independently.  This is actually what most people probably want instead of contrast-autostretch; use c-a only if you wish to remove an undesirable color-tint from a source image which is supposed to contain pure-white and pure-black.

    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_nova(image: Image, drawable: Drawable, xcenter: int, ycenter: int, color: Color, radius: int, nspoke: int, randomhue: int):
    """
    Add a starburst to the image

    This plug-in produces an effect like a supernova burst. The amount of the light effect is approximately in proportion to 1/r, where r is the distance from the center of the star. It works with RGB*, GRAY* image.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param xcenter: X coordinates of the center of supernova
    :param ycenter: Y coordinates of the center of supernova
    :param color: Color of supernova
    :param radius: Radius of supernova
    :param nspoke: Number of spokes
    :param randomhue: Random hue
    """
    raise NotImplementedError()


def plug_in_oilify(image: Image, drawable: Drawable, mask_size: int, mode: int):
    """
    Smear colors to simulate an oil painting

    This function performs the well-known oil-paint effect on the specified drawable.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param mask_size: Oil paint mask size
    :param mode: Algorithm { RGB (0), INTENSITY (1) }
    """
    raise NotImplementedError()


def plug_in_oilify_enhanced(image: Image, drawable: Drawable, mode: int, mask_size: int, mask_size_map: Drawable, exponent: int, exponent_map: Drawable):
    """
    Smear colors to simulate an oil painting

    This function performs the well-known oil-paint effect on the specified drawable.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param mode: Algorithm { RGB (0), INTENSITY (1) }
    :param mask_size: Oil paint mask size
    :param mask_size_map: Mask size control map
    :param exponent: Oil paint exponent
    :param exponent_map: Exponent control map
    """
    raise NotImplementedError()


def plug_in_pagecurl(image: Image, drawable: Drawable, colors: int, edge: int, orientation: int, shade: int) -> Layer:
    """
    Curl up one of the image corners

    This plug-in creates a pagecurl-effect.

    :param image: Input image
    :param drawable: Input drawable
    :param colors: FG- and BG-Color (0), Current gradient (1), Current gradient reversed (2)
    :param edge: Edge to curl (1-4, clockwise, starting in the lower right edge)
    :param orientation: Vertical (0), Horizontal (1)
    :param shade: Shade the region under the curl (1) or not (0)
    :return: Curl_Layer
    """
    raise NotImplementedError()


def plug_in_palettemap(image: Image, drawable: Drawable):
    """
    Recolor the image using colors from the active palette

    This plug-in maps the contents of the specified drawable with the active palette. It calculates luminosity of each pixel and replaces the pixel by the palette sample  at the corresponding index. A complete black pixel becomes the lowest palette entry, and complete white becomes the highest. Works on both Grayscale and RGB image with/without alpha channel.

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_papertile(image: Image, drawable: Drawable, tile_size: int, move_max: float, fractional_type: int, wrap_around: int, centering: int, background_type: int, background_color: int, background_alpha: int):
    """
    Cut image into paper tiles, and slide them

    This plug-in cuts an image into paper tiles and slides each paper tile.

    :param image: Input image
    :param drawable: Input drawable
    :param tile_size: Tile size (pixels)
    :param move_max: Max move rate (%)
    :param fractional_type: 0:Background 1:Ignore 2:Force
    :param wrap_around: Wrap around (bool)
    :param centering: Centering (bool)
    :param background_type: 0:Transparent 1:Inverted 2:Image? 3:FG 4:BG 5:Color
    :param background_color: Background color (for bg-type 5)
    :param background_alpha: Opacity (for bg-type 5)
    """
    raise NotImplementedError()


def plug_in_photocopy(image: Image, drawable: Drawable, mask_radius: float, sharpness: float, pct_black: float, pct_white: float):
    """
    Simulate color distortion produced by a copy machine

    Propagates dark values in an image based on each pixel's relative darkness to a neighboring average. The idea behind this filter is to give the look of a photocopied version of the image, with toner transfered based on the relative darkness of a particular region. This is achieved by darkening areas of the image which are measured to be darker than a neighborhood average and setting other pixels to white. In this way, sufficiently large shifts in intensity are darkened to black. The rate at which they are darkened to black is determined by the second pct_black parameter. The mask_radius parameter controls the size of the pixel neighborhood over which the average intensity is computed and then compared to each pixel in the neighborhood to decide whether or not to darken it to black. Large values for mask_radius result in very thick black areas bordering the regions of white and much less detail for black areas everywhere including inside regions of color. Small values result in less toner overall and more detail everywhere. Small values for the pct_black make the blend from the white regions to the black border lines smoother and the toner regions themselves thinner and less noticable; larger values achieve the opposite effect.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param mask_radius: Photocopy mask radius (radius of pixel neighborhood)
    :param sharpness: Sharpness (detail level) (0.0 - 1.0)
    :param pct_black: Percentage of darkened pixels to set to black (0.0 - 1.0)
    :param pct_white: Percentage of non-darkened pixels left white (0.0 - 1.0)
    """
    raise NotImplementedError()


def plug_in_pixelize(image: Image, drawable: Drawable, pixel_width: int):
    """
    Simplify image into an array of solid-colored squares

    Pixelize the contents of the specified drawable with specified pixelizing width.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param pixel_width: Pixel width (the decrease in resolution)
    """
    raise NotImplementedError()


def plug_in_pixelize2(image: Image, drawable: Drawable, pixel_width: int, pixel_height: int):
    """
    Pixelize the contents of the specified drawable

    Pixelize the contents of the specified drawable with speficied pixelizing width.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param pixel_width: Pixel width (the decrease in horizontal resolution)
    :param pixel_height: Pixel height (the decrease in vertical resolution)
    """
    raise NotImplementedError()


def plug_in_plasma(image: Image, drawable: Drawable, seed: int, turbulence: float):
    """
    Create a random plasma texture

    More help

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param seed: Random seed
    :param turbulence: Turbulence of plasma
    """
    raise NotImplementedError()


def plug_in_plug_in_details():
    """
    Display information about plug-ins

    Allows to browse the plug-in menus system. You can search for plug-in names, sort by name or menu location and you can view a tree representation of the plug-in menus. Can also be of help to find where new plug-ins have installed themselves in the menus.
    """
    raise NotImplementedError()


def plug_in_polar_coords(image: Image, drawable: Drawable, circle: float, angle: float, backwards: int, inverse: int, polrec: int):
    """
    Convert image to or from polar coordinates

    Remaps and image from rectangular coordinates to polar coordinates or vice versa

    :param image: Input image
    :param drawable: Input drawable
    :param circle: Circle depth in %
    :param angle: Offset angle
    :param backwards: Map backwards { TRUE, FALSE }
    :param inverse: Map from top { TRUE, FALSE }
    :param polrec: Polar to rectangular { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_qbist(image: Image, drawable: Drawable):
    """
    Generate a huge variety of abstract patterns

    This Plug-in is based on an article by Jörn Loviscach (appeared in c't 10/95, page 326). It generates modern art pictures from a random genetic formula.

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_randomize_hurl(image: Image, drawable: Drawable, rndm_pct: float, rndm_rcount: float, randomize: int, seed: int):
    """
    Completely randomize a fraction of pixels

    This plug-in ``hurls'' randomly-valued pixels onto the selection or image.  You may select the percentage of pixels to modify and the number of times to repeat the process.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param rndm_pct: Randomization percentage (1.0 - 100.0)
    :param rndm_rcount: Repeat count (1.0 - 100.0)
    :param randomize: Use random seed { TRUE, FALSE }
    :param seed: Seed value (used only if randomize is FALSE)
    """
    raise NotImplementedError()


def plug_in_randomize_pick(image: Image, drawable: Drawable, rndm_pct: float, rndm_rcount: float, randomize: int, seed: int):
    """
    Randomly interchange some pixels with neighbors

    This plug-in replaces a pixel with a random adjacent pixel.  You may select the percentage of pixels to modify and the number of times to repeat the process.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param rndm_pct: Randomization percentage (1.0 - 100.0)
    :param rndm_rcount: Repeat count (1.0 - 100.0)
    :param randomize: Use random seed { TRUE, FALSE }
    :param seed: Seed value (used only if randomize is FALSE)
    """
    raise NotImplementedError()


def plug_in_randomize_slur(image: Image, drawable: Drawable, rndm_pct: float, rndm_rcount: float, randomize: int, seed: int):
    """
    Randomly slide some pixels downward (similar to melting)

    This plug-in slurs (melts like a bunch of icicles) an image.  You may select the percentage of pixels to modify and the number of times to repeat the process.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param rndm_pct: Randomization percentage (1.0 - 100.0)
    :param rndm_rcount: Repeat count (1.0 - 100.0)
    :param randomize: Use random seed { TRUE, FALSE }
    :param seed: Seed value (used only if randomize is FALSE)
    """
    raise NotImplementedError()


def plug_in_recompose(image: Image, drawable: Drawable):
    """
    Recompose an image that was previously decomposed

    This function recombines the grayscale layers produced by Decompose into a single RGB or RGBA layer, and replaces the originally decomposed layer with the result.

    :param image: Image to recompose from
    :param drawable: Not used
    """
    raise NotImplementedError()


def plug_in_red_eye_removal(image: Image, drawable: Drawable, threshold: int):
    """
    Remove the red eye effect caused by camera flashes

    This plug-in removes the red eye effect caused by camera flashes by using a percentage based red color threshold.  Make a selection containing the eyes, and apply the filter while adjusting the threshold to accurately remove the red eyes.

    :param image: Input image
    :param drawable: Input drawable
    :param threshold: Red eye threshold in percent
    """
    raise NotImplementedError()


def plug_in_retinex(image: Image, drawable: Drawable, scale: int, nscales: int, scales_mode: int, cvar: float):
    """
    Enhance contrast using the Retinex method

    The Retinex Image Enhancement Algorithm is an automatic image enhancement method that enhances a digital image in terms of dynamic range compression, color independence from the spectral distribution of the scene illuminant, and color/lightness rendition.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param scale: Biggest scale value
    :param nscales: Number of scales
    :param scales_mode: Retinex distribution through scales
    :param cvar: Variance value
    """
    raise NotImplementedError()


def plug_in_rgb_noise(image: Image, drawable: Drawable, independent: int, correlated: int, noise_1: float, noise_2: float, noise_3: float, noise_4: float):
    """
    Distort colors by random amounts

    Add normally distributed (zero mean) random values to image channels.  Noise may be additive (uncorrelated) or multiplicative (correlated - also known as speckle noise). For colour images colour channels may be treated together or independently.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param independent: Noise in channels independent
    :param correlated: Noise correlated (i.e. multiplicative not additive)
    :param noise_1: Noise in the first channel (red, gray)
    :param noise_2: Noise in the second channel (green, gray_alpha)
    :param noise_3: Noise in the third channel (blue)
    :param noise_4: Noise in the fourth channel (alpha)
    """
    raise NotImplementedError()


def plug_in_ripple(image: Image, drawable: Drawable, period: int, amplitude: int, orientation: int, edges: int, waveform: int, antialias: int, tile: int):
    """
    Displace pixels in a ripple pattern

    Ripples the pixels of the specified drawable. Each row or column will be displaced a certain number of pixels coinciding with the given wave form

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param period: Period: number of pixels for one wave to complete
    :param amplitude: Amplitude: maximum displacement of wave
    :param orientation: Orientation { ORIENTATION-HORIZONTAL (0), ORIENTATION-VERTICAL (1) }
    :param edges: Edges { SMEAR (0), WRAP (1), BLANK (2) }
    :param waveform: Waveform { SAWTOOTH (0), SINE (1) }
    :param antialias: Antialias { TRUE, FALSE }
    :param tile: Tileable { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_rotate(image: Image, drawable: Drawable, angle: int, everything: int):
    """
    Rotates a layer or the whole image by 90, 180 or 270 degrees

    This plug-in does rotate the active layer or the whole image clockwise by multiples of 90 degrees. When the whole image is choosen, the image is resized if necessary.

    :param image: Input image
    :param drawable: Input drawable
    :param angle: Angle { 90 (1), 180 (2), 270 (3) } degrees
    :param everything: Rotate the whole image { TRUE, FALSE }
    """
    raise NotImplementedError()


def plug_in_rotate_colormap(image: Image, drawable: Drawable):
    """
    Replace a range of colors with another

    Exchanges two color ranges. Based on code from Pavel Grinfeld (pavel@ml.com). This version written by Sven Anders (anderss@fmi.uni-passau.de).

    :param image: Input image (used for indexed images)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_sample_colorize(image: Image, dst_drawable: Drawable, sample_drawable: Drawable, hold_inten: int, orig_inten: int, rnd_subcolors: int, guess_missing: int, in_low: int, in_high: int, gamma: float, out_low: int, out_high: int):
    """
    Colorize image using a sample image as a guide

    This plug-in colorizes the contents of the specified (gray) layer with the help of a  sample (color) layer. It analyzes all colors in the sample layer. The sample colors are sorted by brightness (== intentisty) and amount and stored in a sample colortable (where brightness is the index) The pixels of the destination layer are remapped with the help of the sample colortable. If use_subcolors is TRUE, the remapping process uses all sample colors of the corresponding brightness-intensity and distributes the subcolors according to their amount in the sample (If the sample has 5 green, 3 yellow, and 1 red pixel of the  intensity value 105, the destination pixels at intensity value 105 are randomly painted in green, yellow and red in a relation of 5:3:1 If use_subcolors is FALSE only one sample color per intensity is used. (green will be used in this example) The brightness intensity value is transformed at the remapping process according to the levels: out_lo, out_hi, in_lo, in_high and gamma The in_low / in_high levels specify an initial mapping of the intensity. The gamma value determines how intensities are interpolated between the in_lo and in_high levels. A gamma value of 1.0 results in linear interpolation. Higher gamma values results in more high-level intensities Lower gamma values results in more low-level intensities The out_low/out_high levels constrain the resulting intensity index The intensity index is used to pick the corresponding color in the sample colortable. If hold_inten is FALSE the picked color is used 1:1 as resulting remap_color. If hold_inten is TRUE The brightness of the picked color is adjusted back to the origial intensity value (only hue and saturation are taken from the picked sample color) (or to the input level, if orig_inten is set FALSE) Works on both Grayscale and RGB image with/without alpha channel. (the image with the dst_drawable is converted to RGB if necessary) The sample_drawable should be of type RGB or RGBA

    :param image: Input image (unused)
    :param dst_drawable: The drawable to be colorized (Type GRAY* or RGB*)
    :param sample_drawable: Sample drawable (should be of Type RGB or RGBA)
    :param hold_inten: hold brightness intensity levels (TRUE, FALSE)
    :param orig_inten: TRUE: hold brightness of original intensity levels. FALSE: Hold Intensity of input levels
    :param rnd_subcolors: TRUE: Use all subcolors of same intensity, FALSE: use only one color per intensity
    :param guess_missing: TRUE: guess samplecolors for the missing intensity values FALSE: use only colors found in the sample
    :param in_low: intensity of lowest input (0 <= in_low <= 254)
    :param in_high: intensity of highest input (1 <= in_high <= 255)
    :param gamma: gamma correction factor (0.1 <= gamma <= 10) where 1.0 is linear
    :param out_low: lowest sample color intensity (0 <= out_low <= 254)
    :param out_high: highest sample color intensity (1 <= out_high <= 255)
    """
    raise NotImplementedError()


def plug_in_scatter_hsv(image: Image, drawable: Drawable, holdness: int, hue_distance: int, saturation_distance: int, value_distance: int):
    """
    Scattering pixel values in HSV space

    Scattering pixel values in HSV space

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param holdness: convolution strength
    :param hue_distance: scattering of hue angle [0,180]
    :param saturation_distance: distribution distance on saturation axis [0,255]
    :param value_distance: distribution distance on value axis [0,255]
    """
    raise NotImplementedError()


def plug_in_screenshot(root: int, window_id: int, x1: int, y1: int, x2: int, y2: int) -> Image:
    """
    Create an image from an area of the screen

    The plug-in allows to take screenshots of an interactively selected window or of the desktop, either the whole desktop or an interactively selected region. When called non-interactively, it may grab the root window or use the window-id passed as a parameter.  The last four parameters are optional and can be used to specify the corners of the region to be grabbed.

    :param root: Root window { TRUE, FALSE }
    :param window_id: Window id
    :param x1: (optional) Region left x coord
    :param y1: (optional) Region top y coord
    :param x2: (optional) Region right x coord
    :param y2: (optional) Region bottom y coord
    :return: image
    """
    raise NotImplementedError()


def plug_in_script_fu_console():
    """
    Interactive console for Script-Fu development

    Provides an interface which allows interactive scheme development.
    """
    raise NotImplementedError()


def plug_in_script_fu_eval(code: str):
    """
    Evaluate scheme code

    Evaluate the code under the scheme interpreter (primarily for batch mode)

    :param code: The code to evaluate
    """
    raise NotImplementedError()


def plug_in_script_fu_server(ip: str, port: int, logfile: str):
    """
    Server for remote Script-Fu operation

    Provides a server for remote script-fu operation. NOTE that for security reasons this procedure's API was changed in an incompatible way since GIMP 2.8.12. You now have to pass the IP to listen on as first parameter. Calling this procedure with the old API will fail on purpose.

    :param ip: The ip on which to listen for requests
    :param port: The port on which to listen for requests
    :param logfile: The file to log server activity to
    """
    raise NotImplementedError()


def plug_in_script_fu_text_console():
    """
    Provides a text console mode for script-fu development

    Provides an interface which allows interactive scheme development.
    """
    raise NotImplementedError()


def plug_in_sel_gauss(image: Image, drawable: Drawable, radius: float, max_delta: int):
    """
    Blur neighboring pixels, but only in low-contrast areas

    This filter functions similar to the regular gaussian blur filter except that neighbouring pixels that differ more than the given maxdelta parameter will not be blended with. This way with the correct parameters, an image can be smoothed out without losing details. However, this filter can be rather slow.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param radius: Radius of gaussian blur (in pixels, > 0.0)
    :param max_delta: Maximum delta
    """
    raise NotImplementedError()


def plug_in_sel2path(image: Image, drawable: Drawable):
    """
    Converts a selection to a path

    Converts a selection to a path

    :param image: Input image
    :param drawable: Input drawable (unused)
    """
    raise NotImplementedError()


def plug_in_sel2path_advanced(image: Image, drawable: Drawable, align_threshold: float, corner_always_threshold: float, corner_surround: int, corner_threshold: float, error_threshold: float, filter_alternative_surround: int, filter_epsilon: float, filter_iteration_count: int, filter_percent: float, filter_secondary_surround: int, filter_surround: int, keep_knees: int, line_reversion_threshold: float, line_threshold: float, reparameterize_improvement: float, reparameterize_threshold: float, subdivide_search: float, subdivide_surround: int, subdivide_threshold: float, tangent_surround: int):
    """
    Converts a selection to a path (with advanced user menu)

    Converts a selection to a path (with advanced user menu)

    :param image: Input image
    :param drawable: Input drawable (unused)
    :param align_threshold: align_threshold
    :param corner_always_threshold: corner_always_threshold
    :param corner_surround: corner_surround
    :param corner_threshold: corner_threshold
    :param error_threshold: error_threshold
    :param filter_alternative_surround: filter_alternative_surround
    :param filter_epsilon: filter_epsilon
    :param filter_iteration_count: filter_iteration_count
    :param filter_percent: filter_percent
    :param filter_secondary_surround: filter_secondary_surround
    :param filter_surround: filter_surround
    :param keep_knees: {1-Yes, 0-No}
    :param line_reversion_threshold: line_reversion_threshold
    :param line_threshold: line_threshold
    :param reparameterize_improvement: reparameterize_improvement
    :param reparameterize_threshold: reparameterize_threshold
    :param subdivide_search: subdivide_search
    :param subdivide_surround: subdivide_surround
    :param subdivide_threshold: subdivide_threshold
    :param tangent_surround: tangent_surround
    """
    raise NotImplementedError()


def plug_in_semiflatten(image: Image, drawable: Drawable):
    """
    Replace partial transparency with the current background color

    This plugin flattens pixels in an RGBA image that aren't completely transparent against the current GIMP background color

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_sharpen(image: Image, drawable: Drawable, percent: int):
    """
    Make image sharper (less powerful than Unsharp Mask)

    This plug-in selectively performs a convolution filter on an image.

    :param image: Input image
    :param drawable: Input drawable
    :param percent: Percent sharpening (default = 10)
    """
    raise NotImplementedError()


def plug_in_shift(image: Image, drawable: Drawable, shift_amount: int, orientation: int):
    """
    Shift each row of pixels by a random amount

    Shifts the pixels of the specified drawable. Each row will be displaced a random value of pixels.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param shift_amount: shift amount (0 <= shift_amount_x <= 200)
    :param orientation: vertical, horizontal orientation
    """
    raise NotImplementedError()


def plug_in_sinus(image: Image, drawable: Drawable, xscale: float, yscale: float, complex: float, seed: int, tiling: int, perturb: int, colors: int, col1: Color, col2: Color, alpha1: float, alpha2: float, blend: int, blend_power: float):
    """
    Generate complex sinusoidal textures

    FIX ME: sinus help

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param xscale: Scale value for x axis
    :param yscale: Scale value dor y axis
    :param complex: Complexity factor
    :param seed: Seed value for random number generator
    :param tiling: If set, the pattern generated will tile
    :param perturb: If set, the pattern is a little more distorted...
    :param colors: where to take the colors (0= B&W,  1= fg/bg, 2= col1/col2)
    :param col1: fist color (sometimes unused)
    :param col2: second color (sometimes unused)
    :param alpha1: alpha for the first color (used if the drawable has an alpha chanel)
    :param alpha2: alpha for the second color (used if the drawable has an alpha chanel)
    :param blend: 0= linear, 1= bilinear, 2= sinusoidal
    :param blend_power: Power used to strech the blend
    """
    raise NotImplementedError()


def plug_in_small_tiles(image: Image, drawable: Drawable, num_tiles: int):
    """
    Tile image into smaller versions of the original

    More here later

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param num_tiles: Number of tiles to make
    """
    raise NotImplementedError()


def plug_in_smooth_palette(image: Image, drawable: Drawable, width: int, height: int, ntries: int, show_image: int) -> Tuple[Image, Layer]:
    """
    Derive a smooth color palette from the image

    help!

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param width: Width
    :param height: Height
    :param ntries: Search Depth
    :param show_image: Show Image?
    :return: new_image, new_layer
    """
    raise NotImplementedError()


def plug_in_sobel(image: Image, drawable: Drawable, horizontal: int, vertical: int, keep_sign: int):
    """
    Specialized direction-dependent edge detection

    This plugin calculates the gradient with a sobel operator. The user can specify which direction to use. When both directions are used, the result is the RMS of the two gradients; if only one direction is used, the result either the absolut value of the gradient, or 127 + gradient (if the 'keep sign' switch is on). This way, information about the direction of the gradient is preserved. Resulting images are not autoscaled.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param horizontal: Sobel in horizontal direction
    :param vertical: Sobel in vertical direction
    :param keep_sign: Keep sign of result (one direction only)
    """
    raise NotImplementedError()


def plug_in_softglow(image: Image, drawable: Drawable, glow_radius: float, brightness: float, sharpness: float):
    """
    Simulate glow by making highlights intense and fuzzy

    Gives an image a softglow effect by intensifying the highlights in the image. This is done by screening a modified version of the drawable with itself. The modified version is desaturated and then a sigmoidal transfer function is applied to force the distribution of intensities into very small and very large only. This desaturated version is then blurred to give it a fuzzy 'vaseline-on-the-lens' effect. The glow radius parameter controls the sharpness of the glow effect. The brightness parameter controls the degree of intensification applied to image highlights. The sharpness parameter controls how defined or alternatively, diffuse, the glow effect should be.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param glow_radius: Glow radius (radius in pixels)
    :param brightness: Glow brightness (0.0 - 1.0)
    :param sharpness: Glow sharpness (0.0 - 1.0)
    """
    raise NotImplementedError()


def plug_in_solid_noise(image: Image, drawable: Drawable, tilable: int, turbulent: int, seed: int, detail: int, xsize: float, ysize: float):
    """
    Create a random cloud-like texture

    Generates 2D textures using Perlin's classic solid noise function.

    :param image: Input image
    :param drawable: Input drawable
    :param tilable: Create a tilable output { TRUE, FALSE }
    :param turbulent: Make a turbulent noise { TRUE, FALSE }
    :param seed: Random seed
    :param detail: Detail level (0 - 15)
    :param xsize: Horizontal texture size
    :param ysize: Vertical texture size
    """
    raise NotImplementedError()


def plug_in_sparkle(image: Image, drawable: Drawable, lum_threshold: float, flare_inten: float, spike_len: int, spike_pts: int, spike_angle: int, density: float, transparency: float, random_hue: float, random_saturation: float, preserve_luminosity: int, inverse: int, border: int, color_type: int):
    """
    Turn bright spots into starry sparkles

    Uses a percentage based luminoisty threhsold to find candidate pixels for adding some sparkles (spikes). 

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param lum_threshold: Luminosity threshold (0.0 - 1.0)
    :param flare_inten: Flare intensity (0.0 - 1.0)
    :param spike_len: Spike length (in pixels)
    :param spike_pts: # of spike points
    :param spike_angle: Spike angle (0-360 degrees, -1: random)
    :param density: Spike density (0.0 - 1.0)
    :param transparency: Transparency (0.0 - 1.0)
    :param random_hue: Random hue (0.0 - 1.0)
    :param random_saturation: Random saturation (0.0 - 1.0)
    :param preserve_luminosity: Preserve luminosity (TRUE/FALSE)
    :param inverse: Inverse (TRUE/FALSE)
    :param border: Add border (TRUE/FALSE)
    :param color_type: Color of sparkles: { NATURAL (0), FOREGROUND (1), BACKGROUND (2) }
    """
    raise NotImplementedError()


def plug_in_spheredesigner(image: Image, drawable: Drawable):
    """
    Create an image of a textured sphere

    This plugin can be used to create textured and/or bumpmapped spheres, and uses a small lightweight raytracer to perform the task with good quality

    :param image: Input image (unused)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_spread(image: Image, drawable: Drawable, spread_amount_x: float, spread_amount_y: float):
    """
    Move pixels around randomly

    Spreads the pixels of the specified drawable.  Pixels are randomly moved to another location whose distance varies from the original by the horizontal and vertical spread amounts 

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param spread_amount_x: Horizontal spread amount (0 <= spread_amount_x <= 200)
    :param spread_amount_y: Vertical spread amount (0 <= spread_amount_y <= 200)
    """
    raise NotImplementedError()


def plug_in_threshold_alpha(image: Image, drawable: Drawable, threshold: int):
    """
    Make transparency all-or-nothing


    :param image: Input image (not used)
    :param drawable: Input drawable
    :param threshold: Threshold
    """
    raise NotImplementedError()


def plug_in_tile(image: Image, drawable: Drawable, new_width: int, new_height: int, new_image: int) -> Tuple[Image, Layer]:
    """
    Create an array of copies of the image

    This function creates a new image with a single layer sized to the specified 'new_width' and 'new_height' parameters.  The specified drawable is tiled into this layer.  The new layer will have the same type as the specified drawable and the new image will have a corresponding base type.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param new_width: New (tiled) image width
    :param new_height: New (tiled) image height
    :param new_image: Create a new image?
    :return: new_image, new_layer
    """
    raise NotImplementedError()


def plug_in_unit_editor():
    """
    Create or alter units used in GIMP

    The GIMP unit editor
    """
    raise NotImplementedError()


def plug_in_unsharp_mask(image: Image, drawable: Drawable, radius: float, amount: float, threshold: int):
    """
    The most widely useful method for sharpening an image

    The unsharp mask is a sharpening filter that works by comparing using the difference of the image and a blurred version of the image.  It is commonly used on photographic images, and is provides a much more pleasing result than the standard sharpen filter.

    :param image: (unused)
    :param drawable: Drawable to draw on
    :param radius: Radius of gaussian blur (in pixels > 1.0)
    :param amount: Strength of effect
    :param threshold: Threshold (0-255)
    """
    raise NotImplementedError()


def plug_in_video(image: Image, drawable: Drawable, pattern_number: int, additive: int, rotated: int):
    """
    Simulate distortion produced by a fuzzy or low-res monitor

    This function simulates the degradation of being on an old low-dotpitch RGB video monitor to the specified drawable.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param pattern_number: Type of RGB pattern to use
    :param additive: Whether the function adds the result to the original image
    :param rotated: Whether to rotate the RGB pattern by ninety degrees
    """
    raise NotImplementedError()


def plug_in_vinvert(image: Image, drawable: Drawable):
    """
    Invert the brightness of each pixel

    This function takes an indexed/RGB image and inverts its 'value' in HSV space.  The upshot of this is that the color and saturation at any given point remains the same, but its brightness is effectively inverted.  Quite strange.  Sometimes produces unpleasant color artifacts on images from lossy sources (ie. JPEG).

    :param image: Input image (used for indexed images)
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def plug_in_vpropagate(image: Image, drawable: Drawable, propagate_mode: int, propagating_channel: int, propagating_rate: float, direction_mask: int, lower_limit: int, upper_limit: int):
    """
    Propagate certain colors to neighboring pixels

    Propagate values of the layer

    :param image: Input image (not used)
    :param drawable: Input drawable
    :param propagate_mode: propagate 0:white, 1:black, 2:middle value 3:foreground to peak, 4:foreground, 5:background, 6:opaque, 7:transparent
    :param propagating_channel: channels which values are propagated
    :param propagating_rate: 0.0 <= propagatating_rate <= 1.0
    :param direction_mask: 0 <= direction-mask <= 15
    :param lower_limit: 0 <= lower-limit <= 255
    :param upper_limit: 0 <= upper-limit <= 255
    """
    raise NotImplementedError()


def plug_in_warp(image: Image, drawable: Drawable, amount: float, warp_map: Drawable, iter: int, dither: float, angle: float, wrap_type: int, mag_map: Drawable, mag_use: int, substeps: int, grad_map: int, grad_scale: float, vector_map: int, vector_scale: float, vector_angle: float):
    """
    Twist or smear image in many different ways

    Smears an image along vector paths calculated as the gradient of a separate control matrix. The effect can look like brushstrokes of acrylic or watercolor paint, in some cases.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param amount: Pixel displacement multiplier
    :param warp_map: Displacement control map
    :param iter: Iteration count (last required argument)
    :param dither: Random dither amount (first optional argument)
    :param angle: Angle of gradient vector rotation
    :param wrap_type: Edge behavior: { WRAP (0), SMEAR (1), BLACK (2), COLOR (3) }
    :param mag_map: Magnitude control map
    :param mag_use: Use magnitude map: { FALSE (0), TRUE (1) }
    :param substeps: Substeps between image updates
    :param grad_map: Gradient control map
    :param grad_scale: Scaling factor for gradient map (0=don't use)
    :param vector_map: Fixed vector control map
    :param vector_scale: Scaling factor for fixed vector map (0=don't use)
    :param vector_angle: Angle for fixed vector map
    """
    raise NotImplementedError()


def plug_in_waves(image: Image, drawable: Drawable, amplitude: float, phase: float, wavelength: float, type: int, reflective: int):
    """
    Distort the image with waves

    none yet

    :param image: The Image
    :param drawable: The Drawable
    :param amplitude: The Amplitude of the Waves
    :param phase: The Phase of the Waves
    :param wavelength: The Wavelength of the Waves
    :param type: Type of waves, black/smeared
    :param reflective: Use Reflection
    """
    raise NotImplementedError()


def plug_in_web_browser(url: str):
    """
    Open an URL in the user specified web browser

    Opens the given URL in the user specified web browser.

    :param url: URL to open
    """
    raise NotImplementedError()


def plug_in_whirl_pinch(image: Image, drawable: Drawable, whirl: float, pinch: float, radius: float):
    """
    Distort an image by whirling and pinching

    Distorts the image by whirling and pinching, which are two common center-based, circular distortions.  Whirling is like projecting the image onto the surface of water in a toilet and flushing.  Pinching is similar to projecting the image onto an elastic surface and pressing or pulling on the center of the surface.

    :param image: Input image
    :param drawable: Input drawable
    :param whirl: Whirl angle (degrees)
    :param pinch: Pinch amount
    :param radius: Radius (1.0 is the largest circle that fits in the image, and 2.0 goes all the way to the corners)
    """
    raise NotImplementedError()


def plug_in_wind(image: Image, drawable: Drawable, threshold: int, direction: int, strength: int, algorithm: int, edge: int):
    """
    Smear image to give windblown effect

    Renders a wind effect.

    :param image: Input image (unused)
    :param drawable: Input drawable
    :param threshold: Controls where blending will be done >= 0
    :param direction: Left or Right: 0 or 1
    :param strength: Controls the extent of the blending > 1
    :param algorithm: Algorithm { WIND (0), BLAST (1) }
    :param edge: Edge behavior { BOTH (0), LEADING (1), TRAILING (2) }
    """
    raise NotImplementedError()


def plug_in_zealouscrop(image: Image, drawable: Drawable):
    """
    Autocrop unused space from edges and middle


    :param image: Input image
    :param drawable: Input drawable
    """
    raise NotImplementedError()


def python_fu_brush_from_text(font: str, size: int, text: str):
    """
    Create a new brush with characters from a text sequence

    New dynamic brush where each cell is a character from 
    the input text in the chosen font 

    :param font: Font
    :param size: Pixel Size
    :param text: Text
    """
    raise NotImplementedError()


def python_fu_console():
    """
    Interactive GIMP Python interpreter

    Type in commands and see results
    """
    raise NotImplementedError()


def python_fu_eval(code: str):
    """
    Evaluate Python code

    Evaluate python code under the python interpreter (primarily for batch mode)

    :param code: The code to evaluate
    """
    raise NotImplementedError()


def python_fu_foggify(image: Image, drawable: Drawable, name: str, colour: Color, turbulence: float, opacity: float):
    """
    Add a layer of fog

    Adds a layer of fog to the image.

    :param image: Input image
    :param drawable: Input drawable
    :param name: Layer name
    :param colour: Fog color
    :param turbulence: Turbulence
    :param opacity: Opacity
    """
    raise NotImplementedError()


def python_fu_gradient_save_as_css(gradient: str, file_name: str):
    """
    Creates a new palette from a given gradient

    palette_from_gradient (gradient, number, segment_colors) -> None

    :param gradient: Gradient to use
    :param file_name: File Name
    """
    raise NotImplementedError()


def python_fu_palette_offset(palette: str, amount: int) -> str:
    """
    Offset the colors in a palette

    palette_offset (palette, amount) -> modified_palette

    :param palette: Palette
    :param amount: Offset
    :return: new_palette
    """
    raise NotImplementedError()


def python_fu_palette_sort(palette: str, model: str, channel: str, ascending: int):
    """
    Sort the colors in a palette

    palette_merge (palette, model, channel, ascending) -> new_palette

    :param palette: Palette
    :param model: Color model
    :param channel: Channel to sort
    :param ascending: Ascending
    """
    raise NotImplementedError()


def python_fu_palette_to_gradient(palette: str) -> str:
    """
    Create a gradient using colors from the palette

    Create a new gradient using colors from the palette.

    :param palette: Palette
    :return: new_gradient
    """
    raise NotImplementedError()


def python_fu_palette_to_gradient_repeating(palette: str) -> str:
    """
    Create a repeating gradient using colors from the palette

    Create a new repeating gradient using colors from the palette.

    :param palette: Palette
    :return: new_gradient
    """
    raise NotImplementedError()


def python_fu_slice(image: Image, drawable: Drawable, save_path: str, html_filename: str, image_basename: str, image_extension: str, separate_image_dir: int, relative_image_path: str, cellspacing: int, animate: int, skip_caps: int):
    """
    Cuts an image along its guides, creates images and a HTML table snippet

    Add guides to an image. Then run this. It will cut along the guides,
        and give you the html to reassemble the resulting images. If you
        choose to generate javascript for onmouseover and clicked events, it
        will use the lower three visible layers on the image for normal,
        onmouseover and clicked states, in that order. If skip caps is
        enabled, table cells on the edge of the table won't become animated,
        and its images will be taken from the active layer.

    :param image: Input image
    :param drawable: Input drawable
    :param save_path: Path for HTML export
    :param html_filename: Filename for export
    :param image_basename: Image name prefix
    :param image_extension: Image format
    :param separate_image_dir: Separate image folder
    :param relative_image_path: Folder for image export
    :param cellspacing: Space between table elements
    :param animate: Javascript for onmouseover and clicked
    :param skip_caps: Skip animation for table caps
    """
    raise NotImplementedError()


def script_fu_3d_outline_logo(pattern: str, string: str, value: float, font: str, toggle: int):
    """
    Create a logo with outlined text and a drop shadow


    :param pattern: Pattern
    :param string: Text
    :param value: Shadow Y offset
    :param font: Font
    :param toggle: Default bumpmap settings
    """
    raise NotImplementedError()


def script_fu_3d_outline_logo_alpha(image: Image, drawable: Drawable, pattern: str, value: float, toggle: int):
    """
    Outline the selected region (or alpha) with a pattern and add a drop shadow


    :param image: Image
    :param drawable: Drawable
    :param pattern: Pattern
    :param value: Shadow Y offset
    :param toggle: Default bumpmap settings
    """
    raise NotImplementedError()


def script_fu_3dtruchet(value: float, color: Color, toggle: int):
    """
    Create an image filled with a 3D Truchet pattern


    :param value: Number of Y tiles
    :param color: End blend
    :param toggle: Supersample
    """
    raise NotImplementedError()


def script_fu_add_bevel(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Add a beveled border to an image


    :param image: Image
    :param drawable: Drawable
    :param value: Thickness
    :param toggle: Keep bump layer
    """
    raise NotImplementedError()


def script_fu_addborder(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add a border around an image


    :param image: Input image
    :param drawable: Input drawable
    :param value: Delta value on color
    :param color: Border color
    """
    raise NotImplementedError()


def script_fu_alien_glow_bullet(value: float, color: Color, toggle: int):
    """
    Create a bullet graphic with an eerie glow for web pages


    :param value: Radius
    :param color: Background color
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_alien_glow_button(string: str, font: str, value: float, color: Color, toggle: int):
    """
    Create a button graphic with an eerie glow for web pages


    :param string: Text
    :param font: Font
    :param value: Glow radius
    :param color: Background color
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_alien_glow_horizontal_ruler(value: float, color: Color, toggle: int):
    """
    Create an Hrule graphic with an eerie glow for web pages


    :param value: Bar height
    :param color: Background color
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_alien_glow_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo with an alien glow around the text


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Glow color
    """
    raise NotImplementedError()


def script_fu_alien_glow_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add an eerie glow around the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Glow size (pixels * 4)
    :param color: Glow color
    """
    raise NotImplementedError()


def script_fu_alien_glow_right_arrow(value: float, option: int, color: Color, toggle: int):
    """
    Create an arrow graphic with an eerie glow for web pages


    :param value: Size
    :param option: Orientation
    :param color: Background color
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_alien_neon_logo(string: str, value: float, font: str, color: Color, toggle: int):
    """
    Create a logo with psychedelic outlines around the text


    :param string: Text
    :param value: Number of bands
    :param font: Font
    :param color: Background color
    :param toggle: Fade away
    """
    raise NotImplementedError()


def script_fu_alien_neon_logo_alpha(image: Image, drawable: Drawable, color: Color, value: float, toggle: int):
    """
    Add psychedelic outlines to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param color: Background color
    :param value: Number of bands
    :param toggle: Fade away
    """
    raise NotImplementedError()


def script_fu_basic1_logo(string: str, value: float, font: str, color: Color):
    """
    Create a plain text logo with a gradient effect, a drop shadow, and a background


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Text color
    """
    raise NotImplementedError()


def script_fu_basic1_logo_alpha(image: Image, drawable: Drawable, color: Color):
    """
    Add a gradient effect, a drop shadow, and a background to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param color: Text color
    """
    raise NotImplementedError()


def script_fu_basic2_logo(string: str, value: float, font: str, color: Color):
    """
    Create a simple logo with a shadow and a highlight


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Text color
    """
    raise NotImplementedError()


def script_fu_basic2_logo_alpha(image: Image, drawable: Drawable, color: Color):
    """
    Add a shadow and a highlight to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param color: Text color
    """
    raise NotImplementedError()


def script_fu_beveled_pattern_arrow(value: float, option: int, pattern: str):
    """
    Create a beveled pattern arrow for webpages


    :param value: Size
    :param option: Orientation
    :param pattern: Pattern
    """
    raise NotImplementedError()


def script_fu_beveled_pattern_bullet(value: float, pattern: str, toggle: int):
    """
    Create a beveled pattern bullet for webpages


    :param value: Diameter
    :param pattern: Pattern
    :param toggle: Transparent background
    """
    raise NotImplementedError()


def script_fu_beveled_pattern_button(string: str, value: float, font: str, color: Color, pattern: str, toggle: int):
    """
    Create a beveled pattern button for webpages


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Text color
    :param pattern: Pattern
    :param toggle: Pressed
    """
    raise NotImplementedError()


def script_fu_beveled_pattern_heading(string: str, value: float, font: str, pattern: str, toggle: int):
    """
    Create a beveled pattern heading for webpages


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param pattern: Pattern
    :param toggle: Transparent background
    """
    raise NotImplementedError()


def script_fu_beveled_pattern_hrule(value: float, pattern: str):
    """
    Create a beveled pattern hrule for webpages


    :param value: Height
    :param pattern: Pattern
    """
    raise NotImplementedError()


def script_fu_blend_anim(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Create intermediate layers to blend two or more layers over a background as an animation


    :param image: Image
    :param drawable: Drawable
    :param value: Max. blur radius
    :param toggle: Looped
    """
    raise NotImplementedError()


def script_fu_blended_logo(string: str, value: float, font: str, color: Color, option: int, gradient: str, toggle: int):
    """
    Create a logo with blended backgrounds, highlights, and shadows


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: End blend
    :param option: Blend mode
    :param gradient: Gradient
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_blended_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color, option: int, gradient: str, toggle: int):
    """
    Add blended backgrounds, highlights, and shadows to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Offset (pixels)
    :param color: End blend
    :param option: Blend mode
    :param gradient: Gradient
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_bovinated_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo with text in the style of 'cow spots'


    :param string: Text
    :param value: Spots density Y
    :param font: Font
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_bovinated_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add 'cow spots' to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Spots density Y
    :param color: Background Color
    """
    raise NotImplementedError()


def script_fu_burn_in_anim(image: Image, drawable: Drawable, color: Color, toggle: int, value: str):
    """
    Create intermediate layers to produce an animated 'burn-in' transition between two layers


    :param image: The image
    :param drawable: Layer to animate
    :param color: Glow color
    :param toggle: Prepare for GIF
    :param value: Speed (pixels/frame)
    """
    raise NotImplementedError()


def script_fu_button00(string: str, value: float, font: str, color: Color, toggle: int):
    """
    Create a simple, beveled button graphic for webpages


    :param string: Text
    :param value: Bevel width
    :param font: Font
    :param color: Text color
    :param toggle: Pressed
    """
    raise NotImplementedError()


def script_fu_camo_pattern(value: float, color: Color, toggle: int):
    """
    Create an image filled with a camouflage pattern


    :param value: Granularity
    :param color: Color 3
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_carve_it(image: Image, drawable: Drawable, toggle: int):
    """
    Use the specified [GRAY] drawable as a stencil to carve from the specified image. The specified image must be either RGB colour or grayscale, not indexed.


    :param image: Mask image
    :param drawable: Image to carve
    :param toggle: Carve white areas
    """
    raise NotImplementedError()


def script_fu_carved_logo(string: str, value: float, font: str, filename: str, toggle: int):
    """
    Create a logo with text raised above or carved in to the specified background image


    :param string: Text
    :param value: Padding around text
    :param font: Font
    :param filename: Background Image
    :param toggle: Carve raised text
    """
    raise NotImplementedError()


def script_fu_chalk_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo resembling chalk scribbled on a blackboard


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Chalk color
    """
    raise NotImplementedError()


def script_fu_chalk_logo_alpha(image: Image, drawable: Drawable, color: Color):
    """
    Create a chalk drawing effect for the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_chip_away_logo(string: str, font: str, value: float, toggle: int, pattern: str):
    """
    Create a logo resembling a chipped wood carving


    :param string: Text
    :param font: Font
    :param value: Blur amount
    :param toggle: Keep background
    :param pattern: Pattern
    """
    raise NotImplementedError()


def script_fu_chip_away_logo_alpha(image: Image, drawable: Drawable, value: float, toggle: int, pattern: str):
    """
    Add a chipped woodcarving effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Blur amount
    :param toggle: Keep background
    :param pattern: Pattern
    """
    raise NotImplementedError()


def script_fu_chrome_logo(string: str, value: float, font: str, color: Color):
    """
    Create a simplistic, but cool, chromed logo


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_chrome_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add a simple chrome effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Offsets (pixels * 2)
    :param color: Background Color
    """
    raise NotImplementedError()


def script_fu_circuit(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Fill the selected region (or alpha) with traces like those on a circuit board


    :param image: Image
    :param drawable: Drawable
    :param value: Circuit seed
    :param toggle: Separate layer
    """
    raise NotImplementedError()


def script_fu_clothify(image: Image, drawable: Drawable, value: float):
    """
    Add a cloth-like texture to the selected region (or alpha)


    :param image: Input image
    :param drawable: Input drawable
    :param value: Depth
    """
    raise NotImplementedError()


def script_fu_coffee_stain(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Add realistic looking coffee stains to the image


    :param image: The image
    :param drawable: The layer
    :param value: Stains
    :param toggle: Darken only
    """
    raise NotImplementedError()


def script_fu_comic_logo(string: str, value: float, font: str, gradient: str, toggle: int, color: Color):
    """
    Create a comic-book style logo by outlining and filling with a gradient


    :param string: Text
    :param value: Outline size
    :param font: Font
    :param gradient: Gradient
    :param toggle: Gradient reverse
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_comic_logo_alpha(image: Image, drawable: Drawable, gradient: str, toggle: int, value: float, color: Color):
    """
    Add a comic-book effect to the selected region (or alpha) by outlining and filling with a gradient


    :param image: Image
    :param drawable: Drawable
    :param gradient: Gradient
    :param toggle: Gradient reverse
    :param value: Outline size
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_cool_metal_logo(string: str, value: float, font: str, color: Color, gradient: str, toggle: int):
    """
    Create a metallic logo with reflections and perspective shadows


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Background color
    :param gradient: Gradient
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_cool_metal_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color, gradient: str, toggle: int):
    """
    Add a metallic effect to the selected region (or alpha) with reflections and perspective shadows


    :param image: Image
    :param drawable: Drawable
    :param value: Effect size (pixels)
    :param color: Background color
    :param gradient: Gradient
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_copy_visible(image: Image, drawable: Drawable):
    """
    This procedure is deprecated! Use 'gimp-edit-copy-visible' instead.


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_crystal_logo(value: float, string: str, font: str, filename: str):
    """
    Create a logo with a crystal/gel effect displacing the image underneath


    :param value: Font size (pixels)
    :param string: Text
    :param font: Font
    :param filename: Environment map
    """
    raise NotImplementedError()


def script_fu_difference_clouds(image: Image, drawable: Drawable):
    """
    Solid noise applied with Difference layer mode


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_distress_selection(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Distress the selection


    :param image: The image
    :param drawable: The layer
    :param value: Smooth
    :param toggle: Smooth vertically
    """
    raise NotImplementedError()


def script_fu_drop_shadow(image: Image, drawable: Drawable, value: float, color: Color, toggle: int):
    """
    Add a drop shadow to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Opacity
    :param color: Color
    :param toggle: Allow resizing
    """
    raise NotImplementedError()


def script_fu_erase_rows(image: Image, drawable: Drawable, option: int):
    """
    Erase every other row or column


    :param image: Image
    :param drawable: Drawable
    :param option: Erase/fill
    """
    raise NotImplementedError()


def script_fu_flatland(value: float):
    """
    Create an image filled with a Land Pattern


    :param value: Scale Y
    """
    raise NotImplementedError()


def script_fu_font_map(string: str, toggle: int, value: float, option: int):
    """
    Create an image filled with previews of fonts matching a fontname filter


    :param string: _Filter (regexp)
    :param toggle: _Labels
    :param value: _Border (pixels)
    :param option: _Color scheme
    """
    raise NotImplementedError()


def script_fu_frosty_logo(string: str, value: float, font: str, color: Color):
    """
    Create frozen logo with an added drop shadow


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_frosty_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add a frost effect to the selected region (or alpha) with an added drop shadow


    :param image: Image
    :param drawable: Drawable
    :param value: Effect size (pixels)
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_fuzzy_border(image: Image, drawable: Drawable, color: Color, value: float, toggle: int):
    """
    Add a jagged, fuzzy border to an image


    :param image: The image
    :param drawable: The layer
    :param color: Color
    :param value: Shadow weight (%)
    :param toggle: Flatten image
    """
    raise NotImplementedError()


def script_fu_glossy_logo(string: str, value: float, font: str, gradient: str, toggle: int, color: Color, pattern: str):
    """
    Create a logo with gradients, patterns, shadows, and bump maps


    :param string: Text
    :param value: Shadow Y offset
    :param font: Font
    :param gradient: Blend gradient (outline)
    :param toggle: Shadow
    :param color: Background color
    :param pattern: Pattern (overlay)
    """
    raise NotImplementedError()


def script_fu_glossy_logo_alpha(image: Image, drawable: Drawable, gradient: str, toggle: int, value: float, color: Color, pattern: str):
    """
    Add gradients, patterns, shadows, and bump maps to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param gradient: Blend gradient (outline)
    :param toggle: Shadow
    :param value: Shadow Y offset
    :param color: Background color
    :param pattern: Pattern (overlay)
    """
    raise NotImplementedError()


def script_fu_glowing_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo that looks like glowing hot metal


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_glowing_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add a glowing hot metal effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Effect size (pixels)
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_gradient_bevel_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo with a shiny look and beveled edges


    :param string: Text
    :param value: Bevel width
    :param font: Font
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_gradient_bevel_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color):
    """
    Add a shiny look and bevel effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Bevel width
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_gradient_example(value: float, toggle: int):
    """
    Create an image filled with an example of the current gradient


    :param value: Height
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_grid_system(image: Image, drawable: Drawable, value: str):
    """
    Draw a grid as specified by the lists of X and Y locations using the current brush


    :param image: Image to use
    :param drawable: Drawable to draw grid
    :param value: Y divisions
    """
    raise NotImplementedError()


def script_fu_guide_new(image: Image, drawable: Drawable, option: int, value: float):
    """
    Add a guide at the orientation and position specified (in pixels)


    :param image: Image
    :param drawable: Drawable
    :param option: Direction
    :param value: Position
    """
    raise NotImplementedError()


def script_fu_guide_new_percent(image: Image, drawable: Drawable, option: int, value: float):
    """
    Add a guide at the position specified as a percentage of the image size


    :param image: Input Image
    :param drawable: Input Drawable
    :param option: Direction
    :param value: Position (in %)
    """
    raise NotImplementedError()


def script_fu_guides_from_selection(image: Image, drawable: Drawable):
    """
    Create four guides around the bounding box of the current selection


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_guides_remove(image: Image, drawable: Drawable):
    """
    Remove all horizontal and vertical guides


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_i26_gunya2(string: str, color: Color, font: str, value: float):
    """
    Create a logo in a two-color, scribbled text style


    :param string: Text
    :param color: Frame color
    :param font: Font
    :param value: Frame size
    """
    raise NotImplementedError()


def script_fu_land(value: float, gradient: str):
    """
    Create an image filled with a topographic map pattern


    :param value: Scale Y
    :param gradient: Gradient
    """
    raise NotImplementedError()


def script_fu_lava(image: Image, drawable: Drawable, value: float, gradient: str, toggle: int):
    """
    Fill the current selection with lava


    :param image: Image
    :param drawable: Drawable
    :param value: Roughness
    :param gradient: Gradient
    :param toggle: Use current gradient
    """
    raise NotImplementedError()


def script_fu_line_nova(image: Image, drawable: Drawable, value: float):
    """
    Fill a layer with rays emanating outward from its center using the foreground color


    :param image: Image
    :param drawable: Drawable
    :param value: Randomness
    """
    raise NotImplementedError()


def script_fu_make_brush_elliptical(string: str, value: float):
    """
    Create an elliptical brush


    :param string: Name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_make_brush_elliptical_feathered(string: str, value: float):
    """
    Create an elliptical brush with feathered edges


    :param string: Name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_make_brush_rectangular(string: str, value: float):
    """
    Create a rectangular brush


    :param string: Name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_make_brush_rectangular_feathered(string: str, value: float):
    """
    Create a rectangular brush with feathered edges


    :param string: Name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_neon_logo(string: str, value: float, font: str, color: Color, toggle: int):
    """
    Create a logo in the style of a neon sign


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Glow color
    :param toggle: Create shadow
    """
    raise NotImplementedError()


def script_fu_neon_logo_alpha(image: Image, drawable: Drawable, value: float, color: Color, toggle: int):
    """
    Convert the selected region (or alpha) into a neon-sign like object


    :param image: Image
    :param drawable: Drawable
    :param value: Effect size (pixels)
    :param color: Glow color
    :param toggle: Create shadow
    """
    raise NotImplementedError()


def script_fu_newsprint_text(string: str, font: str, value: float, color: Color):
    """
    Create a logo in the style of newspaper printing


    :param string: Text
    :param font: Font
    :param value: Blur radius
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_old_photo(image: Image, drawable: Drawable, toggle: int, value: float):
    """
    Make an image look like an old photo


    :param image: The image
    :param drawable: The layer
    :param toggle: Work on copy
    :param value: Border size
    """
    raise NotImplementedError()


def script_fu_paste_as_brush(string: str, value: float):
    """
    Paste the clipboard contents into a new brush


    :param string: File name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_paste_as_pattern(string: str):
    """
    Paste the clipboard contents into a new pattern


    :param string: File name
    """
    raise NotImplementedError()


def script_fu_perspective_shadow(image: Image, drawable: Drawable, value: float, color: Color, enum: int, toggle: int):
    """
    Add a perspective shadow to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Opacity
    :param color: Color
    :param enum: Interpolation
    :param toggle: Allow resizing
    """
    raise NotImplementedError()


def script_fu_predator(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Add a 'Predator' effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Pixel amount
    :param toggle: Separate layer
    """
    raise NotImplementedError()


def script_fu_refresh():
    """
    Re-read all available Script-Fu scripts

    Re-read all available Script-Fu scripts
    """
    raise NotImplementedError()


def script_fu_render_map(value: float, gradient: str, toggle: int, option: int):
    """
    Create an image filled with an Earth-like map pattern


    :param value: Granularity
    :param gradient: Gradient
    :param toggle: Gradient reverse
    :param option: Behavior
    """
    raise NotImplementedError()


def script_fu_reverse_layers(image: Image, drawable: Drawable):
    """
    Reverse the order of layers in the image


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_ripply_anim(image: Image, drawable: Drawable, value: float, option: int):
    """
    Create a multi-layer image by adding a ripple effect to the current image


    :param image: Image to animage
    :param drawable: Drawable to animate
    :param value: Number of frames
    :param option: Edge behavior
    """
    raise NotImplementedError()


def script_fu_round_button(string: str, value: float, font: str, color: Color, toggle: int):
    """
    Create images, each containing an oval button graphic


    :param string: Text
    :param value: Round ratio
    :param font: Font
    :param color: Text color (active)
    :param toggle: Pressed
    """
    raise NotImplementedError()


def script_fu_round_corners(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Round the corners of an image and optionally add a drop-shadow and background


    :param image: Image
    :param drawable: Drawable
    :param value: Blur radius
    :param toggle: Work on copy
    """
    raise NotImplementedError()


def script_fu_selection_round(image: Image, drawable: Drawable, value: float):
    """
    This procedure is deprecated! Use 'script-fu-selection-rounded-rectangle' instead.


    :param image: Image
    :param drawable: Drawable
    :param value: Relative radius
    """
    raise NotImplementedError()


def script_fu_selection_rounded_rectangle(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Round the corners of the current selection


    :param image: Image
    :param drawable: Drawable
    :param value: Radius (%)
    :param toggle: Concave
    """
    raise NotImplementedError()


def script_fu_selection_to_brush(image: Image, drawable: Drawable, string: str, value: float):
    """
    Convert a selection to a brush


    :param image: Image
    :param drawable: Drawable
    :param string: File name
    :param value: Spacing
    """
    raise NotImplementedError()


def script_fu_selection_to_image(image: Image, drawable: Drawable):
    """
    Convert a selection to an image


    :param image: Image
    :param drawable: Drawable
    """
    raise NotImplementedError()


def script_fu_selection_to_pattern(image: Image, drawable: Drawable, string: str):
    """
    Convert a selection to a pattern


    :param image: Image
    :param drawable: Drawable
    :param string: File name
    """
    raise NotImplementedError()


def script_fu_set_cmap(image: Image, drawable: Drawable, palette: str):
    """
    Change the colormap of an image to the colors in a specified palette.


    :param image: Image
    :param drawable: Drawable
    :param palette: Palette
    """
    raise NotImplementedError()


def script_fu_slide(image: Image, drawable: Drawable, string: str, font: str, color: Color, toggle: int):
    """
    Add a slide-film like frame, sprocket holes, and labels to an image


    :param image: Image
    :param drawable: Drawable
    :param string: Number
    :param font: Font
    :param color: Font color
    :param toggle: Work on copy
    """
    raise NotImplementedError()


def script_fu_sota_chrome_it(image: Image, drawable: Drawable, value: float, filename: str, color: Color, toggle: int):
    """
    Add a chrome effect to the selected region (or alpha) using a specified (grayscale) stencil


    :param image: Chrome image
    :param drawable: Chrome mask
    :param value: Chrome factor
    :param filename: Environment map
    :param color: Chrome balance
    :param toggle: Chrome white areas
    """
    raise NotImplementedError()


def script_fu_sota_chrome_logo(value: float, string: str, font: str, filename: str, color: Color):
    """
    Create a State Of The Art chromed logo


    :param value: Font size (pixels)
    :param string: Text
    :param font: Font
    :param filename: Environment map
    :param color: Chrome balance
    """
    raise NotImplementedError()


def script_fu_speed_text(string: str, font: str, value: float, color: Color):
    """
    Create a logo with a speedy text effect


    :param string: Text
    :param font: Font
    :param value: Density (%)
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_spinning_globe(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Create an animation by mapping the current image onto a spinning sphere


    :param image: The Image
    :param drawable: The Layer
    :param value: Index to n colors (0 = remain RGB)
    :param toggle: Work on copy
    """
    raise NotImplementedError()


def script_fu_spyrogimp(image: Image, drawable: Drawable, option: int, value: float, brush: str, color: Color, gradient: str):
    """
    Add Spirographs, Epitrochoids, and Lissajous Curves to the current layer


    :param image: Image
    :param drawable: Drawable
    :param option: Color method
    :param value: Start angle
    :param brush: Brush
    :param color: Color
    :param gradient: Gradient
    """
    raise NotImplementedError()


def script_fu_starscape_logo(string: str, value: float, font: str, color: Color):
    """
    Create a logo using a rock-like texture, a nova glow, and shadow


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param color: Glow color
    """
    raise NotImplementedError()


def script_fu_swirl_tile(value: float, color: Color):
    """
    Create an image filled with a swirled tile effect


    :param value: Roughness
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_swirly_pattern(value: float):
    """
    Create an image filled with a swirly pattern


    :param value: Number of times to whirl
    """
    raise NotImplementedError()


def script_fu_t_o_p_logo(string: str, value: float, font: str, toggle: int, color: Color):
    """
    Create a logo using a Trace Of Particles effect


    :param string: Text
    :param value: Edge width
    :param font: Font
    :param toggle: Edge only
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_t_o_p_logo_alpha(image: Image, drawable: Drawable, value: float, toggle: int, color: Color):
    """
    Add a Trace of Particles effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Edge width
    :param toggle: Edge only
    :param color: Background color
    """
    raise NotImplementedError()


def script_fu_text_circle(string: str, value: float, toggle: int, font: str):
    """
    Create a logo by rendering the specified text along the perimeter of a circle


    :param string: Text
    :param value: Font size (pixels)
    :param toggle: Antialias
    :param font: Font
    """
    raise NotImplementedError()


def script_fu_textured_logo(string: str, value: float, font: str, pattern: str, option: int, color: Color):
    """
    Create a textured logo with highlights, shadows, and a mosaic background


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param pattern: Text pattern
    :param option: Mosaic tile type
    :param color: Ending blend
    """
    raise NotImplementedError()


def script_fu_textured_logo_alpha(image: Image, drawable: Drawable, value: float, pattern: str, option: int, color: Color):
    """
    Fill the selected region (or alpha) with a texture and add highlights, shadows, and a mosaic background


    :param image: Image
    :param drawable: Drawable
    :param value: Border size (pixels)
    :param pattern: Pattern
    :param option: Mosaic tile type
    :param color: Ending blend
    """
    raise NotImplementedError()


def script_fu_tile_blur(image: Image, drawable: Drawable, value: float, toggle: int, option: int):
    """
    Blur the edges of an image so the result tiles seamlessly


    :param image: The Image
    :param drawable: The Layer
    :param value: Radius
    :param toggle: Blur horizontally
    :param option: Blur type
    """
    raise NotImplementedError()


def script_fu_title_header(string: str, value: float, font: str, toggle: int):
    """
    Create a decorative web title header


    :param string: Text
    :param value: Font size (pixels)
    :param font: Font
    :param toggle: Gradient reverse
    """
    raise NotImplementedError()


def script_fu_truchet(value: float, color: Color):
    """
    Create an image filled with a Truchet pattern


    :param value: Number of Y tiles
    :param color: Foreground color
    """
    raise NotImplementedError()


def script_fu_unsharp_mask(image: Image, drawable: Drawable, value: float):
    """
    Make a new image from the current layer by applying the unsharp mask method


    :param image: Image
    :param drawable: Drawable to apply
    :param value: Mask opacity
    """
    raise NotImplementedError()


def script_fu_waves_anim(image: Image, drawable: Drawable, value: float, toggle: int):
    """
    Create a multi-layer image with an effect like a stone was thrown into the current image


    :param image: Image
    :param drawable: Drawable
    :param value: Number of frames
    :param toggle: Invert direction
    """
    raise NotImplementedError()


def script_fu_weave(image: Image, drawable: Drawable, value: float):
    """
    Create a new layer filled with a weave effect to be used as an overlay or bump map


    :param image: Image to Weave
    :param drawable: Drawable to Weave
    :param value: Thread intensity
    """
    raise NotImplementedError()


def script_fu_xach_effect(image: Image, drawable: Drawable, value: float, color: Color, toggle: int):
    """
    Add a subtle translucent 3D effect to the selected region (or alpha)


    :param image: Image
    :param drawable: Drawable
    :param value: Drop shadow Y offset
    :param color: Drop shadow color
    :param toggle: Keep selection
    """
    raise NotImplementedError()
