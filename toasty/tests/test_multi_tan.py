# -*- mode: python; coding: utf-8 -*-
# Copyright 2019 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import numpy as np
from numpy import testing as nt
import os.path
import pytest

from .. import multi_tan


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

def make_path(*pieces):
    return os.path.join(TESTS_DIR, *pieces)


def test_next_highest_power_of_2():
    assert multi_tan.next_highest_power_of_2(1) == 256
    assert multi_tan.next_highest_power_of_2(256) == 256
    assert multi_tan.next_highest_power_of_2(257) == 512


def check_xml_elements_equal(observed, expected):
    """See if two XML elements are equal through recursive comparison. We do *not*
    check the "tail" text item, and we strip whitespace in "text".

    Derived om `StackExchange <https://stackoverflow.com/a/24349916/3760486>`_.

    """
    if observed.tag != expected.tag:
        return 'expected tag {}, observed tag {}'.format(expected.tag, observed.tag)

    if observed.text is None:
        otext = ''
    else:
        otext = observed.text.strip()

    if expected.text is None:
        etext = ''
    else:
        etext = expected.text.strip()

    if otext != etext:
        return 'expected text {!r} in tag {}, observed {!r}'.format(etext, expected.tag, otext)
    if observed.attrib != expected.attrib:
        return 'expected attrs {!r} in tag {}, observed {!r}'.format(expected.attrib, expected.tag, observed.attrib)
    if len(observed) != len(expected):
        return 'expected {} children of in tag {}, observed {}'.format(len(expected), expected.tag, len(observed))

    for c1, c2 in zip(observed, expected):
        reason = check_xml_elements_equal(c1, c2)
        if reason is not None:
            return reason

    return None

def assert_xml_elements_equal(observed, expected):
    reason = check_xml_elements_equal(observed, expected)
    if reason is not None:
        raise Exception('unequal XML elements: {}'.format(reason))


class TestMultiTan(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_basic(self):
        ds = multi_tan.MultiTanDataSource([make_path('wcs512.fits.gz')])
        ds.compute_global_pixelization()

        WTML = """
<Folder Group="Explorer" Name="TestName">
  <Place Angle="0" DataSetType="Sky" Dec="0.74380165289257" Name="TestName"
         Opacity="100" RA="14.419753086419734" Rotation="0.0"
         ZoomLevel="0.1433599999999144">
    <ForegroundImageSet>
      <ImageSet BandPass="Gamma" BaseDegreesPerTile="0.023893333333319066"
                BaseTileLevel="0" BottomsUp="False" CenterX="216.296296296296"
                CenterY="0.74380165289257" DataSetType="Sky" FileType=".png"
                Name="TestName" OffsetX="4.66666666666388e-05"
                OffsetY="4.66666666666388e-05" Projection="Tan" Rotation="0.0"
                Sparse="True" TileLevels="1" Url="UP{1}/{3}/{3}_{2}.png"
                WidthFactor="2">
        <Credits>CT</Credits>
        <CreditsUrl>CU</CreditsUrl>
        <ThumbnailUrl>TU</ThumbnailUrl>
        <Description>DT</Description>
      </ImageSet>
    </ForegroundImageSet>
  </Place>
</Folder>"""
        from xml.etree import ElementTree as etree
        expected = etree.fromstring(WTML)

        folder = ds.create_wtml(
            name = 'TestName',
            url_prefix = 'UP',
            fov_factor = 1.0,
            bandpass = 'Gamma',
            description_text = 'DT',
            credits_text = 'CT',
            credits_url = 'CU',
            thumbnail_url = 'TU',
        )
        assert_xml_elements_equal(folder, expected)

        from ..pyramid import PyramidIO
        pio = PyramidIO(self.work_path('basic'))
        percentiles = ds.generate_deepest_layer_numpy(pio)

        # These are all hardcoded parameters of this test dataset, derived
        # from a manual processing with checking that the results are correct.
        # Note that to make the file more compressible, I quantized its data,
        # which explains why some of the samples below are identical.

        PERCENTILES = {
            1: 0.098039217,
            99: 0.76862746,
        }

        for pct, expected in PERCENTILES.items():
            nt.assert_almost_equal(percentiles[pct], expected)

        MEAN, TLC, TRC, BLC, BRC = range(5)
        SAMPLES = {
            (0, 0): [0.20828014, 0.20392157, 0.22745098, 0.18431373, 0.20000000],
            (0, 1): [0.22180051, 0.18431373, 0.18823530, 0.16470589, 0.18431373],
            (1, 0): [0.22178716, 0.16470589, 0.18431373, 0.11372549, 0.19607843],
            (1, 1): [0.21140813, 0.18431373, 0.20784314, 0.12549020, 0.14117648],
        }

        for (y, x), expected in SAMPLES.items():
            data = np.load(self.work_path('basic', '1', str(y), '{}_{}.npy'.format(y, x)))
            nt.assert_almost_equal(data.mean(), expected[MEAN])
            nt.assert_almost_equal(data[10,10], expected[TLC])
            nt.assert_almost_equal(data[10,-10], expected[TRC])
            nt.assert_almost_equal(data[-10,10], expected[BLC])
            nt.assert_almost_equal(data[-10,-10], expected[BRC])
