import os
from jupyterngsplugin.markdown.utils import get_link_image


def diffbind_table(output_suffix, width, height):
    """
    Diffbid report table
    :param output_suffix: Result path
    :param width: Image width
    :param height: Image height
    :return: string
    """
    str_msg = '| Deseq2 | EdgeR |\n'
    str_msg += '| --- | --- |\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plot.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plot.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotHeatmap.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotHeatmap.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotMA.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotMA.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotVolcano.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotVolcano.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotPCA.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotPCA.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotPCA_contrast.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotPCA_contrast.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'
    f1 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_deseq2_plotBox.png'))
    f2 = os.path.relpath(os.path.join(output_suffix, 'Diffbind_edgeR_plotBox.png'))
    str_msg += '| ' + get_link_image(f1, width, height, ' --- ')
    str_msg += '| ' + get_link_image(f2, width, height, ' --- ')
    str_msg += '|\n'

    return str_msg
