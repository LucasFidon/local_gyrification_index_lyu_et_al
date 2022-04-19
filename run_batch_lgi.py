import os
import csv
import numpy as np
import pandas as pd

KERNEL_VALUE = 108  # default: 316; and for neonats they have used 108 in the paper
THRES_OUTLIERS = 10  # threshold used to compute the mean
SAVE_FOLDER = '/home/lucasf/data/save_res_lgi_v2'  # where all the output will be saved
CSV_RESULTS = os.path.join(SAVE_FOLDER, 'lgi.csv')
COLUMNS = [
    'Patient ID', 'Condition',
    'Mean LGI left hemisphere', 'Mean LGI right hemisphere',
    'Median LGI left hemisphere', 'Median LGI right hemisphere',
    'p5 LGI left hemisphere', 'p5 LGI right hemisphere',
    'p25 LGI left hemisphere', 'p25 LGI right hemisphere',
    'p75 LGI left hemisphere', 'p75 LGI right hemisphere',
    'p95 LGI left hemisphere', 'p95 LGI right hemisphere',
    'IQR LGI left hemisphere', 'IQR LGI right hemisphere',
]

REPO_PATH = '/home/lucasf/workspace/local_gyrification_index_lyu_et_al'
BASE_FOLDER_DATA = '/home/lucasf/data/Fetal_SRR_and_Seg/'
# CDH FOLDERS
CDH_DOAA_AUG20 = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Michael_cases_group', 'CDH_Doaa_Aug20')
CDH_DOAA_DEC19 = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Michael_cases_group', 'CDH_Doaa_Dec19')
CDH = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Nada_cases_group', 'CDH')
DOAA_LONG1 = os.path.join(BASE_FOLDER_DATA, 'Doaa_brain_longitudinal_SRR_and_Seg_MA')
DOAA_LONG2 = os.path.join(BASE_FOLDER_DATA, 'Doaa_brain_longitudinal_SRR_and_Seg_2')
CDH_FOLDERS = [
    CDH_DOAA_AUG20,
    # CDH_DOAA_DEC19,  # we have not corrected the CGM segmentations for them yet
    CDH,
    DOAA_LONG1,
    DOAA_LONG2,
]
# CONTROL FOLDERS
CONTROLS_2 = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Nada_cases_group', 'Controls_2_partial')  # 7
CONTROLS_DOAA = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Michael_cases_group', 'Controls_Doaa_Oct20_MA')  # 7
CONTROLS_EXT_CSF = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Nada_cases_group', 'Controls_with_extcsf_MA')  # 26
CONTROLS_KCL = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_KCL', 'Control')  # 29
CONTROL_FOLDERS = [
    CONTROLS_2,
    CONTROLS_DOAA,
    CONTROLS_EXT_CSF,
    CONTROLS_KCL,
]
# TEST FOLDER
TEST_FOLDER = os.path.join(BASE_FOLDER_DATA, 'SRR_and_Seg_Michael_cases_group', 'test_LGI')

CASES = {
    'Control': [],
    'CDH': [],
    'Test': [],
}
for folder in CDH_FOLDERS:
    for f in os.listdir(folder):
        if not '.' in f:
            path = os.path.join(folder, f)
            CASES['CDH'].append(path)
for folder in CONTROL_FOLDERS:
    for f in os.listdir(folder):
        if not '.' in f:
            path = os.path.join(folder, f)
            CASES['Control'].append(path)
for f in os.listdir(TEST_FOLDER):  # Only for debugging
    if not '.' in f:
        path = os.path.join(TEST_FOLDER, f)
        CASES['Test'].append(path)

#TODO
#CASES['Control'] = CASES['Control'][:14]


def load_csv_results():
    if not os.path.exists(CSV_RESULTS):
        print('Parameters tuning csv %s not found.' % CSV_RESULTS)
        return None
    data = pd.read_csv(CSV_RESULTS)
    return data


def was_lgi_already_evaluated(pat_id):
    data = load_csv_results()
    if data is None:
        return False
    data = data[data[COLUMNS[0]] == pat_id]
    if len(data) == 0:
        return False
    return True


def update_csv(pat_id, condition, lgi_left, lgi_right):
    """
    Add a new row to the CSV file.
    The rows are reordered in patient ID alphabetical order.
    :param pat_id: patient ID
    :param lgi_left: LGI values for the left hemisphere
    :param lgi_right: LGI values for the right hemisphere
    """
    lgi_left = lgi_left[np.logical_not(np.isnan(lgi_left))]
    lgi_right = lgi_right[np.logical_not(np.isnan(lgi_right))]

    mean_l = np.mean(lgi_left[lgi_left < THRES_OUTLIERS])
    median_l = np.median(lgi_left)
    p5_l = np.percentile(lgi_left, 5)
    p25_l = np.percentile(lgi_left, 25)
    p75_l = np.percentile(lgi_left, 75)
    p95_l = np.percentile(lgi_left, 95)
    IQR_l = p75_l - p25_l

    mean_r = np.mean(lgi_right[lgi_right < THRES_OUTLIERS])
    median_r = np.median(lgi_right)
    p5_r = np.percentile(lgi_right, 5)
    p25_r = np.percentile(lgi_right, 25)
    p75_r = np.percentile(lgi_right, 75)
    p95_r = np.percentile(lgi_right, 95)
    IQR_r = p75_r - p25_r

    row = [
        pat_id, condition,
        mean_l, mean_r,
        median_l, median_r,
        p5_l, p5_r,
        p25_l, p25_r,
        p75_l, p75_r,
        p95_l, p95_r,
        IQR_l, IQR_r,
    ]

    print('\033[92m')
    print(COLUMNS)
    print(row)
    print('\033[0m')

    # Write the new row
    if not os.path.exists(CSV_RESULTS):
        print('Create %s' % CSV_RESULTS)
        with open(CSV_RESULTS, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            writer.writerow(row)
    else:
        with open(CSV_RESULTS, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    # Reorder the rows in ID alphabetical order
    data = load_csv_results()
    df = data.sort_values(by=['Patient ID'], ignore_index=True)
    df.to_csv(CSV_RESULTS, index=False)


def load_lgi(lgi_txt):
    with open(lgi_txt, 'r') as f:
        vals = f.readlines()
    lgi = [float(v.replace('\n', '')) for v in vals]
    lgi_np = np.array(lgi)
    lgi_np[lgi_np == np.inf] = np.nan
    return lgi_np


def main(condition):
    for folder_path in CASES[condition]:
        pat_id = os.path.split(folder_path)[1]

        # Skip if the row for the patient ID already exists
        if was_lgi_already_evaluated(pat_id):
            print('\nSkip %s' % pat_id)
            continue

        print('')
        print('\033[93mCase %s\033[0m' % pat_id)
        print('Folder %s' % folder_path)

        # Convert the segmentation to cgm and wm VTK 4.2 files
        seg = os.path.join(folder_path, 'parcellation.nii.gz')
        save_folder = os.path.join(SAVE_FOLDER, pat_id)
        # if os.path.exists(save_folder):
        #     os.system('rm -r %s' % save_folder)
        if not os.path.exists(save_folder):
            # I use Python 3.6 to make sure I use vtk version 8.1.2
            cmd = 'python3.6 %s/nii2vtk.py --seg %s --save %s' % (REPO_PATH, seg, save_folder)
            os.system(cmd)

        # Compute the LGI values for right and left hemispheres
        lgi_dict = {}
        for side in ['left', 'right']:
            print('\033[92m%s hemisphere\033[0m' % side)

            # Try to find the LGI file
            lgi_txt = None
            candidates = [
                f for f in os.listdir(save_folder)
                if 'cgm_%s' % side in f and f.endswith('.txt')
            ]
            assert len(candidates) < 2, 'Too many lGI map files found in %s' % save_folder
            if len(candidates) == 1:
                lgi_txt = os.path.join(save_folder, candidates[0])

            # Compute the LGI mapping if it does not exists
            if lgi_txt is None:
                # If the LGI file does not exist already,
                # compute it using the method of Lyu et al.
                cmd_base = 'docker run -v %s:/INPUT/ --rm ilwoolyu/cmorph:1.7 lgi' % save_folder
                cmd_paths = '-i /INPUT/cgm_%s.vtk --white /INPUT/wm_%s.vtk --out /INPUT/' % (side, side)
                cmd_options = '--kernel %d' % KERNEL_VALUE
                cmd = '%s %s %s' % (cmd_base, cmd_paths, cmd_options)
                os.system(cmd)

                # Find the LGI txt file
                for f in os.listdir(save_folder):
                    if 'cgm_%s' % side in f and f.endswith('.txt'):
                        lgi_txt = os.path.join(save_folder, f)
            else:
                print('Reuse existing LGI map')
                print(lgi_txt)

            # Load the LGI file
            lgi_dict[side] = load_lgi(lgi_txt)

        # Add values to the csv
        update_csv(pat_id, condition, lgi_dict['left'], lgi_dict['right'])


if __name__ == '__main__':
    if not os.path.exists(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)
    # main('Test')
    main('Control')
    main('CDH')
