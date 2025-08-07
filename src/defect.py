#!/usr/bin/python3.8
# coding: utf-8

import math
import os
import sys
import numpy as np
import warnings
import utils
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd

try:
    import gdspy
except ImportError:
    print("Unable to import GDSpy. Virtual environment might not be working.")

# IMP: All distances are in (GDS) "precision" units

# ----------------------------- #
# Read the configuration file and get all user inputs

CONFIG_FILE = 'config.ini'
(tools_env, mask_data, defect_info, set_compute, set_pds
 ) = utils.unpack_config_dicts(CONFIG_FILE)

mask_gds_file = "mask.gds"
layer_id = mask_data["layer_id"]
pos_tone = mask_data["pos_tone"]

[defect_center_x, defect_center_y] = defect_info["location"]
seed_pct_layer = defect_info["seed"]
if seed_pct_layer > 100:
    print(f"Seed level can not exceed the resist ({seed_pct_layer}>100%). It's reset to 100%")
defect_layer = utils.convert_pct_to_real_layer(seed_pct_layer)  # conv percentage to real value
[defect_x, defect_y, defect_thickness] = defect_info["size"]

[delta_x, delta_y, delta_z] = set_compute["fdtd_grid_size"]
diffusion_coefficient = set_compute["thermal_diffusivity"]
# Iteration number is proportional to this
max_time = set_compute["max_time"]

max_x, max_y = mask_data["max_x"], mask_data["max_y"]

# ----------------------------- #

# Hard-coded model parameters
Qz_thickness = 20
Airtop_thickness = 220

# Check if nx and ny are even numbers (REQUIRE odd numbers).
# This block is different from Li's original script
Nx = math.ceil(max_x / delta_x)
if Nx % 2 == 0:  # even
    max_x = (1+Nx) * delta_x  # Add a delta_x
Ny = math.ceil(max_y / delta_y)
if Ny % 2 == 0:  # even
    max_y = (1+Ny) * delta_y  # Add a delta_y

# Output MTVDAT file name starting with
OutputDATfile_prefix = 'Binary_mask_2u'

# Will be made user inputs in later versions
defect_material = "Si_1"  # assume defect material is silicon
MLpair = 40  # Mask Stack Parameters

# Providing absolute path for these files
abs_path_src_dir = os.path.abspath(os.path.dirname(__file__))
# input mask stack file
mask_input_filename = os.path.join(abs_path_src_dir, 'mask_input_binary.dat')
# intermittent output file
mask_stack_filename = os.path.join(abs_path_src_dir, 'mask_stack_binary.csv')
# intermittent output file
mask_material_filename = os.path.join(abs_path_src_dir, 'mask_stack_material_binary.csv')


# ================ Start Li's Original Code ================ #


def input_mask_conversion(mask_input_filename, mask_stack_filename, mask_material_filename):
    # Convert input to output mask files
    df_mask_input = pd.read_csv(mask_input_filename, sep='\t', lineterminator='\n')
    # change Qz thickness to default thickness
    df_mask_input.loc[df_mask_input.Material == 'Qz', 'Thickness(nm)'] = Qz_thickness
    df_mask_input['Thickness(nm)'] = pd.to_numeric(df_mask_input['Thickness(nm)'], downcast="float")
    df_mask_input['Thickness(nm)'] = df_mask_input['Thickness(nm)'] * 0.001  # convert to um
    print(f'Input mask table: \n {df_mask_input}')

    # Get material from bottom layer to top layer
    material_stack = []
    if 'Substrate' in df_mask_input['Type'].values:
        material_substrate = df_mask_input[df_mask_input['Type'] == 'Substrate'].Material.tolist()
        material_substrate.reverse()
        material_stack.extend(material_substrate)
    if 'ML' in df_mask_input['Type'].values:
        material_ML = df_mask_input[df_mask_input['Type'] == 'ML'].Material.tolist()
        material_ML.reverse()
        material_ML_pairs = material_ML * MLpair  # repeat MLpair times
        material_stack.extend(material_ML_pairs)
    if 'Capping' in df_mask_input['Type'].values:
        material_Capping = df_mask_input[df_mask_input['Type'] == 'Capping'].Material.tolist()
        material_Capping.reverse()
        material_stack.extend(material_Capping)
    if 'Absorber' in df_mask_input['Type'].values:
        material_Absorber = df_mask_input[df_mask_input['Type'] == 'Absorber'].Material.tolist()
        material_Absorber.reverse()
        material_stack.extend(material_Absorber)
    # print("material_substrate, material_ML, material_Capping, material_Absorber",material_substrate, material_ML, material_Capping, material_Absorber)
    # return

    # Get material thickness from bottom layer to top layer
    thickness_stack = []
    if 'Substrate' in df_mask_input['Type'].values:
        thickness_substrate = df_mask_input[df_mask_input['Type'] == 'Substrate']['Thickness(nm)'].tolist()
        thickness_substrate.reverse()
        thickness_stack.extend(thickness_substrate)
    if 'ML' in df_mask_input['Type'].values:
        thickness_ML = df_mask_input[df_mask_input['Type'] == 'ML']['Thickness(nm)'].tolist()
        thickness_ML.reverse()
        thickness_ML_pairs = thickness_ML * MLpair  # repeat MLpair times
        thickness_stack.extend(thickness_ML_pairs)
    if 'Capping' in df_mask_input['Type'].values:
        thickness_Capping = df_mask_input[df_mask_input['Type'] == 'Capping']['Thickness(nm)'].tolist()
        thickness_Capping.reverse()
        thickness_stack.extend(thickness_Capping)
    if 'Absorber' in df_mask_input['Type'].values:
        thickness_Absorber = df_mask_input[df_mask_input['Type'] == 'Absorber']['Thickness(nm)'].tolist()
        thickness_Absorber.reverse()
        thickness_stack.extend(thickness_Absorber)
    thickness_stack = ['{:.6f}'.format(t) for t in thickness_stack]
    # print(thickness_stack)

    # Create layer number
    stack_layer_list = list(range(1, len(material_stack) + 1))
    # print(stack_layer_list)

    mask_stack = pd.DataFrame(list(zip(stack_layer_list, material_stack, thickness_stack)),
                              columns=['layer number', 'material', 'thickness'])
    # add Air top to the stack
    mask_stack.loc[len(mask_stack.index)] = [len(mask_stack.index) + 1, 'air', Airtop_thickness * 0.001]
    # adjust air top thickness by delta_z
    total_thickness = mask_stack['thickness'].astype(float).sum()
    if math.ceil(total_thickness / (delta_z * 0.001)) % 2 == 0:  # even
        total_thickness_rounded = (delta_z * 0.001) * (math.ceil(total_thickness / (delta_z * 0.001)) - 1)
    else:
        total_thickness_rounded = (delta_z * 0.001) * math.ceil(total_thickness / (delta_z * 0.001))
    adjusted_airtop_thickness = Airtop_thickness * 0.001 + (total_thickness_rounded - total_thickness)
    mask_stack.loc[mask_stack.material == 'air', 'thickness'] = format(adjusted_airtop_thickness, '.8f')

    # print(mask_stack)
    mask_stack.to_csv(mask_stack_filename, sep='\t', index=False)
    # ======================================================================
    # Write the material_no file
    #
    # Get n and K from bottom layer to top layer
    if 'Substrate' in df_mask_input['Type'].values:
        n_substrate = df_mask_input[df_mask_input['Type'] == 'Substrate']['n'].tolist()
        n_substrate.reverse()
    if 'ML' in df_mask_input['Type'].values:
        n_ML = df_mask_input[df_mask_input['Type'] == 'ML']['n'].tolist()
        n_ML.reverse()
    if 'Capping' in df_mask_input['Type'].values:
        n_Capping = df_mask_input[df_mask_input['Type'] == 'Capping']['n'].tolist()
        n_Capping.reverse()
    if 'Absorber' in df_mask_input['Type'].values:
        n_Absorber = df_mask_input[df_mask_input['Type'] == 'Absorber']['n'].tolist()
        n_Absorber.reverse()

    if 'Substrate' in df_mask_input['Type'].values:
        k_substrate = df_mask_input[df_mask_input['Type'] == 'Substrate']['k'].tolist()
        k_substrate.reverse()
    if 'ML' in df_mask_input['Type'].values:
        k_ML = df_mask_input[df_mask_input['Type'] == 'ML']['k'].tolist()
        k_ML.reverse()
    if 'Capping' in df_mask_input['Type'].values:
        k_Capping = df_mask_input[df_mask_input['Type'] == 'Capping']['k'].tolist()
        k_Capping.reverse()
    if 'Absorber' in df_mask_input['Type'].values:
        k_Absorber = df_mask_input[df_mask_input['Type'] == 'Absorber']['k'].tolist()
        k_Absorber.reverse()

    # construct the material_no_file
    material_no_stack = ['air', 'air']
    material_no_stack.extend(material_Absorber)
    material_no_stack.extend(material_substrate)
    material_no_stack.extend(material_ML)
    material_no_stack.extend(material_Capping)

    # print("material_no_stack",material_no_stack)

    material_n_list = [1, 1]
    material_n_list.extend(n_Absorber)
    material_n_list.extend(n_substrate)
    material_n_list.extend(n_ML)
    material_n_list.extend(n_Capping)

    # print("material_n_list",material_n_list)

    material_k_list = [0, 0]
    material_k_list.extend(k_Absorber)
    material_k_list.extend(k_substrate)
    material_k_list.extend(k_ML)
    material_k_list.extend(k_Capping)
    # print("material_k_list",material_k_list)

    # Add defect if it exists
    if defect_x > 0 and defect_y > 0 and defect_thickness > 0:
        material_no_stack.append('defect')
        material_n_list.append(material_n_list[material_no_stack.index(defect_material)])
        material_k_list.append(material_k_list[material_no_stack.index(defect_material)])

    material_type_list = ['material'] * (len(material_no_stack))
    material_type_list[0] = "ambient"
    material_no_list = list(range(len(material_no_stack) - 1))
    material_no_list.insert(0, 0)
    material_zero_list = [0] * len(material_no_stack)
    material_homo_list = ['homogeneous'] * len(material_no_stack)
    material_NA_list = ['NA'] * len(material_no_stack)
    material_linear_list = ['linear'] * len(material_no_stack)

    mask_material_df = pd.DataFrame(
        list(zip(material_type_list, material_no_list, material_no_stack, material_n_list, material_k_list, \
                 material_zero_list, material_homo_list, material_NA_list, material_NA_list, material_linear_list, \
                 material_zero_list, material_zero_list, material_zero_list)),
        columns=['type', 'material_no', 'material', 'n', 'k', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10', 'col11',
                 'col12'])
    # print("mask_material_df",mask_material_df)
    mask_material_df.to_csv(mask_material_filename, sep='\t', index=False)
    return material_Absorber


# shift an image cell
def image_shift_roll(img, x_roll, y_roll):
    img_roll = img.copy()
    img_roll = np.roll(img_roll, -y_roll, axis=0)  # Positive y rolls up
    img_roll = np.roll(img_roll, x_roll, axis=1)  # Positive x rolls right
    return img_roll


# # Perform FDTD 2D Heat Simulation using image shift roll
def calculate2D(u):
    for k in range(0, max_iterations - 1, 1):
        u[k + 1] = gamma * (image_shift_roll(u[k], 1, 0) + image_shift_roll(u[k], -1, 0) + image_shift_roll(u[k], 0, 1)
                            + image_shift_roll(u[k], 0, -1) - 4 * u[k]) + u[k]
        # set initial condition. Heat sink on all edges for all k.
        u[:, :, 0] = 0
        u[:, 0, :] = 0
        u[:, int(max_x / delta_x) - 1, 0] = 0
        u[:, :, int(max_y / delta_y) - 1] = 0
    return u


# # Change Time Stepping to Match Material Thickness Transitions
def changeDataRes(df, series):
    # function converts the time steps coming from the heat simulation and interpolates data for other time values. Will
    # delete all the data not part of the series.
    # first, generate new data using linear approximation
    df_tmp = pd.DataFrame()
    for index1, value in series.items():
        # if value already exists, then skip
        # value = round(value, 1)
        if value in df['time'].unique():
            # continue #do not worry about this now. It will be appended later.
            df_temp3 = df[df['time'] == value].copy()
            df_tmp = df_tmp.append(df_temp3)
        else:
            # identify which time to take for the interpolation...
            difference_array = np.absolute(df['time'].unique() - value)
            index = difference_array.argmin()
            if df['time'].unique()[index] > value:
                start = df['time'].unique()[index - 1]
                stop = df['time'].unique()[index]
            else:
                start = df['time'].unique()[index]
                try:
                    stop = df['time'].unique()[index + 1]
                except:
                    print('Error due to insufficient amount of data to interpolate. Extend time of simulation..')
                    return
            #         print (f' For value {value}, start is {start} and stop is {stop}')
            df_temp1 = df[(df['time'] == start) | (df['time'] == stop)]
            df_temp2 = df_temp1.pivot_table(index=['x', 'y'], columns='time', values='data', aggfunc=np.mean)
            df_temp2[value] = df_temp2.iloc[:, 0] + 1 / (df_temp2.columns[1] - df_temp2.columns[0]) * (
                        df_temp2.iloc[:, 1] - df_temp2.iloc[:, 0])
            df_temp2.reset_index(inplace=True)
            df_temp3 = pd.melt(df_temp2, id_vars=['x', 'y'],
                               value_vars=[df_temp2.columns[2], value, df_temp2.columns[3]], var_name='time',
                               value_name='data')
            df_temp3 = df_temp3[df_temp3['time'] == value]
            df_tmp = df_tmp.append(df_temp3)

    # take all the data from df as well
    #     df_tmp = df_tmp.append(df)
    df_tmp = df_tmp.apply(pd.to_numeric)

    df_tmp.sort_values(by=['time', 'x', 'y'], inplace=True)
    df_tmp.reset_index(drop=True, inplace=True)

    # second, delete data points that are not required and are not part of data series
    for value in df_tmp.time.unique():
        if abs(series - value).min() < 0.01:
            continue
        else:
            df_tmp = df_tmp[df_tmp['time'] != value]
    df_tmp.sort_values(by=['time', 'x', 'y'], inplace=True)
    df_tmp.reset_index(drop=True, inplace=True)
    return df_tmp


# Detect and correct if there is overlap between neighboring lines
def detectOverwriteOverlap(df_input):
    # assign output df to be time=0 of input df
    df_output = df_input[df_input['time'] == df_input.time.unique()[0]].copy()
    df_output.reset_index(drop=True, inplace=True)
    counter_line = 1
    counter_overlap = 0
    while counter_line <= len(df_input.time.unique()) - 2:
        df_prevline = df_output[df_output['time'] == df_input.time.unique()[counter_line - 1]].copy()
        df_curline = df_input[df_input['time'] == df_input.time.unique()[counter_line]].copy()
        df_nextline = df_input[df_input['time'] == df_input.time.unique()[counter_line + 1]].copy()

        df_prevline['data'] = df_prevline['data'] + df_prevline['time']  # increase data height by time.
        df_curline['data'] = df_curline['data'] + df_curline['time']  # increase data height by time.
        df_prevline.reset_index(drop=True, inplace=True)
        df_curline.reset_index(drop=True, inplace=True)
        df_nextline.reset_index(drop=True, inplace=True)

        df_check_overlap = df_curline['data'].subtract(df_prevline['data'], fill_value=0)
        df_prevline['data'] = df_prevline['data'] - df_prevline['time']  # decrease data height by time.
        df_curline['data'] = df_curline['data'] - df_curline['time']  # decreaes data height by time.
        if df_check_overlap.min() < 0:
            counter_overlap += 1
            print(f'Overlap exists at time = {df_input.time.unique()[counter_line]}')
            if counter_line == 1:
                df_prevline['data_line1'] = df_curline['data']
                df_prevline['data_min'] = df_prevline[['data', 'data_line1']].min(axis=1)
                df_prevline.drop(columns=['data', 'data_line1'], inplace=True)
                df_prevline.rename(columns={'data_min': 'data'}, inplace=True)
                df_output = df_prevline.copy()
                df_output.reset_index(drop=True, inplace=True)
            else:
                df_curline['data'] = (df_prevline['data'] + df_nextline['data']) / 2
                df_output = df_output.append(df_curline, ignore_index=True)
        else:
            df_output = df_output.append(df_curline, ignore_index=True)
        counter_line += 1
        if counter_overlap / len(df_input.time.unique()) > 0.25:
            sys.exit(
                f'Identified {(counter_overlap / len(df_input.time.unique())) * 100:.1f}% overlaps. Too many overlaps. Diffusion Coefficient too high. Reduce and try again...')
    df_output = df_output.append(df_nextline, ignore_index=True)
    df_output.sort_values(by=['time', 'x', 'y'], inplace=True)
    df_output.reset_index(drop=True, inplace=True)
    return df_output


if __name__ == '__main__':
    print(
        f'Simulation conditions: \n X domain: {max_x}nm, resolution={delta_x}nm; Y domain: {max_y}nm, resoulution={delta_y}nm; Z resolution={delta_z}nm')
    print(f' Defect size: X={defect_x}nm, Y={defect_y}nm, Z={defect_thickness}nm')
    print(f' Defect at X={defect_center_x}nm, Y={defect_center_y}nm, at bottom layer {defect_layer}')
    print(f' GDS mask file: {mask_gds_file}, layer {layer_id}')

    # Read mask_input.dat and generate mask stack intermittent files
    absorber_layers = input_mask_conversion(mask_input_filename, mask_stack_filename, mask_material_filename)

    # Read in mask stack
    df_material = pd.read_csv(mask_stack_filename, sep='\t')
    df_material['thickness'] = df_material['thickness'] * 1000  # convert from micron to nm
    total_thickness_mask = df_material['thickness'].sum()  # total thickness of the mask
    print(f'Total thickness of the mask: {total_thickness_mask} nm')
    # print(df_material)
    # Remove the air layer
    df_material.drop(df_material[df_material['material'] == 'air'].index, inplace=True)

    # adding defect to the material dataframe
    if ((defect_x != 0) and (defect_y != 0) and (defect_thickness != 0)):
        df_temp1 = df_material.iloc[0:defect_layer].copy()
        df_temp1 = df_temp1.append({'layer number': defect_layer + 0.1, 'material': 'defect', 'thickness': 0},
                                   ignore_index=True)
        df_temp2 = df_material.iloc[defect_layer:].copy()
        df_material = df_temp1.append(df_temp2, ignore_index=True)
    else:
        pass

    # adding total_thickness column and computing for all layers above the defect.
    signal = 0
    df_material['total_thickness'] = np.nan
    for index, row in df_material.iterrows():
        if (signal == 0) & ((defect_x == 0) | (defect_y == 0) | (defect_thickness == 0)):
            signal = 1
            df_material.loc[index, 'total_thickness'] = 0
            continue
        elif row['material'] == 'defect':
            signal = 1
            df_material.loc[index, 'total_thickness'] = 0
            continue
        elif signal == 1:
            df_material.loc[index, 'total_thickness'] = row['thickness'] + df_material.loc[index - 1, 'total_thickness']
        else:
            pass

    # computing the total_thickness for layers under the defect...
    for value in reversed(df_material.index):
        if pd.isnull(df_material.total_thickness.iloc[value]):
            df_material.loc[value, 'total_thickness'] = df_material.loc[value + 1, 'total_thickness'] - df_material.loc[
                value, 'thickness']
    print(f'(1) Reading mask stack complete.')
    # print("df_material",df_material)
    # df_material.to_csv('df_material.csv',index=False)

    # # Set Heat Equation Variables
    factor = max_time / int(round(df_material['total_thickness'].max() * 1.25, 0))
    # To achieve a stable equation, need to set the following conditions
    delta_t = (delta_x * delta_y) / (4 * diffusion_coefficient)
    max_iterations = int(max_time / delta_t)  # number of iterations
    gamma = (diffusion_coefficient * delta_t) / (delta_x * delta_y)
    defect_temperature = defect_thickness * factor
    # print(f'max_iterations = {max_iterations}')
    # print(f'defect_thickness = {defect_thickness}, factor = {factor}, defect_temperature = {defect_temperature}')

    # # Set Initial Condition
    # Initialize u
    u = np.empty((max_iterations, int(max_x / delta_x), int(max_y / delta_y)))
    u.fill(0)

    u_initial = np.zeros((max_iterations, int(max_x / delta_x), int(max_y / delta_y)))

    for x in range(int(max_x / delta_x)):
        for y in range(int(max_y / delta_y)):
            if (((x * delta_x) >= (defect_center_x - defect_x / 2)) & (
                    (y * delta_y) >= (defect_center_y - defect_y / 2)) & \
                    ((x * delta_x) <= (defect_center_x + defect_x / 2)) & (
                            (y * delta_y) <= (defect_center_y + defect_y / 2))):
                u_initial[0, x, y] = defect_temperature
    u[:, :, :] = u_initial

    # Do the calculation here
    u = calculate2D(u)
    print(f'(2) Heat equation calculation complete: max_iterations = {max_iterations}')

    # # Convert Heat Numpy 3D Array into Pandas Dataframe
    names = ['time', 'x', 'y']
    index = pd.MultiIndex.from_product([range(s) for s in u.shape], names=names)
    df = pd.DataFrame({'data': u.flatten()}, index=index)['data']
    df = df.reset_index()
    df['time'] = df['time'] * delta_t / factor
    df['data'] = df['data'] / factor
    df['x'] = df['x'] * delta_x
    df['y'] = df['y'] * delta_y
    # print(f'Convert Heat Numpy 3D Array into Pandas Dataframe:\n {df}')

    # drop the first 2 data points and then adjust the time axis by resetting it to 0.
    df = df[(df['time'] != df.time.unique()[0]) & (
                df['time'] != df.time.unique()[1])].copy()  # eliminate the first two points
    df['time'] = df['time'] - df['time'].min()  # set the time back to 0.
    df.reset_index(drop=True, inplace=True)
    # print(df)

    # interpolate data to line up with the various thickness of the material info.
    df_changeDataRes = changeDataRes(df, df_material[df_material['total_thickness'] >= 0]['total_thickness'])
    # print(df_changeDataRes)
    # print(df_changeDataRes.time.unique())

    # # Convert from Heat to Thickness
    df2 = df_changeDataRes.copy()
    # print(df2)

    print(f'(3) 2D heat data generation complete.')

    # Detect if there is any overlap
    df3 = detectOverwriteOverlap(df2)
    # print(f'After detecting overlap, it becomes: \n {df3}')

    print(f'(4) Detecting overlap complete.')

    # Finally, scale the data with time. Effectively changing the time column to thickness!
    df3['data'] = df3['data'] + df3['time']  # scales with time
    # print(f'After scaling over time, it becomes: \n {df3}')
    # print(df3.time.unique()[0])
    df4 = df3

    print(f'(5) Scaling data with time complete.')

    # # Join Material Info to Heat-->Thickness Data
    # join data
    df4.rename(columns={'time': 'total_thickness'}, inplace=True)

    df4['total_thickness'].astype('float64')
    df_material['total_thickness'].astype('float64')

    df4['total_thickness'] = df4['total_thickness'].round(1)
    df_material['total_thickness'] = df_material['total_thickness'].round(1)

    df_combined = df4.merge(df_material, on='total_thickness')
    df_combined.sort_values(by=['layer number', 'x', 'y'], inplace=True)
    df_combined.reset_index(drop=True, inplace=True)
    # print(f'Joining material info with thickness data: \n {df_combined}')

    # add defect which is thickness time = 0 back in
    # add other layers which are under the defect
    # scale the data value accordingly
    # push all layers/material up to re-zero
    df_combined['data'] = df_combined['data'] + abs(df_material.total_thickness.iloc[0])

    df_layers = df_combined.drop(columns=['total_thickness'])
    # print(f'df_layers: \n {df_layers}')

    # in the situation that the defect is sized 0, we need to add the very first layer and increase its thickness.
    if (defect_x == 0) or (defect_y == 0) or (defect_thickness == 0):
        df_layers['data'] = df_layers['data'] + df_layers.thickness[0]
    else:
        pass

    # # Adjust thickness for layers under the defect
    # identify layers that are negative (under the defect). Adjust total_thickness to positive values.
    df_material_underlayers = df_material[df_material['total_thickness'] < 0].copy()
    df_material_underlayers['total_thickness'] = df_material_underlayers['total_thickness'] + abs(
        df_material.total_thickness.iloc[0]) + df_material_underlayers['thickness']
    df_material_underlayers.reset_index(drop=True, inplace=True)
    # print(f'df_material_underlayers: \n {df_material_underlayers}')

    print(f'(6) Adding defect to the stack complete.')

    # Create a loop and concatenate the underlayers to the combined dataset
    for index, row in df_material_underlayers.iterrows():
        df_test1 = pd.DataFrame()
        df_test2 = pd.DataFrame()
        df_test1['x'] = pd.Series(range(0, max_x, delta_x))
        df_test1['data'] = row['total_thickness']
        df_test1['layer number'] = row['layer number']
        df_test1['material'] = row['material']
        df_test1['thickness'] = row['thickness']
        df_test1['tmp'] = 1
        df_test2['y'] = pd.Series(range(0, max_y, delta_y))
        df_test2['tmp'] = 1
        # df_test1 = df_test1.merge(df_test2, how='cross')
        df_test1 = df_test1.merge(df_test2, on=['tmp'])
        df_test1 = df_test1.drop('tmp', axis=1)
        df_layers = df_layers.append(df_test1, ignore_index=True)
    df_layers.sort_values(by=['layer number', 'x', 'y'], inplace=True)
    df_layers.reset_index(drop=True, inplace=True)
    # print(f'df_layers: \n {df_layers}')

    print(f'(7) Adding underlayers complete.')

    # check to ensure that total thickness is odd multiples of delta_z. Remove rounding error..
    total_thickness_mask = total_thickness_mask - delta_z * (
                total_thickness_mask / delta_z - math.floor(total_thickness_mask / delta_z))
    if math.floor(total_thickness_mask / delta_z) % 2 == 0:
        total_thickness_mask = total_thickness_mask + delta_z

    # add air to the top to cap the last material with defect.
    df_test1 = pd.DataFrame()
    df_test2 = pd.DataFrame()
    df_test1['x'] = pd.Series(range(0, max_x, delta_x))

    # set air to fill the rest of the total thickness
    current_total_thickness = df_layers['data'].max() + delta_z * 10
    if current_total_thickness < total_thickness_mask:
        df_test1['data'] = total_thickness_mask
    else:
        df_test1['data'] = df_layers['data'].max() + delta_z * 10
    df_test1['layer number'] = df_layers['layer number'].max() + 0.1
    df_test1['material'] = 'air'
    df_test1['thickness'] = total_thickness_mask - current_total_thickness
    df_test1['tmp'] = 1
    df_test2['y'] = pd.Series(range(0, max_y, delta_y))
    df_test2['tmp'] = 1
    # df_test1 = df_test1.merge(df_test2, how='cross')
    df_test1 = df_test1.merge(df_test2, on=['tmp'])
    df_test1 = df_test1.drop('tmp', axis=1)
    df_layers = df_layers.append(df_test1, ignore_index=True)
    df_layers.sort_values(by=['layer number', 'x', 'y'], inplace=True)
    df_layers.reset_index(drop=True, inplace=True)
    # print(f'df_layers: \n {df_layers}')

    print(f'(8) Adding air layer on top complete.')

    df_slice = df_layers[(df_layers['x'] == 0) & (df_layers['y'] == 0)]
    # print(f'Taking the x=0, y=0 slice, df_slice: {df_slice}')

    # create a data frame where data axis is at delta_z resolution.
    df_test1, df_test2, df_test3 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    df_test1['x'] = pd.Series(range(0, max_x, delta_x))
    df_test2['y'] = pd.Series(range(0, max_y, delta_y))
    df_test3['data'] = pd.Series(np.arange(0, df_layers.data.max() + delta_z, delta_z))
    # df_test1 = df_test1.merge(df_test2, how='cross')
    df_test1['tmp'] = 1
    df_test2['tmp'] = 1
    df_test1 = df_test1.merge(df_test2, on=['tmp'])
    # df_test3 = df_test1.merge(df_test3, how='cross')
    df_test3['tmp'] = 1
    df_test3 = df_test1.merge(df_test3, on=['tmp'])
    df_test3 = df_test3.drop('tmp', axis=1)
    # print(f'df_test3: {df_test3}')

    # Drop items that are overlapping each other
    df_layers.sort_values(by=['x', 'y', 'layer number', 'data'], inplace=True)
    df_layers2 = df_layers.drop_duplicates(subset=['x', 'y', 'data'])

    print(f'(9) Converting dataframe to delta_z resolution complete.')

    # Merging the thickness with material layers
    df_test4 = df_test3.sort_values(by='data')
    df_layers2 = df_layers2.sort_values(by='data')
    df_total = pd.merge_asof(df_test4, df_layers2, left_by=['x', 'y'], right_by=['x', 'y'], on='data',
                             direction='forward')

    print(f'(10) Merging thickness with material complete.')

    # Read in GDS file
    gdsii = gdspy.GdsLibrary(infile=mask_gds_file)
    # print(gdsii.cells)
    cellNames = list(gdsii.cells.keys())
    print(f'cellNames are: {cellNames}')
    coup_cell = gdsii.cells[cellNames[-1]]
    # search for layer id
    for (ip, poly) in enumerate(coup_cell.polygons):
        if poly.layers[0] == layer_id[0] and poly.datatypes[0] == layer_id[1]:
            layerid = ip
    print(f'(11) Reading GDS mask polygon complete.')

    # Apply GDS pattern to the absorber layers
    # generate a DataFrame with x and y coordinates
    df_xy = df_total[['x', 'y']].sort_values(by=['x', 'y']).drop_duplicates().reset_index(drop=True)
    df_xy['inside_polygon'] = False  # default

    # loop through multiple polygons and identify whether the x,y coordinates are inside or outside the polygon
    for (ip, poly) in enumerate(coup_cell.polygons):
        if poly.layers[0] == layer_id[0] and poly.datatypes[0] == layer_id[1]:
            layerid = ip
            for i in range(len(coup_cell.polygons[layerid].polygons)):
                points = coup_cell.polygons[layerid].polygons[i]
                # increase by x4
                # mask_points = [p * 4 * 1000 for p in points]
                #     for p in mask_points:
                #         print("Points: {}".format(p))
                mask_points = [p * 1000 for p in points]

                for index, row in df_xy.iterrows():
                    # if it is already true, do not check again.
                    if row['inside_polygon'] == True:
                        pass
                    else:
                        # df_xy.loc[index, 'inside_polygon'] = Point(row['x'], row['y']).intersects(Polygon(mask_points).buffer(1e-8))
                        df_xy.loc[index, 'inside_polygon'] = Polygon(mask_points).buffer(1E-9).contains(
                            Point(row['x'], row['y']))

    # slice the DataFrame containing absorber_layers and then merge it with the df_yx DataFrame
    df_total_toplayers = df_total[df_total['material'].isin(absorber_layers)].merge(df_xy, on=['x', 'y'], how='left')
    # replace the material to air if it's inside polygon
    df_total_toplayers.loc[df_total_toplayers.inside_polygon == pos_tone, 'material'] = 'air'
    df_total_toplayers.drop(columns=['inside_polygon'], inplace=True)
    df_total_new = df_total[~df_total['material'].isin(absorber_layers)].append(df_total_toplayers)

    df_total = df_total_new.copy()
    print(f'(12) Applying mask to the absorber layer complete.')

    # Assign material no
    df_total.sort_values(by=['data', 'y', 'x'], inplace=True)
    df_total.reset_index(drop=True)
    # print(f'df_total: \n {df_total}')
    # print('Checking material of df_total:')
    # print(df_total['material'].unique())

    df_material_no = pd.read_csv(mask_material_filename, sep='\t', keep_default_na=False)
    # print(f'Assigning material no: \n {df_material_no}')
    # remove duplicated "material" rows
    df_material_no.drop_duplicates(subset='material', keep="last", inplace=True)

    # join with material_no
    df_total['material_no'] = df_total['material'].map(df_material_no.set_index('material')['material_no'])

    # Take the material_no out as a series
    stack_series_orig = df_total['material_no'].squeeze()
    stack_series = stack_series_orig[::-1]  # reverse the sequence
    # print(f'Taking the material_no as a series (reversed): {stack_series}')

    print(f'(13) Adding material_no and convert to series complete.')

    # Save data to output
    filename = OutputDATfile_prefix + str(diffusion_coefficient) + '_' + str(max_x) + 'x' + str(max_y) + 'x' + str(
        total_thickness_mask) + \
               '_r' + str(max(delta_x, delta_y, delta_z)) + \
               '_d' + str(defect_x) + 'x' + str(defect_y) + 'x' + str(defect_thickness) + \
               '_l' + str(defect_layer) + 'at' + str(defect_center_x) + 'x' + str(defect_center_y) + '.mtvdat'
    if os.path.exists(filename):
        os.remove(filename)
    with open(mask_material_filename, 'r') as file_input, open(filename, "w") as file_output:
        file_output.writelines(['$DATA=GRID4D_PLUS\n', '% toplabel="Material grid"\n', '% contstyle=2\n',
                                '% xmin=' + str(df_total['x'].min() / 1000) + ' xmax=' + str(
                                    df_total['x'].max() / 1000) + ' nx=' + str(len(df_total['x'].unique())) + '\n',
                                '% ymin=' + str(df_total['y'].min() / 1000) + ' ymax=' + str(
                                    df_total['y'].max() / 1000) + ' ny=' + str(len(df_total['y'].unique())) + '\n',
                                '% zmin=' + str(df_total['data'].min() / 1000) + ' zmax=' + str(
                                    format(df_total['data'].max() / 1000, '.4f')) + ' nz=' + str(
                                    len(df_total['data'].unique()) - 1) + '\n', '# Data\n'])
        for i in stack_series:
            file_output.writelines(f'{int(i)}\n')
        file_output.writelines('\n# Material List\n')
        # write the material_no file
        next(file_input)  # skip the header row
        for row in file_input:
            row_string = row.split("\t")
            for index, value in enumerate(row_string):
                if index == 0:
                    line = value
                elif index == 2:
                    line = line + " \"" + value + "\""
                else:
                    line = line + " " + value
            # print(line)
            file_output.writelines(line)
            line = ""
        file_output.writelines('$END\n')

    print(f'(14) Writing output to MTVDAT file complete: {filename}')
    print('Everything complete. Success!')
