"""Publication style presets for matplotlib figures.

Provides one-command journal configuration for Nature, Science, Cell, etc.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = [
    'apply_publication_style',
    'configure_for_journal',
    'set_color_palette',
]

PUBLICATION_RC_PARAMS = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 8,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'axes.linewidth': 1.0,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': False,
    'ytick.right': False,
    'lines.linewidth': 1.5,
    'lines.markersize': 4,
    'legend.fontsize': 7,
    'legend.frameon': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
}

NATURE_RC_PARAMS = {
    **PUBLICATION_RC_PARAMS,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 1.0,
    'font.size': 7,
    'axes.labelsize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
}

SCIENCE_RC_PARAMS = {
    **PUBLICATION_RC_PARAMS,
    'font.size': 8,
    'axes.labelsize': 9,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
}

JOURNALS = {
    'default': PUBLICATION_RC_PARAMS,
    'nature': NATURE_RC_PARAMS,
    'science': SCIENCE_RC_PARAMS,
    'cell': PUBLICATION_RC_PARAMS,
    'plos': PUBLICATION_RC_PARAMS,
}


def apply_publication_style(style='default'):
    """Apply a publication style preset.

    Args:
        style: One of 'default', 'nature', 'science', 'cell', 'plos'
    """
    if style in JOURNALS:
        mpl.rcParams.update(JOURNALS[style])
    else:
        print(f"Unknown style '{style}'. Available: {list(JOURNALS.keys())}")


def configure_for_journal(journal='nature', figure_width='single'):
    """Configure matplotlib for a specific journal.

    Args:
        journal: Journal name ('nature', 'science', 'cell', 'plos', 'acs')
        figure_width: 'single' or 'double' column width
    """
    widths = {
        'nature': {'single': 3.5, 'double': 7.2},
        'science': {'single': 2.17, 'double': 6.89},
        'cell': {'single': 3.35, 'double': 7.01},
        'plos': {'single': 3.27, 'double': 6.81},
        'acs': {'single': 3.25, 'double': 7.0},
    }

    if journal in widths and figure_width in widths[journal]:
        mpl.rcParams['figure.figsize'] = [widths[journal][figure_width], 2.5]
    else:
        mpl.rcParams['figure.figsize'] = [3.5, 2.5]

    apply_publication_style(journal)


def set_color_palette(palette='okabe_ito'):
    """Set the default color cycle.

    Args:
        palette: 'okabe_ito', 'tol_bright', 'tol_muted', 'colorblind'
    """
    palettes = {
        'okabe_ito': ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                       '#0072B2', '#D55E00', '#CC79A7', '#000000'],
        'tol_bright': ['#4477AA', '#EE6677', '#228833', '#CCBB44',
                        '#66CCEE', '#AA3377', '#BBBBBB'],
        'tol_muted': ['#332288', '#88CCEE', '#44AA99', '#117733',
                       '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499'],
        'colorblind': ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                        '#D55E00', '#56B4E9', '#F0E442', '#000000'],
    }

    colors = palettes.get(palette, palettes['okabe_ito'])
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)


if __name__ == '__main__':
    print("Available styles:", list(JOURNALS.keys()))
    print("\nTesting 'nature' style:")
    configure_for_journal('nature', 'single')
    print(f"Figure size: {mpl.rcParams['figure.figsize']}")
    print(f"Font family: {mpl.rcParams['font.sans-serif']}")
