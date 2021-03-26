# flake8: noqa
import pprint

import pytest

import adijif


@pytest.mark.parametrize(
    "attr",
    [
        "ref_clock_max",
        "ref_clock_min",
        "vco_min",
        "vco_max",
        "vco0_min",
        "vco0_max",
        "vco1_min",
        "vco1_max",
        "N",
    ],
)
def test_jesd_unknown_trx(attr):
    transciever_type = "NAN"
    with pytest.raises(
        Exception, match=f"Unknown {attr} for transceiver type {transciever_type}"
    ):
        f = adijif.xilinx()
        f.transciever_type = transciever_type
        d = getattr(f, attr)


def test_jesd_unknown_dev():
    name = "zcu103"
    with pytest.raises(Exception, match=f"No boardname found in library for {name}"):
        f = adijif.xilinx()
        f.setup_by_dev_kit_name(name)


def test_jesd_wrong_order():
    msg = (
        "get_required_clocks must be run to generated"
        + " dependent clocks before names are available"
    )
    with pytest.raises(Exception, match=msg):
        f = adijif.xilinx()
        cn = f.get_required_clock_names()
