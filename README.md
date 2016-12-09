toasty
======

[![Coverage Status](https://coveralls.io/repos/ChrisBeaumont/toasty/badge.png)](https://coveralls.io/r/ChrisBeaumont/toasty)
[![Build Status](https://travis-ci.org/ChrisBeaumont/toasty.png?branch=master)](https://travis-ci.org/ChrisBeaumont/toasty)


Library to build WorldWide Telescope TOAST tiles.


### Dependencies
 * Required: python (2.6, 2.7, 3.2, or 3.3), numpy, cython, Pillow/PIL
 * Optional: astropy (for FITS IO), healpy (for HEALPIX data), pytest (for testing)

### Usage

```python
from toasty import toast
(data_sampler, depth, base_dir, wtml_file=None, merge=True, base_level_only=False, ra_range=None, dec_range=None, toast_tile=None, restart=False, top_layer=0)
```

where:

  * **data_sampler** function or string  
    - A function of (lon, lat) that samples a datasetat the input 2D coordinate arrays
    - A string giving a base toast directory that contains the base level of toasted tiles, using this option, only the merge step takes place, the given directory must contain a "depth" directory for the given depth parameter
  * **depth** int
    - The depth of the tile pyramid to create (4^d tiles are created at a depth of d)
  * **base_dir** str
    - The path to create the files at
  * **wtml_file** str (optional)
    - The path to write a WTML file to. If not present, no file will be written
  * **merge** bool or callable (default True)  
     How to treat lower resolution tiles.
    - If True, tiles above the lowest level (highest resolution) will be computed by averaging and downsampling the 4 subtiles.
    - If False, sampler will be called explicitly for all tiles
    - If a callable object, this object will be passed the 4x oversampled image to downsample
  * **base_level_only** bool (default False)  
     If True only the bottem level of tiles will be created.  
     In this case merge will be set to True, but no merging will happen, and only the highest resolution layer of images will be created.
  * **ra_range** array (optional)
  * **dec_range** array (optional)  
     To toast only a portion of the sky give min and max ras and decs ([minRA,maxRA],[minDec,maxDec]) in degrees.  
     If these keywords are used base_level_only will be automatically set to true, regardless of its given value.
  * **toast_tile** array\[n,x,y\] (optional)  
     If this keyword is used the output will be all the subtiles of toast_tile at the given depth (base_level_only will be automatically set to true, regardless of its given value.
  * **top_layer** int (optional)  
     If merging this indicates the uppermost layer to be created.




Toasty provides a few basic sampler functions:

  * **healpix_sampler** for sampling from healpix arrays
  * **cartesian_sampler** for sampling from cartesian-projections
  * **normalizer** for applying an intensity normalization after sampling

### Examples

To toast an all-sky, Cartesian projection, 8 byte image:

```python
from toasty import toast, cartesian_sampler
from skimage.io import imread

data = imread('allsky.png')
sampler = cartesian_sampler(data)
output = 'toast'
depth = 8  # approximately 0.165"/pixel at highest resolution
toast(sampler, depth, output)
```

To apply a log-stretch to an all sky FITS image:

```python
from toasty import toast, cartesian_sampler, normalizer
from astropy.io import fits

data = fits.open('allsky.fits')[0].data
vmin, vmax = 100, 65535
scaling = 'log'
contrast = 1
sampler = normalizer(cartesian_sampler(data), vmin, vmax
                     scaling, bias, contrast)
output = 'toast'
depth = 8
toast(sampler, depth, output)
```

To perform a custom transformation

```python
from toasty import toast
from astropy.io import fits

data = fits.open('allsky.fits')[0].data

def sampler(x, y):
    """
    x and y are arrays, giving the RA/Dec centers
    (in radians) for each pixel to extract
    """
    ... code to extract a tile from `data` here ...

output = 'toast'
depth = 8
toast(sampler, depth, output)
```


See ``toasty.tile`` for documentation on these functions.


### Using with WorldWide Telescope
To quickly preview a toast directory named `test`, navigate to the directory
where `test` exists and run

```
python -m toasty.viewer test
```

This will start a web server, probably at [http://0.0.0.0:8000](http://0.0.0:8000) (check the output for the actual address). Open this URL in a browser to get a quick look at the data.

For more information about using WorldWide Telescope with custom image data,
see [the official documentation](http://www.worldwidetelescope.org/Docs/worldwidetelescopedatafilesreference.html). The function `toasty.gen_wtml` can generate the wtml information for images generated with toasty.

For an example of tiles generated with Toasty (originally from [Aladin healpix images](http://alasky.u-strasbg.fr/cats/SIMBAD/)), see [The ADS All Sky Survey](http://adsass.org/wwt). The code used to generate these images is [here](https://github.com/ChrisBeaumont/adsass/blob/master/toast/toast.py).
