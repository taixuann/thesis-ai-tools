# Scientific Color Palettes

## Colorblind-Friendly Palettes

### Okabe-Ito (Recommended for Categories)

```python
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']
```

### Paul Tol Bright (up to 7 categories)

```python
tol_bright = ['#4477AA', '#EE6677', '#228833', '#CCBB44',
              '#66CCEE', '#AA3377', '#BBBBBB']
```

### Paul Tol Muted (up to 9 categories)

```python
tol_muted = ['#332288', '#88CCEE', '#44AA99', '#117733',
             '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
```

### Nature High Contrast (for memristor I-V)

```python
nature_colors = ['#009E73', '#0072B2', '#E69F00', '#CC79A7',
                 '#56B4E9', '#D55E00', '#F0E442', '#000000']
```

## Perceptually Uniform Colormaps

- **Sequential**: viridis, plasma, cividis, magma, inferno
- **Diverging**: RdBu_r, PuOr, BrBG (colorblind-safe)
- **Avoid**: jet, rainbow, RdGy

## Grayscale Compatibility

All figures should be interpretable in grayscale:
1. Different line styles (solid, dashed, dotted)
2. Different marker shapes (circles, squares, triangles)
3. Hatching patterns on bars
4. Sufficient luminance contrast between colors
