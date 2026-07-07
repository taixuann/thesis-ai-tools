"""Publication figure export utilities.

Handles multi-format export with correct DPI, journal verification, and
figure size checking.
"""

import os
import matplotlib.pyplot as plt

__all__ = [
    'save_publication_figure',
    'save_for_journal',
    'check_figure_size',
]

# Journal figure dimension requirements (width, max_height) in inches
JOURNAL_DIMENSIONS = {
    'nature': {'single': (3.5, 9.7), 'double': (7.2, 9.7)},
    'science': {'single':  (2.17, 9.17), 'double': (6.89, 9.17)},
    'cell': {'single': (3.35, 9.06), 'double': (7.01, 9.06)},
    'plos': {'single': (3.27, 9.17), 'double': (6.81, 9.17)},
    'acs': {'single': (3.25, 9.0), 'double': (7.0, 9.0)},
}


def save_publication_figure(fig, filename, formats=('pdf', 'png'), dpi=300):
    """Save figure in multiple publication formats.

    Args:
        fig: matplotlib Figure object
        filename: Output filename (without extension)
        formats: Tuple of formats to export ('pdf', 'png', 'eps', 'svg', 'tiff')
        dpi: Resolution in DPI (300 for combined, 600 for line art, 1000+ for fine detail)
    """
    format_config = {
        'pdf': {'dpi': dpi, 'format': 'pdf'},
        'png': {'dpi': dpi, 'format': 'png'},
        'eps': {'dpi': dpi, 'format': 'eps'},
        'svg': {'dpi': dpi, 'format': 'svg'},
        'tiff': {'dpi': dpi, 'format': 'tiff'},
    }

    saved = []
    for fmt in formats:
        if fmt in format_config:
            fpath = f"{filename}.{fmt}"
            config = format_config[fmt]
            kwargs = {'dpi': config['dpi'], 'bbox_inches': 'tight', 'pad_inches': 0.1}
            if fmt == 'tiff':
                kwargs['format'] = 'tiff'
            fig.savefig(fpath, **kwargs)
            saved.append(fpath)

    return saved


def save_for_journal(fig, filename, journal='nature', figure_type='line_art'):
    """Save figure with journal-specific settings.

    Args:
        fig: matplotlib Figure object
        filename: Output filename (without extension)
        journal: Target journal name
        figure_type: 'line_art', 'photograph', or 'combination'
    """
    dpi_map = {
        'line_art': 1000,
        'photograph': 300,
        'combination': 600,
    }
    dpi = dpi_map.get(figure_type, 300)

    formats = ('pdf', 'png')
    if journal == 'acs':
        formats = ('tiff', 'pdf')
    elif journal == 'plos':
        formats = ('tiff', 'png')

    return save_publication_figure(fig, f"{filename}_{journal}", formats=formats, dpi=dpi)


def check_figure_size(fig, journal='nature', figure_width='single'):
    """Check if figure dimensions match journal specifications.

    Args:
        fig: matplotlib Figure object
        journal: Journal name
        figure_width: 'single' or 'double'

    Returns:
        dict with width, height, expected_width, expected_height, passes
    """
    if journal not in JOURNAL_DIMENSIONS:
        return {'error': f"Unknown journal: {journal}"}

    expected_w, expected_h_max = JOURNAL_DIMENSIONS[journal][figure_width]
    fig_w, fig_h = fig.get_size_inches()

    width_pass = abs(fig_w - expected_w) < 0.1
    height_pass = fig_h <= expected_h_max + 0.1

    passes = width_pass and height_pass

    return {
        'width': fig_w,
        'height': fig_h,
        'expected_width': expected_w,
        'max_height': expected_h_max,
        'width_pass': width_pass,
        'height_pass': height_pass,
        'passes': passes,
    }


if __name__ == '__main__':
    fig = plt.figure(figsize=(3.5, 3))
    result = check_figure_size(fig, 'nature', 'single')
    print("Figure size check:", result)
