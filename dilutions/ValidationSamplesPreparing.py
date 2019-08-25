from opentrons import labware, instruments, robot

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
tip_rack_small = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack_big_C = labware.load('tiprack-1000ul', slot='11')

validation_tuberacks_array = [validation_tuberack_A, validation_tuberack_B, validation_tuberack_C]

single50 = instruments.P50_Single(mount='right',
                                  tip_racks=[tip_rack_small],
                                  aspirate_flow_rate=50,
                                  dispense_flow_rate=100)

single1000 = instruments.P1000_Single(mount='left',
                                      tip_racks=[tip_rack_big_A, tip_rack_big_B, tip_rack_big_C],
                                      aspirate_flow_rate=1000,
                                      dispense_flow_rate=1500)
# Global variables
h2o_source_current_vol = 0


# method for preparing temporary dilutions
def dilutions_prep(dp_begin_vol, h2o_begin_vol, dp_spiked_begin_vol, dilB_begin_vol, dp_conc, dp_spiked_conc, dilB_conc,
                   ss1_vol, ss2_vol, ss3_vol, ss24_vol, ss3_conc, ss24_conc,
                   ss_tubes_vol):
    # Stock Sample no. 1 preparation - 16 times diluted Donor Plasma with water
    dp_vol_for_ss1 = round(ss1_vol / 16)
    print("Donor Plasma volume that will be transferred for SS#1: ", dp_vol_for_ss1)
    h2o_vol_for_ss1 = ss1_vol - dp_vol_for_ss1
    print("Water volume that will be transferred for SS#1: ", h2o_vol_for_ss1)
    # Donor Plasma transferring
    dp_source_current_vol = dp_begin_vol
    used_pipette = which_pipette(dp_vol_for_ss1, single50, single1000)
    dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_ss1, dp_source_current_vol,
                                            source_falcons_rack('A3'),
                                            temp_falcons_rack('A1'))

    # Water transferring
    global h2o_source_current_vol
    h2o_source_current_vol = h2o_begin_vol
    used_pipette = which_pipette(h2o_vol_for_ss1, single50, single1000)
    h2o_source_current_vol = liquid_transfer(used_pipette, h2o_vol_for_ss1, h2o_source_current_vol,
                                             source_falcons_rack('B1'),
                                             temp_falcons_rack('A1'))
    print('Stock Sample no. 1 in temporary falcon prepared.\n')

    # Stock Sample no. 2 preparation - raw Donor Plasma
    used_pipette = which_pipette(ss2_vol, single50, single1000)
    dp_source_current_vol = liquid_transfer(used_pipette, ss2_vol, dp_source_current_vol, source_falcons_rack('A3'),
                                            temp_falcons_rack('A2'))
    print('\n', ss2_vol, '[ul] of Raw Donor Plasma was transferred. '
                         'Stock Sample no. 2 in temporary falcon prepared.')

    # Stock Sample no. 3 preparation - Donor Plasma + Donor Plasma spiked OR Donor Plasma + water
    if dp_conc >= ss3_conc:
        print('\nDonor Plasma concentration is greater than desired '
              'concentration of dilution in Stock Sample no. 3. '
              'Raw Donor Plasma will be diluted with water.')
        dp_vol_for_ss3 = round((ss3_conc / dp_conc) * ss3_vol)
        print('Calculated volume of Donor Plasma for Stock Sample no. 3 is: ', dp_vol_for_ss3)
        h2o_vol_for_ss3 = ss3_vol - dp_vol_for_ss3
        print('Calculated volume of water for Stock Sample no. 3 is: ', h2o_vol_for_ss3)
        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_ss3, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                temp_falcons_rack('B1'))
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        used_pipette = which_pipette(h2o_vol_for_ss3, single50, single1000)
        h2o_source_current_vol = liquid_transfer(used_pipette, h2o_vol_for_ss3, h2o_source_current_vol,
                                                 source_falcons_rack('A1'),
                                                 temp_falcons_rack('B1'))
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

        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_ss3, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                temp_falcons_rack('B1'))
        print('Donor Plasma was transferred for Stock Sample no. 3 falcon.')

        dp_spiked_source_current_vol = dp_spiked_begin_vol
        used_pipette = which_pipette(dp_spiked_vol_for_ss3, single50, single1000)
        dp_spiked_source_current_vol = liquid_transfer(used_pipette, dp_spiked_vol_for_ss3,
                                                       dp_spiked_source_current_vol, source_falcons_rack('A1'),
                                                       temp_falcons_rack('B1'))
        print('Spiked Donor Plasma was transferred for Stock Sample no. 3 falcon.'
              'Stock Sample no. 3 is prepared.')

    # Stock Sample no. 24 preparation - Donor Plasma + Donor Plasma spiked
    dp_vol_for_ss24 = round(((dp_spiked_conc - ss24_conc) / (dp_spiked_conc - dp_conc)) * ss24_vol)
    dp_spiked_vol_for_ss24 = ss24_vol - dp_vol_for_ss24

    used_pipette = which_pipette(dp_vol_for_ss24, single50, single1000)
    dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_ss24, dp_source_current_vol,
                                            source_falcons_rack('A3'),
                                            temp_falcons_rack('B2'))
    print('\nDonor Plasma was transferred to temporary Stock Sample no. 24 falcon.')

    used_pipette = which_pipette(dp_spiked_vol_for_ss24, single50, single1000)
    dp_spiked_source_current_vol = liquid_transfer(used_pipette, dp_spiked_vol_for_ss24, dp_spiked_source_current_vol,
                                                   source_falcons_rack('A1'),
                                                   temp_falcons_rack('B2'))
    print('Spiked Donor Plasma was transferred to temporary Stock Sample no. 24 falcon.')

    # Stock Samples no. 4 - 8 preparation in 1.5 ml tubes
    # Donor Plasma transferring
    j = 0
    for i in range(70, 20, -10):
        dp_vol_for_tubes = round(((dilB_conc - i) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_tubes, dp_source_current_vol,
                                                source_falcons_rack('A3'),
                                                ss_tubes_rack(j))
        j = j + 1
    print('\nStock Samples no. 4 - 8 preparation in progress. Donor Plasma to these tubes added.')

    # Dilution B transferring
    j = 0
    dilB_source_current_vol = dilB_begin_vol
    for i in range(30, 80, 10):
        dilB_vol_for_tubes = round(((i - dp_conc) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dilB_vol_for_tubes, single50, single1000)
        dilB_source_current_vol = liquid_transfer(used_pipette, dilB_vol_for_tubes, dilB_source_current_vol,
                                                  source_falcons_rack('A2'),
                                                  ss_tubes_rack(j))
        j = j + 1
    print('Dilution B to the Stock Samples no. 4 - 8 added. 8th tube has no.:', j, ' Their preparation finished.\n')

    # Stock Samples no. 9 - 23 preparation in 1.5 ml tubes

    # Stock Sample no. 9 - 100% spiked Donor Plasma
    j = j + 1
    used_pipette = which_pipette(ss_tubes_vol, single50, single1000)
    dp_spiked_source_current_vol = liquid_transfer(used_pipette, ss_tubes_vol, dp_spiked_source_current_vol,
                                                   source_falcons_rack('A1'),
                                                   ss_tubes_rack(j))
    print('Stock Sample no. 9 (spiked Donor Plasma) prepared. Its number is:', j, '\n')

    conc_step = round((dilB_conc - dp_conc) / 14)
    j = j + 1
    k = j
    # Donor Plasma spiked transferring
    for i in range(13):
        desired_conc = dp_spiked_conc - i * conc_step
        dp_spiked_vol_for_tubes = round(((desired_conc - dp_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        used_pipette = which_pipette(dp_spiked_vol_for_tubes, single50, single1000)
        dp_spiked_source_current_vol = liquid_transfer(used_pipette, dp_spiked_vol_for_tubes,
                                                       dp_spiked_source_current_vol, source_falcons_rack('A1'),
                                                       ss_tubes_rack(j))
        j = j + 1

    # Raw Donor Plasma transferring
    for i in range(13):
        desired_conc = dp_spiked_conc - i * conc_step
        dp_vol_for_tubes = round(((dp_spiked_conc - desired_conc) / (dp_spiked_conc - dp_conc)) * ss_tubes_vol)
        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        dp_source_current_vol = liquid_transfer(used_pipette, dp_vol_for_tubes, dp_source_current_vol,
                                                source_falcons_rack('A1'),
                                                ss_tubes_rack(k))
        k = k + 1
    print('Serial dilutions for Stock Samples no. 10 - 22 from raw Donor Plasma and spiked Donor Plasma prepared.')

    # Stock Sample no. 23 - 100% Donor Plasma
    k = k + 1
    used_pipette = which_pipette(ss_tubes_vol, single50, single1000)
    dp_source_current_vol = liquid_transfer(used_pipette, ss_tubes_vol, dp_source_current_vol,
                                            source_falcons_rack('A3'), ss_tubes_rack(k))
    print('SS#23 is tube no.:', k)
    print('Stock Sample no. 23 (pure Raw Donor Plasma) prepared.\n')


# ********         VORTEX PAUSE START        ************ #

# ********         VORTEX PAUSE END          ************ #

# global cobas_tube_no
cobas_tube_no = 0


# method for transferring from temporary tubes and falcons into the Cobas tubes
def transfer_to_turb_tubes():
    print('TRANSFER TO TURB TUBES METHOD STARTED')
    cobas_tubes_vol = 100

    # transferring Stock Samples no. 1, no. 2, no. 3 and no. 24
    # TODO poprawic ss1 -> cobas 01
    global cobas_tube_no
    for cobas_tube_no in range(5):
        if cobas_tube_no == 2:
            print('cobas_tube_no: ', cobas_tube_no)
        elif cobas_tube_no == 4:
            single1000.pick_up_tip()
            single1000.aspirate(cobas_tubes_vol, temp_falcons_rack(cobas_tube_no).top(-40))
            single1000.dispense(single1000.current_volume, cobas_tuberack(23))
            blow_outs(2, single1000)
            single1000.drop_tip()
            print('cobas_tube_no: ', cobas_tube_no)
        else:
            single1000.pick_up_tip()
            single1000.aspirate(cobas_tubes_vol, temp_falcons_rack(cobas_tube_no).top(-40))
            single1000.dispense(single1000.current_volume, cobas_tuberack(cobas_tube_no))
            blow_outs(2, single1000)
            single1000.drop_tip()
            print('cobas_tube_no: ', cobas_tube_no)

    # transferring Stock Samples no. 4 - 23
    i = 0
    print('Kobas: ', cobas_tube_no)
    # global cobas_tube_no
    for cobas_tube_no in range(cobas_tube_no, 24):
        single1000.pick_up_tip()
        single1000.aspirate(cobas_tubes_vol, ss_tubes_rack(i).top(-25))
        single1000.dispense(single1000.current_volume, cobas_tuberack(cobas_tube_no))
        blow_outs(2, single1000)
        single1000.drop_tip()
        i = i + 1
        print('cobas_tube_no: ', cobas_tube_no)


# ********         TURB TESTS PAUSE START       ************ #

# ********         TURB TESTS PAUSE END         ************ #

# method for validation sample preparation
# global current_rack
current_rack = 0

global current_tube
current_tube = 0


def validation_samples_preparation(validation_sample_vol, ss1_vol, ss2_vol, ss3_vol, ss24_vol):
    used_pipette = which_pipette(validation_sample_vol, single50, single1000)
    global h2o_source_current_vol

    # transferring water to Validation Samples no. 1 - 10
    for current_tube in range(10):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        h2o_source_current_vol = liquid_transfer(used_pipette, validation_sample_vol, h2o_source_current_vol,
                                                 source_falcons_rack('B1'),
                                                 destination_tube)

    # transferring dilution from Stock Sample no. 1 to Validation Samples no. 11 - 20
    ss1_current_vol = ss1_vol
    for current_tube in range(20):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss1_current_vol = liquid_transfer(used_pipette, validation_sample_vol, ss1_current_vol, temp_falcons_rack('A1'),
                                          destination_tube)

    # transferring dilution from Stock Sample no. 2 to Validation Samples no. 21 - 30
    ss2_current_vol = ss2_vol
    for current_tube in range(30):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss2_current_vol = liquid_transfer(used_pipette, validation_sample_vol, ss2_current_vol, temp_falcons_rack('A2'),
                                          destination_tube)

    # transferring dilution from Stock Sample no. 3 to Validation Samples no. 31 - 45
    ss3_current_vol = ss3_vol
    for current_tube in range(45):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss3_current_vol = liquid_transfer(used_pipette, validation_sample_vol, ss3_current_vol, temp_falcons_rack('B1'),
                                          destination_tube)

    # transferring dilution from Stock Samples no. 4 - 23 to Validation Samples no. 46 - 65
    i = 0
    for current_tube in range(65):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        used_pipette.pick_up_tip()
        used_pipette.aspirate(validation_sample_vol, ss_tubes_rack(i).top(-25))
        used_pipette.dispense(used_pipette.current_volume, destination_tube)
        blow_outs(2, used_pipette)
        used_pipette.drop_tip()
        i = i + 1

    # transferring dilution from Stock Sample no. 24 to Validation Samples no. 66 - 80
    ss24_current_vol = ss24_vol
    for current_tube in range(80):
        destination_tube = dest_validation_tube(validation_tuberacks_array, current_tube)
        ss24_current_vol = liquid_transfer(used_pipette, validation_sample_vol, ss24_current_vol,
                                           temp_falcons_rack('B2'),
                                           destination_tube)


def liquid_transfer(used_pipette, transfer_vol, current_vol, source, destination):
    used_pipette.pick_up_tip()
    if (transfer_vol > 0) and (transfer_vol <= 50) and (transfer_vol > 100) and (transfer_vol < 1000):
        used_pipette.aspirate(transfer_vol, source_aspirating_height(current_vol, source))
        used_pipette.dispense(used_pipette.current_volume, destination)
        current_vol = current_vol - transfer_vol

    elif (transfer_vol > 50) and (transfer_vol <= 100):
        for j in range(2):
            used_pipette.aspirate(transfer_vol / 2, source_aspirating_height(current_vol, source))
            used_pipette.dispense(used_pipette.current_volume, destination)
        current_vol = current_vol - transfer_vol

    elif transfer_vol >= 1000:
        repeat_times = round(transfer_vol / 1000)
        rest_liquid = transfer_vol - repeat_times * 1000
        for i in range(repeat_times):
            used_pipette.aspirate(1000, source_aspirating_height(current_vol, source))
            used_pipette.dispense(used_pipette.current_volume, destination)
        used_pipette.aspirate(rest_liquid, source_aspirating_height(current_vol, source))
        used_pipette.dispense(used_pipette.current_volume, destination)
        current_vol = current_vol - transfer_vol

    blow_outs(2, used_pipette)
    used_pipette.drop_tip()
    return current_vol


# the height of aspirating from falcon calculating
def source_aspirating_height(current_vol, source):
    if source == source_falcons_rack('A3'):
        if current_vol >= 5000:
            height = 0.0018 * current_vol - 118
            return source.top(height)
        else:
            return source.bottom(3)
    # else:
    # TODO add a function for 15 ml falcon


# selecting proper tube rack for validation tubes iteration
def dest_validation_tube(validation_tuberacks_array, iteration):
    global current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        current_rack = current_rack + 1
    print('ZROB MI TUTEJ PRINTA: ',validation_tuberacks_array[current_rack][iteration - (tubes_amount_in_rack * current_rack)])
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
dilutions_prep(44000, 13250, 12000, 10000, 2.0, 15.0, 503.0, 10000, 11000, 12000, 13000, 4.0, 8.7, 1500)

# VORTEX PAUSE #
robot.pause()
robot.comment(
    'Take out the 15 ml falcons from 2nd slot and mix them with Vortex. '
    'Put them to the origin places. Mix also the tubes from the 1st slot. '
    'Put them also back to their origin place.'
    '\nThen select RESUME and the protocol will be executed further.')

transfer_to_turb_tubes()

# TURB TESTS PAUSE #
robot.pause()
robot.comment('The pipetted samples can be measured on Cobas turb device.'
              '\nIf done, press RESUME and the protocol will be executed further.')

validation_samples_preparation(350, 10000, 11000, 12000, 13000)
