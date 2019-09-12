from opentrons import labware, instruments, robot
import math, sys

# creates custom labware if currently not created
tube_rack_35 = "tube_rack_35"
if tube_rack_35 not in labware.list():
    tube_rack_35 = labware.create("tube_rack_35",
                                  grid=(7, 5),
                                  spacing=(16.25, 14.56),
                                  diameter=10,
                                  depth=41)

ss_tubes_rack = labware.load('tube_rack_35', slot='1')
temp_falcons_rack = labware.load('tube-rack-15_50ml', slot='2')
cobas_tuberack = labware.load('24-vial-rack', slot='3')
validation_tuberack_A = labware.load('tube_rack_35', slot='4')
validation_tuberack_B = labware.load('tube_rack_35', slot='5')
validation_tuberack_C = labware.load('tube_rack_35', slot='6')
source_falcons_rack = labware.load('tube-rack-15_50ml', slot='7')
tip_rack_big_A = labware.load('tiprack-1000ul', slot='8')
tip_rack_big_B = labware.load('tiprack-1000ul', slot='9')
tip_rack_small_A = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack_small_B = labware.load('opentrons-tiprack-300ul', slot='11')

validation_tuberacks_array = [validation_tuberack_A, validation_tuberack_B, validation_tuberack_C]

single50 = instruments.P50_Single(mount='right',
                                  tip_racks=[tip_rack_small_A, tip_rack_small_B],
                                  aspirate_flow_rate=50,
                                  dispense_flow_rate=100)

single1000 = instruments.P1000_Single(mount='left',
                                      tip_racks=[tip_rack_big_A, tip_rack_big_B],
                                      aspirate_flow_rate=1000,
                                      dispense_flow_rate=1500)
# global variables
h2o_source_current_vol = 0


# method for preparing temporary dilutions
def dilutions_prep(dp_begin_vol, h2o_begin_vol, dp_spiked_begin_vol, dilB_begin_vol, dp_conc, dp_spiked_conc, dilB_conc,
                   ss1_vol, ss2_vol, ss3_vol, ss24_vol, ss3_conc, ss24_conc,
                   ss_tubes_vol):
    # ******** Stock Sample no. 1 preparation - 16 times diluted Donor Plasma with water ******* #
    dp_vol_for_ss1 = round(ss1_vol / 16)
    print("Donor Plasma volume that will be transferred for SS#1: ", dp_vol_for_ss1)
    h2o_vol_for_ss1 = ss1_vol - dp_vol_for_ss1
    print("Water volume that will be transferred for SS#1: ", h2o_vol_for_ss1)
    # Donor Plasma transferring
    dp_source_current_vol = dp_begin_vol
    dp_source_current_vol = liquid_transfer(dp_vol_for_ss1, dp_source_current_vol,
                                            source_falcons_rack('A3'),
                                            temp_falcons_rack('A1').top(-30))

    # Water transferring
    global h2o_source_current_vol
    h2o_source_current_vol = h2o_begin_vol
    h2o_source_current_vol = liquid_transfer(h2o_vol_for_ss1, h2o_source_current_vol,
                                             source_falcons_rack('B1'),
                                             temp_falcons_rack('A1').top(-30))
    print('Stock Sample no. 1 in temporary falcon prepared.\n')

    # ******* Stock Sample no. 2 preparation - raw Donor Plasma ******* #
    dp_source_current_vol = liquid_transfer(ss2_vol, dp_source_current_vol, source_falcons_rack('A3'),
                                            temp_falcons_rack('B1').top(-30))
    print('\n', ss2_vol, '[ul] of Raw Donor Plasma was transferred. '
                         'Stock Sample no. 2 in temporary falcon prepared.')

    # ******* Stock Sample no. 3 preparation - Donor Plasma + Donor Plasma spiked OR Donor Plasma + water ******* #
    if dp_conc >= ss3_conc:
        print('\nDonor Plasma concentration is greater than desired '
              'concentration of dilution in Stock Sample no. 3. '
              'Raw Donor Plasma will be diluted with water.')
        dp_vol_for_ss3 = round((ss3_conc / dp_conc) * ss3_vol)
        print('Calculated volume of Donor Plasma for Stock Sample no. 3 is: ', dp_vol_for_ss3)
        h2o_vol_for_ss3 = ss3_vol - dp_vol_for_ss3
        print('Calculated volume of water for Stock Sample no. 3 is: ', h2o_vol_for_ss3)
        dp_source_current_vol = liquid_transfer(dp_vol_for_ss3, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                temp_falcons_rack('C1').top(-30))
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        h2o_source_current_vol = liquid_transfer(h2o_vol_for_ss3, h2o_source_current_vol,
                                                 source_falcons_rack('A1'),
                                                 temp_falcons_rack('C1').top(-30))
        print('Water was transferred for Stock Sample no. 3 falcon.'
              'Stock Sample no. 3 is prepared.')
    else:
        print('\nDonor Plasma concentration is less than desired '
              'concentration of dilution in Stock Sample no. 3. '
              'Raw Donor Plasma will be mixed with spiked Donor Plasma.')
        dp_vol_for_ss3 = round(((dp_spiked_conc - ss3_conc) / (dp_spiked_conc - dp_conc)) * ss3_vol)
        print('Calculated volume of Raw Donor Plasma for Stock Sample no. 3 is: ', dp_vol_for_ss3)
        dp_spiked_vol_for_ss3 = ss3_vol - dp_vol_for_ss3
        print('Calculated volume of spiked Donor Plasma for Stock Sample no. 3 is: ', dp_spiked_vol_for_ss3)

        dp_source_current_vol = liquid_transfer(dp_vol_for_ss3, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                temp_falcons_rack('C1').top(-30))
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        dp_spiked_source_current_vol = dp_spiked_begin_vol
        dp_spiked_source_current_vol = liquid_transfer(dp_spiked_vol_for_ss3,
                                                       dp_spiked_source_current_vol, source_falcons_rack('A1'),
                                                       temp_falcons_rack('C1').top(-30))
        print('Spiked Donor Plasma was transferred for Stock Sample no. 3 falcon.'
              'Stock Sample no. 3 is prepared.')

    # ******* Stock Sample no. 24 preparation - Donor Plasma + Donor Plasma spiked ******* #
    dp_vol_for_ss24 = round(((dp_spiked_conc - ss24_conc) / (dp_spiked_conc - dp_conc)) * ss24_vol)
    dp_spiked_vol_for_ss24 = ss24_vol - dp_vol_for_ss24

    dp_source_current_vol = liquid_transfer(dp_vol_for_ss24, dp_source_current_vol,
                                            source_falcons_rack('A3'),
                                            temp_falcons_rack('A2').top(-30))
    print('\n', dp_vol_for_ss24, ' ul of Donor Plasma was transferred to temporary Stock Sample no. 24 falcon.')

    dp_spiked_source_current_vol = liquid_transfer(dp_spiked_vol_for_ss24, dp_spiked_source_current_vol,
                                                   source_falcons_rack('A1'),
                                                   temp_falcons_rack('A2').top(-30))
    print(dp_spiked_vol_for_ss24,
          'ul of Spiked Donor Plasma was transferred to temporary Stock Sample no. 24 falcon. The SS#24 prepared.\n')

    # ******* Stock Samples no. 4 - 8 preparation in 1.5 ml tubes ******* #
    j = 0
    dilB_source_current_vol = dilB_begin_vol
    for i in range(70, 20, -10):
        dp_vol_for_tubes = round(((dilB_conc - i) / (dilB_conc - dp_conc)) * ss_tubes_vol)
        dp_source_current_vol = liquid_transfer(dp_vol_for_tubes, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                ss_tubes_rack(j).top(-5))
        print(dp_vol_for_tubes, ' ul of Donor Plasma to', j, 'ss tube added.')

        dilB_vol_for_tubes = round(((i - dp_conc) / (dilB_conc - dp_conc)) * ss_tubes_vol)
        dilB_source_current_vol = liquid_transfer(dilB_vol_for_tubes, dilB_source_current_vol,
                                                  source_falcons_rack('A2'),
                                                  ss_tubes_rack(j).top(-5))
        print(dilB_vol_for_tubes, ' ul of Dilution B to', j, 'ss tube added.')
        j = j + 1
    print('The Stock Samples no. 4 - 8 preparation finished.\n')

    # ******* Stock Samples no. 9 - 23 preparation in 1.5 ml tubes ******* #

    # Stock Sample no. 9 - 100% spiked Donor Plasma
    dp_spiked_source_current_vol = liquid_transfer(ss_tubes_vol, dp_spiked_source_current_vol,
                                                   source_falcons_rack('A1'),
                                                   ss_tubes_rack(j).top(-5))
    print(ss_tubes_vol, ' ul of spiked Donor Plasma transferred to ss tube number ', j,
          'Stock Sample no. 9 () prepared.\n')

    # Stock Samples no. 10 - 22 (Raw Donor Plasma + Donor Plasma Spiked)
    conc_step = round(((dp_spiked_conc - dp_conc) / 14), 3)
    j = j + 1
    for i in range(13):
        desired_conc = round((dp_spiked_conc - (i + 1) * conc_step), 1)
        print('\ndesired concentration:', desired_conc)

        dp_spiked_vol_for_tubes = round(((desired_conc - dp_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        dp_spiked_source_current_vol = liquid_transfer(dp_spiked_vol_for_tubes,
                                                       dp_spiked_source_current_vol, source_falcons_rack('A1'),
                                                       ss_tubes_rack(j).top(-5))
        print(dp_spiked_vol_for_tubes, ' ul of spiked Donor Plasma to', j, 'ss tube added.')

        dp_vol_for_tubes = round(((dp_spiked_conc - desired_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        dp_source_current_vol = liquid_transfer(dp_vol_for_tubes, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                ss_tubes_rack(j).top(-5))
        print(dp_vol_for_tubes, ' ul of Donor Plasma to', j, 'ss tube added.')

        j = j + 1

    print('Serial dilutions for Stock Samples no. 10 - 22 from raw Donor Plasma and spiked Donor Plasma prepared.\n')

    # Stock Sample no. 23 - 100% Raw Donor Plasma
    dp_source_current_vol = liquid_transfer(ss_tubes_vol, dp_source_current_vol,
                                            source_falcons_rack('A3'), ss_tubes_rack(j).top(-5))
    print(ss_tubes_vol, ' ul of Donor Plasma transferred to ss tube number ', j,
          'Stock Sample no. 23 () prepared.\n')


# ********         VORTEX PAUSE START        ************ #

# ********         VORTEX PAUSE END          ************ #

# global cobas_tube_no
cobas_tube_no = 0


# method for transferring from temporary tubes and falcons into the Cobas tubes
def transfer_to_turb_tubes():
    print('\nTRANSFER TO TURB TUBES METHOD STARTED')
    cobas_tubes_vol = 100

    # transferring Stock Samples no. 1, no. 2 and no. 3
    global cobas_tube_no
    for cobas_tube_no in range(3):
        single1000.pick_up_tip()
        single1000.aspirate(cobas_tubes_vol, temp_falcons_rack(cobas_tube_no).bottom(10))
        single1000.dispense(single1000.current_volume, cobas_tuberack(cobas_tube_no))
        single1000.drop_tip()
        print('cobas_tube_no: ', cobas_tube_no)
    print('Stock Samples 1 - 3 transferred to cobas tubes.\n')

    # transferring Stock Samples no. 4 - 23
    i = 0
    cobas_tube_no = cobas_tube_no + 1
    # global cobas_tube_no
    for cobas_tube_no in range(cobas_tube_no, 23):
        single1000.pick_up_tip()
        single1000.aspirate(cobas_tubes_vol, ss_tubes_rack(i))
        single1000.dispense(single1000.current_volume, cobas_tuberack(cobas_tube_no))
        single1000.drop_tip()
        i = i + 1
        print('cobas_tube_no: ', cobas_tube_no)
    print('Stock Samples 4 - 23 transferred to cobas tubes.\n')

    cobas_tube_no = cobas_tube_no + 1
    single1000.pick_up_tip()
    single1000.aspirate(cobas_tubes_vol, temp_falcons_rack('A2').bottom(10))
    single1000.dispense(single1000.current_volume, cobas_tuberack(cobas_tube_no))
    single1000.drop_tip()
    print('Stock Sample 24 transferred to cobas tube number:', cobas_tube_no, '\n\n')


# ********         TURB TESTS PAUSE START       ************ #

# ********         TURB TESTS PAUSE END         ************ #

# method for validation sample preparation
global dest_current_rack
dest_current_rack = 0

global current_tube
current_tube = 0


def validation_samples_preparation(validation_sample_vol, ss1_vol, ss2_vol, ss3_vol, ss24_vol, ss_tubes_vol):
    global h2o_source_current_vol
    global current_tube
    global dest_current_rack

    # transferring water to Validation Samples no. 1 - 10
    for current_tube in range(10):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        h2o_source_current_vol = liquid_transfer(validation_sample_vol, h2o_source_current_vol,
                                                 source_falcons_rack('B1'),
                                                 destination_tube.top(-10))
        print('Water transferred into tube ', destination_tube, 'VS#', current_tube)

    # transferring dilution from Stock Sample no. 1 to Validation Samples no. 11 - 20
    # global current_tube
    ss1_current_vol = ss1_vol
    for current_tube in range(current_tube + 1, 20):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss1_current_vol = liquid_transfer(validation_sample_vol, ss1_current_vol, temp_falcons_rack('A1'),
                                          destination_tube.top(-10))
        print('Dilutions from SS#1 transferred into tube ', destination_tube, 'VS#', current_tube)

    # transferring dilution from Stock Sample no. 2 to Validation Samples no. 21 - 30
    ss2_current_vol = ss2_vol
    for current_tube in range(current_tube + 1, 30):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss2_current_vol = liquid_transfer(validation_sample_vol, ss2_current_vol, temp_falcons_rack('B1'),
                                          destination_tube.top(-10))
        print('Dilutions from SS#2 transferred into tube ', destination_tube, 'VS#', current_tube)

    # transferring dilution from Stock Sample no. 3 to Validation Samples no. 31 - 45
    ss3_current_vol = ss3_vol
    for current_tube in range(current_tube + 1, 45):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss3_current_vol = liquid_transfer(validation_sample_vol, ss3_current_vol, temp_falcons_rack('C1'),
                                          destination_tube.top(-10))
        print('Dilutions from SS#3 transferred into tube ', destination_tube, 'VS#', current_tube)

    # transferring dilution from Stock Samples no. 4 - 23 to Validation Samples no. 46 - 65
    i = 0
    for current_tube in range(current_tube + 1, 65):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        liquid_transfer(validation_sample_vol, ss_tubes_vol, ss_tubes_rack(i), destination_tube.top(-10))
        print('Dilutions from ', ss_tubes_rack(i), ' transferred into tube ', destination_tube, 'VS#', current_tube)
        i = i + 1

    # transferring dilution from Stock Sample no. 24 to Validation Samples no. 66 - 80
    ss24_current_vol = ss24_vol
    for current_tube in range(current_tube + 1, 80):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss24_current_vol = liquid_transfer(validation_sample_vol, ss24_current_vol,
                                           temp_falcons_rack('A2'),
                                           destination_tube.top(-10))
        print('Dilutions from SS#24 transferred into tube ', destination_tube, 'VS#', current_tube)


# custom method for transferring the liquid
def liquid_transfer(transfer_vol, current_vol, source, destination):
    single1000.pick_up_tip()
    single50.pick_up_tip()
    while transfer_vol != 0:
        if transfer_vol >= 1000:
            single1000.aspirate(1000, source_aspirating_height(current_vol, source))
            single1000.dispense(single1000.current_volume, destination)
            transfer_vol = transfer_vol - 1000
            current_vol = current_vol - 1000

        elif transfer_vol >= 100:
            single1000.aspirate(transfer_vol, source_aspirating_height(current_vol, source))
            single1000.dispense(single1000.current_volume, destination)
            transfer_vol = 0
            current_vol = current_vol - transfer_vol

        elif 100 > transfer_vol > 50:
            single50.aspirate(50, source_aspirating_height(current_vol, source))
            single50.dispense(single50.current_volume, destination)
            transfer_vol = transfer_vol - 50
            current_vol = current_vol - 50

        elif 50 >= transfer_vol > 0:
            single50.aspirate(transfer_vol, source_aspirating_height(current_vol, source))
            single50.dispense(single50.current_volume, destination)
            transfer_vol = 0
            current_vol = current_vol - transfer_vol

    blow_outs(2, single1000)
    blow_outs(2, single50)
    single1000.drop_tip()
    single50.drop_tip()
    return current_vol


# the height of aspirating from falcon calculating
def source_aspirating_height(current_vol, source):
    if source == source_falcons_rack('A3'):
        if current_vol >= 5000:
            height = 0.0018 * current_vol - 128
            return source.top(height)
        else:
            return source.bottom(5)
    else:
        if current_vol <= 15000 and current_vol > 7000:
            height = 0.0063 * current_vol - 120
            return source.top(height)
        elif current_vol <= 7000 and current_vol > 2000:
            height = 0.0067 * current_vol - 135
            return source.top(height)
        elif current_vol <= 2000 and current_vol > 0:
            return source.bottom(5)


# selecting proper tube rack for validation tubes iteration
def dest_validation_tube(validation_tuberacks_array, iteration):
    global dest_current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        dest_current_rack = dest_current_rack + 1
    return validation_tuberacks_array[dest_current_rack][iteration - (tubes_amount_in_rack * dest_current_rack)]


# how much blow_outs is supposed to be performed
def blow_outs(times, pipette):
    for i in range(times):
        pipette.blow_out()


# method for checking if the concentration of SS#24 is greater than concentration of Donor Plasma
def dp_and_ss24_conc_comparison(ss24_conc, dp_conc):
    if ss24_conc < dp_conc:
        robot.comment('Concentration of SS#24 is lower than Donor Plasma concentration.'
                      'Change the desired concentration of SS#24.')
        sys.exit()


# ****************************************************************************************#

# invoke method
dp_begin_vol_invoke = 45000
h2o_begin_vol_invoke = 13000
dp_spiked_begin_vol_invoke = 6000
dilB_begin_vol_invoke = 7000
dp_conc_invoke = 2.5
dp_spiked_conc_invoke = 15.3
dilB_conc_invoke = 503
ss1_vol_invoke = 4000
ss2_vol_invoke = 3000
ss3_vol_invoke = 5000
ss24_vol_invoke = 2500
ss3_conc_invoke = 5.0
ss24_conc_invoke = 8.0
ss_tubes_vol_invoke = 1500

dp_and_ss24_conc_comparison(ss24_conc_invoke, dp_conc_invoke)

dilutions_prep(dp_begin_vol_invoke, h2o_begin_vol_invoke, dp_spiked_begin_vol_invoke, dilB_begin_vol_invoke,
               dp_conc_invoke, dp_spiked_conc_invoke, dilB_conc_invoke,
               ss1_vol_invoke, ss2_vol_invoke, ss3_vol_invoke, ss24_vol_invoke, ss3_conc_invoke, ss24_conc_invoke,
               ss_tubes_vol_invoke)

# VORTEX PAUSE #
robot.pause()
robot.comment(
    'Take out the 15 ml falcons from 2nd slot and mix them with Vortex. '
    'Afterwards put them to the origin places. Mix also the tubes from the 1st slot. '
    'Put them also back to their origin place.'
    '\nRemove the waste from the trash bin.'
    '\nThen select RESUME and the protocol will be executed further.')

transfer_to_turb_tubes()

# TURB TESTS PAUSE #
robot.pause()
robot.comment('The pipetted samples can be measured on Cobas turb device.'
              '\nIf done, press RESUME and the protocol will be executed further.')

validation_sample_vol_invoke = 500
validation_samples_preparation(validation_sample_vol_invoke, ss1_vol_invoke, ss2_vol_invoke, ss3_vol_invoke,
                               ss24_vol_invoke, ss_tubes_vol_invoke)
