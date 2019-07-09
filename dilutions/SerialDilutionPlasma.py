from opentrons import labware, instruments, robot
import math

robot.clear_commands()

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
                                          aspirate_flow_rate=100,
                                          dispense_flow_rate=100)

    current_vol = begin_vol
    diff = math.floor(final_vol / (tube_amount - 1))

    # calculating of real tube amount by rounding up
    needed_tube = math.ceil(final_vol / diff)

    #robot.comment(needed_tube, 'tubes is needed.')
    print(robot.comment('tubes is needed.'))

    # for c in robot.commands():
    #     print(c)

    if begin_vol < calc_min_begin_vol(needed_tube, diff):
        print('Begin volume is too little. Pour more liquid into the falcon.')
        return

    # dispensing plasma A from 0 ul to final volume
    dispense_plasma(True, needed_tube, diff, final_vol, single50, single1000, plasma_falcon('A3'), tubes, current_vol)

    current_vol = begin_vol

    # tubes iteration from scratch
    tubes = [tubes1, tubes2, tubes3, tubes4]

    # dispensing plasma B from final volume to 0 ul
    dispense_plasma(False, needed_tube, diff, final_vol, single50, single1000, plasma_falcon('A4'), tubes, current_vol)

    print(needed_tube, 'dilutions prepared.')


def dispense_plasma(is_increase, needed_tube, diff, final_vol, single50, single1000, source, tubes, current_vol):
    single50.pick_up_tip()
    single1000.pick_up_tip()

    counter_single50 = 0
    counter_single1000 = 0

    for i in range(needed_tube):
        current_tube = i + 1
        transfer_vol = calc_transfer_vol(is_increase, final_vol, diff, i)
        if current_vol >= 5000:
            height = 0.0018 * current_vol - 118
            if transfer_vol < 100:
                check_if_tip_replace(single50, counter_single50)
                single50.transfer(transfer_vol, source.top(height), which_well_dest(tubes, i).top(-15), new_tip='never', blow_out=True)
                single50.blow_out()
                single50.blow_out()
                current_vol = current_vol - transfer_vol
                # print('current volume of plasma A: ', current_vol)
                print(transfer_vol, ' ul of plasma added to tube ', current_tube)
                counter_single50 = counter_single50 + 1
            else:
                check_if_tip_replace(single1000, counter_single1000)
                single1000.transfer(transfer_vol, source.top(height), which_well_dest(tubes, i).top(-15), new_tip='never', blow_out=True)
                single1000.blow_out()
                single1000.blow_out()
                current_vol = current_vol - transfer_vol
                # print('current volume of plasma A: ', current_vol)
                print(transfer_vol, ' ul of plasma added to tube ', current_tube)
                counter_single1000 = counter_single1000 + 1
        else:
            if transfer_vol < 100:
                check_if_tip_replace(single50, counter_single50)
                single50.transfer(transfer_vol, source.bottom(3), which_well_dest(tubes, i).top(-15), new_tip='never', blow_out=True)
                single50.blow_out()
                single50.blow_out()
                current_vol = current_vol - transfer_vol
                # print('current volume of plasma A: ', current_vol)
                print(transfer_vol, ' ul of plasma added to tube ', current_tube)
                counter_single50 = counter_single50 + 1

            else:
                check_if_tip_replace(single1000, counter_single1000)
                single1000.transfer(transfer_vol, source.bottom(3), which_well_dest(tubes, i).top(-15), new_tip='never', blow_out=True)
                single1000.blow_out()
                single1000.blow_out()
                current_vol = current_vol - transfer_vol
                # print('current volume of plasma A: ', current_vol)
                print(transfer_vol, ' ul of plasma added to tube ', current_tube)
                counter_single1000 = counter_single1000 + 1

    single50.drop_tip()
    single1000.drop_tip()


def calc_transfer_vol(is_increase, final_vol, diff, iteration):
    if is_increase:
        return iteration * diff
    else:
        return final_vol - iteration * diff


def calc_min_begin_vol(needed_tube, diff):
    calculated_min = 0
    for i in range(needed_tube):
        calculated_min = calculated_min + i * diff
    return calculated_min


# method for changing pipette tip for 5 pipetting cycles
def check_if_tip_replace(pipette, counter_pipette):
    if counter_pipette % 5 == 0 and counter_pipette != 0:
        pipette.drop_tip()
        pipette.pick_up_tip()


# destination place iterating
def which_well_dest(tubes, iteration):
    tubes_amount_in_rack = 35
    if iteration < tubes_amount_in_rack:
        return tubes[0][iteration]
    elif (iteration >= tubes_amount_in_rack) and (iteration < tubes_amount_in_rack * 2):
        return tubes[1][iteration - tubes_amount_in_rack]
    elif (iteration >= tubes_amount_in_rack * 2) and (iteration < tubes_amount_in_rack * 3):
        return tubes[2][iteration - (tubes_amount_in_rack * 2)]
    elif (iteration >= tubes_amount_in_rack * 3) and (iteration < tubes_amount_in_rack * 4):
        return tubes[3][iteration - (tubes_amount_in_rack * 3)]

# ****************************************************************************************#

# invoke method
begin_vol1 = 20000
final_vol1 = 600
tube_amount1 = 10
serial_dil(begin_vol1, final_vol1, tube_amount1)
