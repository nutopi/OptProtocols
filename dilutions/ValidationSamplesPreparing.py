from opentrons import labware, instruments, robot
import math

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
tip_rack_small_A = labware.load('opentrons-tiprack-300ul', slot='8')
tip_rack_big_A = labware.load('tiprack-1000ul', slot='9')
tip_rack_small_B = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack_big_B = labware.load('tiprack-1000ul', slot='11')

validation_tuberacks_array = [validation_tuberack_A, validation_tuberack_B, validation_tuberack_C]

single50 = instruments.P50_Single(mount='right',
                                  tip_racks=[tip_rack_small_A, tip_rack_small_B],
                                  aspirate_flow_rate=50,
                                  dispense_flow_rate=100)

single1000 = instruments.P1000_Single(mount='left',
                                      tip_racks=[tip_rack_big_A, tip_rack_big_B],
                                      aspirate_flow_rate=1000,
                                      dispense_flow_rate=1500)


# method for preparing temporary dilutions
def dilutions_prep(dp_conc, dp_spiked_conc, dilB_conc, ss1_vol, ss2_vol, ss3_vol, ss24_vol, ss3_conc, ss24_conc,
                   ss_tubes_vol):
    # Stock Sample no. 1 preparation - 16 times diluted Donor Plasma with water
    dp_vol_for_ss1 = round(ss1_vol / 16)
    print("Donor Plasma volume that will be transferred for SS#1: ", dp_vol_for_ss1, '\n')
    h2o_vol_for_ss1 = ss1_vol - dp_vol_for_ss1
    print("Water volume that will be transferred for SS#1: ", h2o_vol_for_ss1, '\n')

    used_pipette = which_pipette(dp_vol_for_ss1, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(dp_vol_for_ss1, source_falcons_rack('A3'), temp_falcons_rack('A1'), new_tip='never',
                          blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()

    used_pipette = which_pipette(h2o_vol_for_ss1, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(h2o_vol_for_ss1, source_falcons_rack('B1'), temp_falcons_rack('A1'), new_tip='never',
                          blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('Stock Sample no. 1 in temporary falcon prepared.\n')

    # Stock Sample no. 2 preparation - raw Donor Plasma
    used_pipette = which_pipette(ss2_vol, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(ss2_vol, source_falcons_rack('A3'), temp_falcons_rack('A2'), new_tip='never', blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('\n', ss2_vol, '[ul] of Raw Donor Plasma was transferred. '
                         'Stock Sample no. 2 in temporary falcon prepared.\n')

    # Stock Sample no. 3 preparation - Donor Plasma + Donor Plasma spiked OR Donor Plasma + water
    if dp_conc >= ss3_conc:
        print('Donor Plasma concentration is greater than desired concentration of dilution in Stock Sample no. 3. Raw Donor Plasma will be diluted with water.')
        dp_vol_for_ss3 = round((ss3_conc / dp_conc) * ss3_vol)
        print('Calculated volume of Donor Plasma for Stock Sample no. 3 is: ', dp_vol_for_ss3)
        h2o_vol_for_ss3 = ss3_vol - dp_vol_for_ss3
        print('Calculated volume of water for Stock Sample no. 3 is: ', h2o_vol_for_ss3)
        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        used_pipette.pick_up_tip()
        used_pipette.transfer(dp_vol_for_ss3, source_falcons_rack('A3'), temp_falcons_rack('B1'), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        used_pipette.drop_tip()
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        used_pipette = which_pipette(h2o_vol_for_ss3, single50, single1000)
        used_pipette.pick_up_tip()
        used_pipette.transfer(h2o_vol_for_ss3, source_falcons_rack('A1'), temp_falcons_rack('B1'), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        used_pipette.drop_tip()
        print('Water was transferred for Stock Sample no. 3 falcon.\n Stock Sample no. 3 is prepared.\n')
    else:
        print('Donor Plasma concentration is less than desired concentration of dilution in Stock Sample no. 3. Raw Donor Plasma will be mixed with spiked Donor Plasma.')
        dp_vol_for_ss3 = round(((dp_spiked_conc - ss3_conc) / (dp_spiked_conc - dp_conc)) * ss3_vol)
        print('Calculated volume of Raw Donor Plasma for Stock Sample no. 3 is: ', dp_vol_for_ss3)
        dp_spiked_vol_for_ss3 = ss3_vol - dp_vol_for_ss3
        print('Calculated volume of spiked Donor Plasma for Stock Sample no. 3 is: ', dp_spiked_vol_for_ss3)

        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        used_pipette.pick_up_tip()
        used_pipette.transfer(dp_vol_for_ss3, source_falcons_rack('A3'), temp_falcons_rack('B1'), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        used_pipette.drop_tip()
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        used_pipette = which_pipette(dp_spiked_vol_for_ss3, single50, single1000)
        used_pipette.pick_up_tip()
        used_pipette.transfer(dp_spiked_vol_for_ss3, source_falcons_rack('A1'), temp_falcons_rack('B1'),
                              new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        used_pipette.drop_tip()
        print('Spiked Donor Plasma was transferred for Stock Sample no. 3 falcon.\n Stock Sample no. 3 is prepared.\n')


    # Stock Sample no. 24 preparation - Donor Plasma + Donor Plasma spiked
    dp_vol_for_ss24 = round(((dp_spiked_conc - ss24_conc) / (dp_spiked_conc - dp_conc)) * ss24_vol)
    dp_spiked_vol_for_ss24 = ss24_vol - dp_vol_for_ss24

    used_pipette = which_pipette(dp_vol_for_ss24, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(dp_vol_for_ss24, source_falcons_rack('A3'), temp_falcons_rack('B2'), new_tip='never',
                          blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('\nDonor Plasma was transferred to temporary Stock Sample no. 24 falcon.')

    used_pipette = which_pipette(dp_spiked_vol_for_ss24, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(dp_spiked_vol_for_ss24, source_falcons_rack('A1'), temp_falcons_rack('B2'), new_tip='never',
                          blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('\nSpiked Donor Plasma was transferred to temporary Stock Sample no. 24 falcon.')

    # Stock Samples no. 4 - 8 preparation in 1.5 ml tubes
    # Donor Plasma transferring
    single1000.pick_up_tip()
    single50.pick_up_tip()
    for i in range(70, 20, -10):
        j = 0
        dp_vol_for_tubes = round(((dilB_conc - i) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_vol_for_tubes, source_falcons_rack('A3'), ss_tubes_rack(j), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        j = j + 1
    single50.drop_tip()
    single1000.drop_tip()
    print('\nStock Samples no. 4 - 8 preparation in progress. Donor Plasma to these tubes added.')

    # Dilution B transferring
    single1000.pick_up_tip()
    single50.pick_up_tip()
    for i in range(30, 80, 10):
        j = 0
        dilB_vol_for_tubes = round(((i - dp_conc) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dilB_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dilB_vol_for_tubes, source_falcons_rack('A2'), ss_tubes_rack(j), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
        j = j + 1
    single50.drop_tip()
    single1000.drop_tip()
    print('Dilution B to the Stock Samples no. 4 - 8 added. Their preparation finished.\n')


    # Stock Samples no. 9 - 23 preparation in 1.5 ml tubes

    # Stock Sample no. 9 - 100% spiked Donor Plasma
    used_pipette = which_pipette(ss_tubes_vol, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(ss_tubes_vol, source_falcons_rack('A1'), ss_tubes_rack(j), new_tip='never', blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('Stock Sample no. 9 (spiked Donor Plasma) prepared.')

    conc_step = round((dilB_conc - dp_conc) / 14)
    k = j
    # Donor Plasma spiked transferring
    single1000.pick_up_tip()
    single50.pick_up_tip()
    for i in range(13):
        desired_conc = dp_spiked_conc - i * conc_step
        dp_spiked_vol_for_tubes = round(((desired_conc - dp_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        used_pipette = which_pipette(dp_spiked_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_spiked_vol_for_tubes, source_falcons_rack('A1'), ss_tubes_rack(j), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    single50.drop_tip()
    single1000.drop_tip()

    # Raw Donor Plasma transferring
    single1000.pick_up_tip()
    single50.pick_up_tip()
    for i in range(13):
        desired_conc = dp_spiked_conc - i * conc_step
        dp_vol_for_tubes = round(((dp_spiked_conc - desired_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_vol_for_tubes, source_falcons_rack('A1'), ss_tubes_rack(k), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    single50.drop_tip()
    single1000.drop_tip()
    print('Serial dilutions for Stock Samples no. 10 - 22 from raw Donor Plasma and spiked Donor Plasma prepared.')

# Stock Sample no. 23 - 100% Donor Plasma
    used_pipette = which_pipette(ss_tubes_vol, single50, single1000)
    used_pipette.pick_up_tip()
    used_pipette.transfer(ss_tubes_vol, source_falcons_rack('A3'), ss_tubes_rack(i), new_tip='never', blow_out=True)
    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    print('Stock Sample no. 23 (pure Raw Donor Plasma) prepared.')

# ********         VORTEX PAUSE START        ************ #

# ********         VORTEX PAUSE END          ************ #

# method for transferring from temporary tubes and falcons into the Cobas tubes
def turb_tubes_transfer():
    cobas_tubes_vol = 100
    cobas_tube_no = 0

    # transferring Stock Samples no. 1, no. 2, no. 3 and no. 24
    # single1000.pick_up_tip()
    for cobas_tube_no in range(5):
        if cobas_tube_no == 2:
            return
        elif cobas_tube_no == 4:
            single1000.transfer(cobas_tubes_vol, temp_falcons_rack(cobas_tube_no), cobas_tuberack(23), new_tip='always',
                                blow_out=True)
            blow_outs(2, single1000)
        else:
            single1000.transfer(cobas_tubes_vol, temp_falcons_rack(cobas_tube_no), cobas_tuberack(cobas_tube_no),
                                new_tip='always', blow_out=True)
            blow_outs(2, single1000)
    single1000.drop_tip()

    # transferring Stock Samples no. 4 - 23
    print('cobas_tube_no: ', cobas_tube_no)
    i = 0
    single1000.pick_up_tip()
    for cobas_tube_no in range(20):
        single1000.transfer(cobas_tubes_vol, ss_tubes_rack(i), cobas_tuberack(cobas_tube_no), new_tip='always',
                            blow_out=True)
        blow_outs(2, single1000)
        i = i + 1
    single1000.drop_tip()

# ********         TURB TESTS PAUSE START       ************ #

# ********         TURB TESTS PAUSE END         ************ #

# method for validation sample preparation
global current_rack
current_rack = 0


def validation_samples_preparation(validation_sample_vol):
    global current_tube
    current_tube = 0
    used_pipette = which_pipette(validation_sample_vol, single50, single1000)

    # transferring water to Validation Samples no. 1 - 10
    used_pipette.pick_up_tip()
    for current_tube in range(10):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, source_falcons_rack('B1'), destination_tube, new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    used_pipette.drop_tip()

    # transferring dilution from Stock Sample no. 1 to Validation Samples no. 11 - 20
    used_pipette.pick_up_tip()
    for current_tube in range(20):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, temp_falcons_rack('A1'), destination_tube, new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    used_pipette.drop_tip()

    # transferring dilution from Stock Sample no. 2 to Validation Samples no. 21 - 30
    used_pipette.pick_up_tip()
    for current_tube in range(30):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, temp_falcons_rack('A2'), destination_tube, new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    used_pipette.drop_tip()

    # transferring dilution from Stock Sample no. 3 to Validation Samples no. 31 - 45
    used_pipette.pick_up_tip()
    for current_tube in range(45):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, temp_falcons_rack('B1'), destination_tube, new_tip='never',
                              blow_out=True)
    used_pipette.drop_tip()

    # transferring dilution from Stock Samples no. 4 - 23 to Validation Samples no. 46 - 65
    used_pipette.pick_up_tip()
    i = 0
    for current_tube in range(65):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, ss_tubes_rack(i), destination_tube, new_tip='never', blow_out=True)
        blow_outs(2, used_pipette)
        i = i + 1

    # transferring dilution from Stock Sample no. 24 to Validation Samples no. 66 - 80
    used_pipette.pick_up_tip()
    for current_tube in range(80):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.transfer(validation_sample_vol, temp_falcons_rack('B2'), destination_tube, new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)
    used_pipette.drop_tip


# *************************************************************************************************** #
# TODO add aspiration height depend on the begin volume of the liquids
# # the height of aspirating from falcon calculating
# def source_aspirating_height(current_vol, source):
#     if current_vol >= 5000:
#         height = 0.0018 * current_vol - 118
#         return source.top(height)
#     else:
#         return source.bottom(3)

#TODO add custom transfer method
#def transfer ():
    #aspiration, dispensing, blow_outs()

# selecting proper tube rack for validation tubes iteration
def dest_validation_tube(validation_tuberacks_array, iteration):
    global current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        current_rack = current_rack + 1
    return validation_tuberacks_array[current_rack][iteration - (tubes_amount_in_rack * current_rack)]


# which pipette should be used
def which_pipette(transfer_vol, single50, single1000):
    if transfer_vol < 100:
        return single50
    else:
        return single1000


# how much blow_outs is supposed to be performed
def blow_outs(times, pipette):
    for i in range(times):
        pipette.blow_out()


# ****************************************************************************************#

# invoke method
dilutions_prep(2, 15, 503, 15000, 15000, 15000, 15000, 3.5, 8.7, 1500)

# VORTEX PAUSE #
robot.pause()
robot.comment(
    'Take out the 15 ml falcons from 2nd slot and mix them with Vortex. '
    'Put them to the origin places. Mix also the tubes from the 1st slot. '
    'Put them also back to their origin place.'
    '\nThen select RESUME and the protocol will be executed further.')

turb_tubes_transfer()

# TURB TESTS PAUSE #
robot.pause()
robot.comment('The pipetted samples can be measured on Cobas turb device.'
              '\nIf done, press RESUME and the protocol will be executed further.')

validation_samples_preparation(350)
