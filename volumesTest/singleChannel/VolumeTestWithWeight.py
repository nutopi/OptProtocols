from opentrons import labware, instruments, robot
from opentrons.data_storage import database


def volume_test(disp_vol, times, tube_on_weight):
    labware_list = labware.list()

    if labware_list.__contains__(tube_on_weight):
        database.delete_container(tube_on_weight)

    labware.create(tube_on_weight,
                   grid=(1, 1),
                   spacing=(0, 0),
                   diameter=10,
                   depth=30,
                   volume=200)

    weight_tube = labware.load(tube_on_weight, slot='5')
    trough_rack = labware.load('trough-12row', slot='11')
    tips300ul_rack1 = labware.load('tiprack-200ul', slot='10')

    single = instruments.P50_Single(mount='right',
                                    tip_racks=[tips300ul_rack1],
                                    aspirate_flow_rate=100,
                                    dispense_flow_rate=100)

    single.pick_up_tip()

    for i in range(times):
        curr_vol = single.current_volume
        if curr_vol < disp_vol:
            single.dispense(curr_vol, trough_rack(0))
            single.aspirate(single.max_volume, trough_rack(0))
            single.move_to(weight_tube(0))
            robot.pause()
        single.dispense(disp_vol, weight_tube(0))
        robot.pause()
        print('Read weight, then press Resume button, lol xD')

    single.dispense(single.current_volume, trough_rack(0))
    robot.home('z')


# ****************************************************************************************#

disp_vol1 = 10
times1 = 10
tube_type = 'tube_2ml_weight'
volume_test(disp_vol1, times1, tube_type)
