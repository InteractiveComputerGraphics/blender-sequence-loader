from .mzd import readMZD_to_bpymesh,readMZD_to_meshio
from .bgeo import readbgeo_to_meshio

additional_format_loader  ={'.bgeo':readbgeo_to_meshio, '.mzd':readMZD_to_meshio}

__all__ = [readMZD_to_bpymesh,readMZD_to_meshio,readbgeo_to_meshio,additional_format_loader]

