from opentrons import labware, instruments, robot
import time

#creates custom labware if currently not created
custom_tube="tube_on_weight"
if custom_tube not in labware.list():
    labware_with_weight = labware.create("tube_on_weight",
         grid=(1, 1),
         spacing=(0, 0),
         diameter=10,
         depth=30,
         volume=2000)

weight_tube = labware.load("tube_on_weight", slot='5')
trough_rack = labware.load('trough-12row', slot='11')
tips300ul_rack1 = labware.load('opentrons-tiprack-300ul', slot='10')

single = instruments.P50_Single(mount='right',
                                tip_racks=[tips300ul_rack1],
                                aspirate_flow_rate=100,
                                dispense_flow_rate=100)

single.pick_up_tip()


def volume_test(disp_vol, times):
    for i in range(times):
        curr_vol = single.current_volume
        if curr_vol < disp_vol:
            single.dispense(curr_vol, trough_rack(6))
            single.aspirate(disp_vol, trough_rack(6))
            single.move_to(weight_tube(0))
        single.dispense(disp_vol, weight_tube(0))
        single.blow_out(weight_tube(0))
        single.blow_out(weight_tube(0))
        robot.pause()
        print('Read weight, then press Resume button, lol xD')

    single.dispense(single.current_volume, trough_rack(6))
    robot.home()
    #database.delete_container('tube_2ml_weightB')


# ****************************************************************************************#

disp_vol1 = 20
times1 = 10
# tube_type = 'tube_2ml_weight'
volume_test(disp_vol1, times1)
