import warnings

#attempting to mask FutureWarnings caused by plotnine implimentation
warnings.filterwarnings(
    'ignore',
    category=FutureWarning,
    module='plotnine')

class CowpatchWarning(UserWarning):
    """
    Warnings for cowpatch inconsistancies
    """


