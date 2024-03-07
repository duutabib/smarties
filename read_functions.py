import os
import re
import h5py
import scipy
import numpy as np
from scipy.io import loadmat
from collections.abc import Callable


def get_files_in_dir(dir_path):
    files = os.listdir(dir_path)
    if files.__len__() == 0:
        raise FileNotFoundError()
    return files


def get_label_for_dir(dir_path, filter_pattern="z.*f\d"):
    return re.findall(r'{}'.format(filter_pattern), dir_path)[0]


def sort_files(files, sort_key, reverse=False):
    return sorted(files, key=sort_key) if sort_key else sorted(files, reverse=reverse)


def remove_files_from_dir(files, filenames_to_remove: [list]):
    for filename in filenames_to_remove:
        files.remove(filename)
    return files


# should be moved to the caller
def extract_files_label_for_loading_data(
                                         dir_path,
                                         filter_pattern='z.*f\d+',
                                         filext_to_remove=["README_LICENSE.rtf"],
                                        ):
    files = get_files_in_dir(dir_path)
    label = get_label_for_dir(dir_path, filter_pattern)
    remove_files_from_dir(files, filext_to_remove)
    files = [dir_path + file for file in files]
    return label, *files


# new code starts from here
def read_file(file, function,  function_read_format= 'r'):
    data = function(file, function_read_format)
    return data


def filter_files(data, data_filter='j'):
    return data[data_filter]


def cells_to_eliminate(data, eliminate_filter=''):
    return data[eliminate_filter]


def align_data_with_cells(data, eliminated_cells):
    return [row for j, row in enumerate(data) if j not in list(eliminated_cells)]




def read_data(
        path0,
        path1,
        num_rois,
        d1key='data',
        dholderkey='CellResp',
        cellpositions_var="CellXYZ",
        eliminate_cells_key='IX_inval_anat',
        scells=True,
):
    dholder = h5py.File(path0, "r")
    d0 = dholder[dholderkey][:]  # responses
    d1 = loadmat(path1, simplify_cells=scells)

    eliminated_rois = d1[d1key][eliminate_cells_key]  # rename keys later
    all_rois = d1[d1key][cellpositions_var]  # roi positions x, y, z

    used_rois_coor = np.array(
        [row for j, row in enumerate(all_rois) if j not in list(eliminated_rois)]
    )

    x, y, z = used_rois_coor[:num_rois, :].T

    return x, y, z, d0


def unbox(Filepath):
    """returns 3 outputs resp (response), spon (activity),
    istim (index of stimuli)
    x : data from Filepath read 
    """
    x = loadmat(Filepath, simplify_cells=True)
    resp = x["stim"]["resp"]
    spon = x["stim"]["spont"]
    istm = (x["stim"]["istim"]).astype(np.int32)
    istm -= 1
    nimg = istm.max()
    resp = resp[istm < nimg, :]
    istm = istm[istm < nimg]

    return resp, spon, istm


if __name__ == "__main__":
    filepath = "/Users/duuta/ppp/data/zebf00/"
    x = extract_files_label_for_loading_data(filepath)
    print(x)
