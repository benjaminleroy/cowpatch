import numpy as np
import cowpatch as cow
import pytest

def test_patch__init__():
    """
    test patch's __init__ function to collecting grobs

    Note:
    this test will likely have to converted to passing in
    plotnine and other patch objects...
    """
    pass
    # mypatch = myf(grobs = ["banana", [], "ap"]) # .grobs = ["banan", [], "ap"]
    # assert np.all(mypatch.grobs == ["banana", [], "ap"]), \
    #     "grobs passed through grobs parameter incorrectly"

    # mypatch2 = myf("banana", [], "ap") # .grobs = ["banan", [], "ap"]
    # assert np.all(mypatch2.grobs == ["banana", [], "ap"]), \
    #     "grobs passed through *args incorrectly"

    # with pytest.raises(Exception) as e_info:
    #     myf("banan", [], "ap", grobs = ["banana", [], "ap"]) #error


