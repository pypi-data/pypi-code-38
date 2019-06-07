"""
Module for the DomainExtendableHeatmap class, which adds domain outlining
functionality for the extendable heatmap system.
"""

from lib5c.plotters.extendable import BaseExtendableHeatmap


class DomainExtendableHeatmap(BaseExtendableHeatmap):
    """
    ExtendableHeatmap mixin class providing ChIP-seq domain outlining
    functionality.
    """
    def outline_domain(self, domain, color='green', linewidth=2, upper=True):
        """
        Outlines a contact domain on the heatmap.

        Parameters
        ----------
        domain : dict
            A genomic feature dict describing the domain to be outlinerd. Should
            be a dict with at least the following keys::

                {
                    'chrom': str,
                    'start': int,
                    'end': int
                }

            'start' and 'end' should be in units of base pairs (this function
            will handle the conversion to heatmap pixel units).
        color : matplotlib color
            The color to outline the domain with.
        linewidth : float
            The line width to use when outlining the domain. Pass a larger
            number for a thicker, more visible outline.
        upper : bool
            Pass True to draw the outline in the upper triangle of the heatmap.
            Pass False to draw it in the lower triangle.
        """
        x_coords = self.transform_feature(domain, axis='x')
        y_coords = self.transform_feature(domain, axis='y')
        xs = [x_coords['start'], x_coords['end']]
        ys = [y_coords['start'], y_coords['start']]
        if upper:
            self['root'].plot(xs, ys, color=color, linewidth=linewidth)
        else:
            self['root'].plot(ys, xs, color=color, linewidth=linewidth)
        xs = [x_coords['end'], x_coords['end']]
        ys = [y_coords['start'], y_coords['end']]
        if upper:
            self['root'].plot(xs, ys, color=color, linewidth=linewidth)
        else:
            self['root'].plot(ys, xs, color=color, linewidth=linewidth)

    def outline_domains(self, domains, color='green', linewidth=2, upper=True):
        """
        Outlines a set of contact domains on the heatmap by repeatedly calling
        ``outline_domain()``.

        Parameters
        ----------
        domains : list of dict
            A list of domains, where each domain is represented as genomic
            feature dict with at least the following keys::

                {
                    'chrom': str,
                    'start': int,
                    'end': int
                }

            'start' and 'end' should be in units of base pairs (this function
            will handle the conversion to heatmap pixel units).
        color : matplotlib color
            The color to outline the domains with.
        linewidth : float
            The line width to use when outlining the domains. Pass a larger
            number for a thicker, more visible outline.
        upper : bool
            Pass True to draw the outlines in the upper triangle of the heatmap.
            Pass False to draw them in the lower triangle.
        """
        for domain in domains:
            self.outline_domain(domain, color=color, linewidth=linewidth,
                                upper=upper)
