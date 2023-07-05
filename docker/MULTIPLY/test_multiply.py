import os
import shutil

from multiply_data_access import DataAccessComponent
from vm_support.sym_linker import create_sym_links
from vm_support.utils import set_permissions


def create_dir(dir):
    try:
        if not os.path.exists(dir):
            os.makedirs(dir)
    except Exception as e:
        print(e)
        print(dir)
    return

from osgeo import osr

wgs84_srs = osr.SpatialReference()
wgs84_srs.ImportFromEPSG(4326)

def get_working_dir(dir_name: str) -> str:
    working_dir = f'/datastore/working_dirs/{dir_name}'
    working_dir = f'/home/jovyan/data/working_dirs/{dir_name}'
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.makedirs(working_dir)
    return working_dir

name = '/tmp'
working_dir = get_working_dir(name)

print(working_dir)


def get_static_data(data_access_component: DataAccessComponent, roi: str, roi_grid: str, start_time: str,
                    stop_time: str, emulation_directory: str, dem_directory: str):
    create_dir(emulation_directory)
    create_dir(dem_directory)

    print('Retrieving emulators ...')
    emu_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'ISO_MSI_A_EMU,ISO_MSI_B_EMU', roi_grid)
    set_permissions(emu_urls)
    create_sym_links(emu_urls, emulation_directory)

    print('Retrieving DEM ...')
    dem_urls = data_access_component.get_data_urls(roi, start_time, stop_time, 'Aster_DEM', roi_grid)
    set_permissions(dem_urls)
    create_sym_links(dem_urls, dem_directory)
    print('Done retrieving static data')

# data_access_component = DataAccessComponent()

# param_roi = 'POLYGON ((5.163574 52.382529, 5.163574 52.529813, 5.493164 52.529813, 5.493164 52.382529, 5.163574 52.382529))'
# spatial_resolution = 20
#
# # define output grid
# param_roi_grid = 'EPSG:4326'
# param_destination_grid = 'EPSG:4326'
#
# param_start_time_as_string = '2008-04-16'
# param_stop_time_as_string = '2008-04-20'
# time_step = 5 # in days
#
# emulators_directory = '{}/emulators'.format(working_dir)
# dem_directory = '{}/dem'.format(working_dir)
#
#
# get_static_data(data_access_component=data_access_component, roi=param_roi,
#                 start_time=param_start_time_as_string, stop_time=param_stop_time_as_string,
#           emulation_directory=emulators_directory, dem_directory=dem_directory, roi_grid=param_roi_grid)