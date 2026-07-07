"""Scientific color palettes for publication figures.

All palettes are colorblind-friendly. Import constants or use apply_palette().
"""

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = [
    'OKABE_ITO',
    'OKABE_ITO_LIST',
    'TOL_BRIGHT',
    'TOL_MUTED',
    'NATURE_HIGH_CONTRAST',
    'apply_palette',
]

# Okabe-Ito palette (recommended for categorical data)
# Distinguishable by all types of color blindness
OKABE_ITO = {
    'orange': '#E69F00',
    'sky_blue': '#56B4E9',
    'bluish_green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'reddish_purple': '#CC79A7',
    'black': '#000000',
}

OKABE_ITO_LIST = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                  '#0072B2', '#D55E00', '#CC79A7', '#000000']

# Paul Tol Bright (up to 7 categories)
TOL_BRIGHT = ['#4477AA', '#EE6677', '#228833', '#CCBB44',
              '#66CCEE', '#AA3377', '#BBBBBB']

# Paul Tol Muted (up to 9 categories)
TOL_MUTED = ['#332288', '#88CCEE', '#44AA99', '#117733',
             '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

# Nature high-contrast (for memristor I-V figures)
NATURE_HIGH_CONTRAST = ['#009E73', '#0072B2', '#E69F00', '#CC79A7',
                        '#56B4E9', '#D55E00', '#F0E442', '#000000']


def apply_palette(palette='okabe_ito'):
    """Set the default matplotlib color cycle to a colorblind-safe palette.

    Args:
        palette: One of 'okabe_ito', 'tol_bright', 'tol_muted',
                 'nature_high_contrast', 'colorblind'
    """
    palettes = {
        'okabe_ito': OKABE_ITO_LIST,
        'tol_bright': TOL_BRIGHT,
        'tol_muted': TOL_MUTED,
        'nature_high_contrast': NATURE_HIGH_CONTRAST,
        'colorblind': ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                        '#D55E00', '#56B4E9', '#F0E442', '#000000'],
    }

    colors = palettes.get(palette, OKABE_ITO_LIST)
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colors)

    # Also set as seaborn palette if available
    try:
        import seaborn as sns
        sns.set_palette(colors)
    except ImportError:
        pass
