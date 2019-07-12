from opentrons import labware, instruments, robot
import math


def serial_dil(begin_vol, final_vol, tube_amount):
    # creates custom labware if currently not created
    tube_2ml_rack_35 = "tube_2ml_rack_35"
    if tube_2ml_rack_35 not in labware.list():
        tube_2ml_rack_35 = labware.create("tube_2ml_rack_35",
                                          grid=(7, 5),
                                          spacing=(16.25, 14.56),
                                          diameter=10,
                                          depth=30)

    tubes1 = labware.load('tube_2ml_rack_35', slot='1')
    tubes2 = labware.load('tube_2ml_rack_35', slot='2')
    tubes3 = labware.load('tube_2ml_rack_35', slot='3')
    tubes4 = labware.load('tube_2ml_rack_35', slot='4')
    tip_rack_small = labware.load('opentrons-tiprack-300ul', slot='6')
    tip_rack_big = labware.load('tiprack-1000ul', slot='9')
    plasma_falcon = labware.load('opentrons-tuberack-15_50ml', slot='5')

    tubes = [tubes1, tubes2, tubes3, tubes4]

    single50 = instruments.P50_Single(mount='right',
                                      tip_racks=[tip_rack_small],
                                      aspirate_flow_rate=100,
                                      dispense_flow_rate=100)

    single1000 = instruments.P1000_Single(mount='left',
                                          tip_racks=[tip_rack_big],
                                          aspirate_flow_rate=500,
                                          dispense_flow_rate=1000)
    # difference value calculating
    current_vol = begin_vol
    diff = round(final_vol / (tube_amount - 1), 2)

    # text = 'Amount of needed tubes is {needed_tube}'.format(
    #     needed_tube=needed_tube
    # )
    # robot.comment(text)

    if begin_vol < calc_min_begin_vol(tube_amount, diff):
        robot.comment('Begin volume is too little. Pour more liquid into the falcon.')
        return

    # dispensing plasma A from 0 ul to final volume
    dispense_plasma(True, tube_amount, diff, final_vol, single50, single1000, plasma_falcon('A3'), tubes, current_vol)

    current_vol = begin_vol

    # tubes iteration from scratch
    tubes = [tubes1, tubes2, tubes3, tubes4]

    # tubes in racks iteration from scratch
    global current_rack
    current_rack = 0

    # dispensing plasma B from final volume to 0 ul
    dispense_plasma(False, tube_amount, diff, final_vol, single50, single1000, plasma_falcon('A4'), tubes, current_vol)

    print(tube_amount, 'dilutions prepared.')


last_rack = 0
current_rack = 0


# main method for dispening plasma
def dispense_plasma(is_increase, tube_amount, diff, final_vol, single50, single1000, source, tubes, current_vol):
    single50.pick_up_tip()
    single1000.pick_up_tip()

    counter_pipette = 0

    tubes_amount_in_rack = 35

    global last_rack
    last_rack = math.floor(tube_amount / tubes_amount_in_rack)

    for i in range(tube_amount):
        transfer_vol = round(final_vol - i * diff)

        used_pipette = which_pipette(transfer_vol, single50, single1000)

        check_if_tip_replace(used_pipette, counter_pipette)
        used_pipette.transfer(transfer_vol,
                              source_aspirating_height(current_vol, source),
                              destination(is_increase, tubes, i, tubes_amount_in_rack, tube_amount).top(-15),
                              new_tip='never')

        blow_outs(3, used_pipette)

        current_vol = current_vol - transfer_vol
        print(transfer_vol, ' ul of plasma added to tube ', i + 1)
        counter_pipette = counter_pipette + 1

    single50.drop_tip()
    single1000.drop_tip()


# checking if begin volume is enough for all dilutions
def calc_min_begin_vol(tube_amount, diff):
    calculated_min = 0
    for i in range(tube_amount):
        calculated_min = calculated_min + i * diff
    return calculated_min


# method for changing pipette tip for 5 pipetting cycles
def check_if_tip_replace(pipette, counter_pipette):
    if counter_pipette % 5 == 0 and counter_pipette != 0:
        print('pipette tips of ', pipette.name, 'changed')
        pipette.drop_tip()
        pipette.pick_up_tip()


# destination place iterating
def destination(is_increase, tubes, iteration, tubes_amount_in_rack, tube_amount):
    global current_rack
    global last_rack
    # tubes_amount_in_rack = 35
    if is_increase:
        if iteration % tubes_amount_in_rack == 0 and iteration != 0:
            current_rack = current_rack + 1
        return tubes[current_rack][iteration - (tubes_amount_in_rack * current_rack)]
    else:
        if (tube_amount - iteration) % 35 == 0 and iteration != 0:
            last_rack = last_rack - 1
        return tubes[last_rack][tube_amount - last_rack * tubes_amount_in_rack - iteration-1]


# the height of aspirating from falcon calculating
def source_aspirating_height(current_vol, source):
    if current_vol >= 5000:
        height = 0.0018 * current_vol - 118
        return source.top(height)
    else:
        return source.bottom(3)


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
