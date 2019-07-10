from opentrons import labware, instruments, robot


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


def dispense_plasma(is_increase, tube_amount, diff, final_vol, single50, single1000, source, tubes, current_vol):
    single50.pick_up_tip()
    single1000.pick_up_tip()

    for i in range(tube_amount):
        current_tube = i + 1
        transfer_vol = calc_transfer_vol(is_increase, final_vol, diff, i)

        counter_pipette = 0

        check_if_tip_replace(which_pipette(transfer_vol, single50, single1000), counter_pipette)
        which_pipette(transfer_vol, single50, single1000).transfer(transfer_vol,
                                                                   source_aspirating_height(current_vol, source),
                                                                   which_well_dest(tubes, i).top(-15), new_tip='never')
        for b in range(3):
            which_pipette(transfer_vol, single50, single1000).blow_out()

        current_vol = current_vol - transfer_vol
        print(transfer_vol, ' ul of plasma added to tube ', current_tube)
        counter_pipette = counter_pipette + 1

    # counter_single50 = 0
    # counter_single1000 = 0

    # for i in range(tube_amount):
    #     current_tube = i + 1
    #     transfer_vol = calc_transfer_vol(is_increase, final_vol, diff, i)
    #     if current_vol >= 5000:
    #         height = 0.0018 * current_vol - 118
    #         if transfer_vol < 100:
    #             check_if_tip_replace(single50, counter_single50)
    #             single50.transfer(transfer_vol, source.top(height), which_well_dest(tubes, i).top(-15), new_tip='never',
    #                               blow_out=True)
    #             single50.blow_out()
    #             single50.blow_out()
    #             single50.blow_out()
    #             current_vol = current_vol - transfer_vol
    #             print(transfer_vol, ' ul of plasma added to tube ', current_tube)
    #             counter_single50 = counter_single50 + 1
    #         else:
    #             check_if_tip_replace(single1000, counter_single1000)
    #             single1000.transfer(transfer_vol, source.top(height), which_well_dest(tubes, i).top(-15),
    #                                 new_tip='never', blow_out=True)
    #             single1000.blow_out()
    #             single1000.blow_out()
    #             single1000.blow_out()
    #             current_vol = current_vol - transfer_vol
    #             print(transfer_vol, ' ul of plasma added to tube ', current_tube)
    #             counter_single1000 = counter_single1000 + 1
    #     else:
    #         if transfer_vol < 100:
    #             check_if_tip_replace(single50, counter_single50)
    #             single50.transfer(transfer_vol, source.bottom(3), which_well_dest(tubes, i).top(-15), new_tip='never',
    #                               blow_out=True)
    #             single50.blow_out()
    #             single50.blow_out()
    #             single50.blow_out()
    #             current_vol = current_vol - transfer_vol
    #             print(transfer_vol, ' ul of plasma added to tube ', current_tube)
    #             counter_single50 = counter_single50 + 1
    #
    #         else:
    #             check_if_tip_replace(single1000, counter_single1000)
    #             single1000.transfer(transfer_vol, source.bottom(3), which_well_dest(tubes, i).top(-15), new_tip='never',
    #                                 blow_out=True)
    #             single1000.blow_out()
    #             single1000.blow_out()
    #             single1000.blow_out()
    #             current_vol = current_vol - transfer_vol
    #             print(transfer_vol, ' ul of plasma added to tube ', current_tube)
    #             counter_single1000 = counter_single1000 + 1

    single50.drop_tip()
    single1000.drop_tip()


def calc_transfer_vol(is_increase, final_vol, diff, iteration):
    if is_increase:
        return round(iteration * diff)
    else:
        return round(final_vol - iteration * diff)


def calc_min_begin_vol(tube_amount, diff):
    calculated_min = 0
    for i in range(tube_amount):
        calculated_min = calculated_min + i * diff
    return calculated_min


# method for changing pipette tip for 5 pipetting cycles
def check_if_tip_replace(pipette, counter_pipette):
    if counter_pipette % 5 == 0 and counter_pipette != 0:
        pipette.drop_tip()
        pipette.pick_up_tip()


current_rack = 0


# destination place iterating
def which_well_dest(tubes, iteration):
    global current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        current_rack = current_rack + 1

    return tubes[current_rack][iteration - (tubes_amount_in_rack * current_rack)]


def source_aspirating_height(current_vol, source):
    if current_vol >= 5000:
        height = 0.0018 * current_vol - 118
        return source.top(height)
    else:
        return source.bottom(3)


def which_pipette(transfer_vol, single50, single1000):
    if transfer_vol < 100:
        return single50
    else:
        return single1000


# ****************************************************************************************#

# invoke method
begin_vol1 = 40000
final_vol1 = 600
tube_amount1 = 10
serial_dil(begin_vol1, final_vol1, tube_amount1)
