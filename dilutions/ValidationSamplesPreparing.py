from opentrons import labware, instruments, robot
import math


last_rack = 0


current_rack = 0
def dispense_plasma(is_increase, tube_amount, diff, final_vol, single50, single1000, source, tubes, current_vol):
    single50.pick_up_tip()
    single1000.pick_up_tip()

    tubes_amount_in_rack = 35

    global last_rack
    last_rack = math.floor((tube_amount - 1) / tubes_amount_in_rack)

    for i in range(tube_amount):
        transfer_vol = round(final_vol - i * diff)

        used_pipette = which_pipette(transfer_vol, single50, single1000)

        transfer(used_pipette, transfer_vol, current_vol, source, is_increase,
                 tubes, i, tubes_amount_in_rack, tube_amount)

        check_if_tip_replace(used_pipette, single50)

        current_vol = current_vol - transfer_vol
        print(transfer_vol, ' ul of plasma added to tube ', i + 1)

    single50.drop_tip()
    single1000.drop_tip()


# main method for dispening plasma
def calc_min_begin_vol(tube_amount, diff):
    calculated_min = 0
    for i in range(tube_amount):
        calculated_min = calculated_min + i * diff
    return calculated_min


# checking if begin volume is enough for all dilutions
def which_pipette_tip_counter(used_pipette, single50):
    if used_pipette == single50:
        global counter_pipette50
        counter_pipette50 = counter_pipette50 + 1
        return counter_pipette50
    else:
        global counter_pipette1000
        counter_pipette1000 = counter_pipette1000 + 1
        return counter_pipette1000


# method for tip iterating
def transfer(used_pipette, transfer_vol, current_vol, source, is_increase, tubes,
             i, tubes_amount_in_rack, tube_amount):
    # using touch tip instance for small volumes
    if (transfer_vol < 100) and (transfer_vol > 50):
        for j in range(2):
            used_pipette.aspirate(transfer_vol / 2, source_aspirating_height(current_vol, source))
            used_pipette.dispense(used_pipette.current_volume,
                                  destination(is_increase, tubes, i, tubes_amount_in_rack, tube_amount).top(
                                      -15)).blow_out().touch_tip(radius=0.7, v_offset=-10)

    elif (transfer_vol < 50) and (transfer_vol > 0):
        used_pipette.aspirate(transfer_vol, source_aspirating_height(current_vol, source))
        used_pipette.dispense(used_pipette.current_volume,
                              destination(is_increase, tubes, i, tubes_amount_in_rack, tube_amount).top(
                                  -15)).blow_out().touch_tip(radius=0.7, v_offset=-10)

    else:
        used_pipette.aspirate(transfer_vol, source_aspirating_height(current_vol, source))
        used_pipette.dispense(used_pipette.current_volume,
                              destination(is_increase, tubes, i, tubes_amount_in_rack, tube_amount).top(
                                  -15)).blow_out()

    blow_outs(2, used_pipette)


# to zostaje ale pozmieniać trochę
# method for transferring the liquid
def dilutions_prep(dp_conc, dp_spiked_conc, dilB_conc, ss1_vol, ss2_vol, ss3_vol, ss24_vol, ss3_conc, ss24_conc,
                   ss_tubes_vol):
    # creates custom labware if currently not created
    tube_rack_35 = "tube_rack_35"
    if tube_rack_35 not in labware.list():
        tube_rack_35 = labware.create("tube_rack_35",
                                      grid=(7, 5),
                                      spacing=(16.25, 14.56),
                                      diameter=10,
                                      depth=41)

    ss_tubes = labware.load('tube_rack_35', slot='1')
    temp_falcons = labware.load('tube-rack-15_50ml', slot='2')
    cobas_tubes = labware.load('24-vial-rack', slot='3')
    valid_tubes_A = labware.load('tube_rack_35', slot='4')
    valid_tubes_B = labware.load('tube_rack_35', slot='5')
    valid_tubes_C = labware.load('tube_rack_35', slot='6')
    source_falcons = labware.load('tube-rack-15_50ml', slot='7')
    tip_rack_small_A = labware.load('opentrons-tiprack-300ul', slot='8')
    tip_rack_big_A = labware.load('tiprack-1000ul', slot='9')
    tip_rack_small_B = labware.load('opentrons-tiprack-300ul', slot='10')
    tip_rack_big_B = labware.load('tiprack-1000ul', slot='11')

    valid_tubes_array = [valid_tubes_A, valid_tubes_B, valid_tubes_C]

    single50 = instruments.P50_Single(mount='right',
                                      tip_racks=[tip_rack_small_A, tip_rack_small_B],
                                      aspirate_flow_rate=50,
                                      dispense_flow_rate=100)

    single1000 = instruments.P1000_Single(mount='left',
                                          tip_racks=[tip_rack_big_A, tip_rack_big_B],
                                          aspirate_flow_rate=1000,
                                          dispense_flow_rate=1500)

    #
    #
    # Stock Sample no. 1 preparation - 16 times diluted Donor Plasma with water
    dp_vol_for_ss1 = round(ss1_vol / 16)
    h2_o_vol_for_ss1 = ss1_vol - dp_vol_for_ss1

    used_pipette = which_pipette(dp_vol_for_ss1, single50, single1000)
    used_pipette.transfer(dp_vol_for_ss1, source_falcons('A3'), temp_falcons('A1'), new_tip='always',
                          blow_out=True)
    blow_outs(2, used_pipette)

    used_pipette = which_pipette(h2_o_vol_for_ss1, single50, single1000)
    used_pipette.transfer(h2_o_vol_for_ss1, source_falcons('B1'), temp_falcons('A1'), new_tip='always',
                          blow_out=True)
    blow_outs(2, used_pipette)

    #
    #
    # Stock Sample no. 2 preparation - raw Donor Plasma
    used_pipette = which_pipette(ss2_vol, single50, single1000)
    used_pipette.transfer(ss2_vol, source_falcons('A3'), temp_falcons('A2'), new_tip='always', blow_out=True)
    blow_outs(2, used_pipette)

    #
    #
    # Stock Sample no. 3 preparation - Donor Plasma + Donor Plasma spiked OR Donor Plasma + water
    if dp_conc >= ss3_conc:
        dp_vol_for_ss3 = round((ss3_conc / dp_conc) * ss3_vol)
        h2_o_vol_for_ss3 = ss3_vol - dp_vol_for_ss3

        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        used_pipette.transfer(dp_vol_for_ss3, source_falcons('A3'), temp_falcons('B1'), new_tip='always', blow_out=True)
        blow_outs(2, used_pipette)

        used_pipette = which_pipette(h2_o_vol_for_ss3, single50, single1000)
        used_pipette.transfer(h2_o_vol_for_ss3, source_falcons('A1'), temp_falcons('B1'), new_tip='always',
                              blow_out=True)
        blow_outs(2, used_pipette)
    else:
        dp_vol_for_ss3 = round(((dp_spiked_conc - ss3_conc) / (dp_spiked_conc - dp_conc)) * ss3_vol)
        dp_spiked_vol_for_ss3 = ss3_vol - dp_vol_for_ss3

        used_pipette = which_pipette(dp_vol_for_ss3, single50, single1000)
        used_pipette.transfer(dp_vol_for_ss3, source_falcons('A3'), temp_falcons('B1'), new_tip='always', blow_out=True)
        blow_outs(2, used_pipette)

        used_pipette = which_pipette(dp_spiked_vol_for_ss3, single50, single1000)
        used_pipette.transfer(dp_spiked_vol_for_ss3, source_falcons('A1'), temp_falcons('B1'), new_tip='always',
                              blow_out=True)
        blow_outs(2, used_pipette)

    #
    #
    # Stock Sample no. 24 preparation - Donor Plasma + Donor Plasma spiked
    dp_vol_for_ss24 = round(((dp_spiked_conc - ss24_conc) / (dp_spiked_conc - dp_conc)) * ss24_vol)
    dp_spiked_vol_for_ss24 = ss24_vol - dp_vol_for_ss24

    used_pipette = which_pipette(dp_vol_for_ss24, single50, single1000)
    used_pipette.transfer(dp_vol_for_ss24, source_falcons('A3'), temp_falcons('B2'), new_tip='always', blow_out=True)
    blow_outs(2, used_pipette)

    used_pipette = which_pipette(dp_spiked_vol_for_ss24, single50, single1000)
    used_pipette.transfer(dp_spiked_vol_for_ss24, source_falcons('A1'), temp_falcons('B2'), new_tip='always',
                          blow_out=True)
    blow_outs(2, used_pipette)

    #
    #
    # Stock Samples no. 4 - 8 preparation in 1.5 ml tubes
    #
    # Donor Plasma transferring
    for i range(70, 20, -10):
        j = 0
        dp_vol_for_tubes = round(((dilB_conc - i) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_vol_for_tubes, source_falcons('A3'), ss_tubes(j), new_tip='never', blow_out=True)
        blow_outs(2, used_pipette)
        j = j + 1

    # Dilution B transferring
    for i range(30, 80, 10):
        j = 0
        dilB_vol_for_tubes = round(((i - dp_conc) / (dilB_conc - dp_conc)) * ss_tubes_vol)

        used_pipette = which_pipette(dilB_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dilB_vol_for_tubes, source_falcons('A2'), ss_tubes(j), new_tip='never', blow_out=True)
        blow_outs(2, used_pipette)
        j = j + 1

    #
    # Stock Samples no. 9 - 23 preparation in 1.5 ml tubes
    #
    # Stock Sample no. 9 - 100% Donor Plasma spiked
    used_pipette = which_pipette(ss_tubes_vol, single50, single1000)
    used_pipette.transfer(ss_tubes_vol, source_falcons('A1'), ss_tubes(j), blow_out=True)
    blow_outs(2, used_pipette)

    conc_step = round((dilB_conc - dp_conc) / 14)
    j = k
    # Donor Plasma spiked transferring
    for i in range (13):
        desired_conc = dp_spiked_conc-i*conc_step
        dp_spiked_vol_for_tubes=round(((desired_conc- dp_conc)/(dp_spiked_conc-dp_conc))*ss_tubes_vol)
        used_pipette = which_pipette(dp_spiked_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_spiked_vol_for_tubes, source_falcons('A1'), ss_tubes(j), new_tip='never', blow_out = True)
        blow_outs(2, used_pipette)

    # Raw Donor Plasma transferring
    for i in range(13):
        desired_conc = dp_spiked_conc-i*conc_step
        dp_vol_for_tubes = round(((dp_spiked_conc-  desired_conc)/(dp_spiked_conc-dp_conc))*ss_tubes_vol)
        used_pipette = which_pipette(dp_vol_for_tubes, single50, single1000)
        used_pipette.transfer(dp_vol_for_tubes, source_falcons('A1'), ss_tubes(k), new_tip='never',
                              blow_out=True)
        blow_outs(2, used_pipette)

# ********************************************************************** #
# VORTEX PAUSE #
 # TODO continue writing here








# *************************************************************************************************** #
    # OLD PROTOCOL

    # difference value calculating
    current_vol = begin_vol
    diff = round(final_vol / (tube_amount - 1), 2)

    if begin_vol < calc_min_begin_vol(tube_amount, diff):
        robot.comment('Begin volume is too little. Pour more liquid into the falcon.')
    return

    # dispensing plasma A from final volume to 0 ul, tubes iterated from the first to the last one
    dispense_plasma(True, tube_amount, diff, final_vol, single50, single1000, plasma_falcon('A1'), tubes, current_vol)

    current_vol = begin_vol

    # tubes iteration from scratch
    tubes = [tubes1, tubes2, tubes3, tubes4]

    # tubes in racks iteration from scratch
    global current_rack
    current_rack = 0

    # dispensing plasma B from final volume to 0 ul, tubes iterated from the last one to the first
    dispense_plasma(False, tube_amount, diff, final_vol, single50, single1000, plasma_falcon('A3'), tubes, current_vol)

    print(tube_amount, 'dilutions prepared.')


# method for changing pipette tip every 5 pipetting cycles
def check_if_tip_replace(pipette, single50):
    counter_pipette = which_pipette_tip_counter(pipette, single50)
    if counter_pipette % 5 == 0 and counter_pipette != 0:
        print('pipette tips of ', pipette.name, 'changed')
        pipette.drop_tip()
        pipette.pick_up_tip()
        print('current tip', pipette.current_tip(), ' from pipette ', pipette)
        print('Picking up tip from ', pipette.tip_racks, 'counter pipette =', counter_pipette)


# destination place iterating
def destination(is_increase, tubes, iteration, tubes_amount_in_rack, tube_amount):
    global current_rack
    global last_rack
    if is_increase:
        if iteration % tubes_amount_in_rack == 0 and iteration != 0:
            current_rack = current_rack + 1
        return tubes[current_rack][iteration - (tubes_amount_in_rack * current_rack)]
    else:
        if (tube_amount - iteration) % 35 == 0 and iteration != 0:
            last_rack = last_rack - 1
        return tubes[last_rack][tube_amount - last_rack * tubes_amount_in_rack - iteration - 1]


# the height of aspirating from falcon calculating
def source_aspirating_height(current_vol, source):
    if current_vol >= 5000:
        height = 0.0018 * current_vol - 118
        return source.top(height)
    else:
        return source.bottom(3)


# to zostaje
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
begin_vol1 = 40000
final_vol1 = 648
tube_amount1 = 105
serial_dil(begin_vol1, final_vol1, tube_amount1)
