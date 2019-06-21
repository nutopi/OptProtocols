from opentrons import labware, instruments, robot

def serial_dil(diff, final_vol, tube_amount):
    labware_list = labware.list()

# creates custom labware if currently not created
    if tube_2ml_rack_35 not in labware.list():
        tube_2ml_rack_35 = labware.create("tube_2ml_rack_35",
                                          grid=(7,5),
                                          spacing=(16.25, 14.56),
                                          diameter=10,
                                          depth=30)

    2ml_tubes1 = labware.load('tube_2ml_rack_35', slot='1)
    2ml_tubes2 = labware.load('tube_2ml_rack_35', slot='2)
    2ml_tubes3 = labware.load('tube_2ml_rack_35', slot='3)
    tip_rack_small = labware.load('opentrons-tiprack-300ul', slot='4)
    #TODO: check the big tip rack
    tip_rack_big = labware.load('tiprack-1000ul', slot='5')
    plasma_falcon = labware.load('opentrons-tuberack-15_50ml', slot='6')

    single50 = instruments.P50_Single(mount='right',
                                    tip_racks=tip_rack_small,
                                    aspirate_flow_rate=100,
                                    dispense_flow_rate=100)

    single1000 = instruments.P1000_Single(mount='left',
                                      tip_racks=tip_rack_big,
                                      aspirate_flow_rate=100,
                                      dispense_flow_rate=100)

    #    for i in range(times):
    #     curr_vol = single.current_volume
    #     if curr_vol < disp_vol:
    #         single.dispense(curr_vol, trough_rack(0))
    #         single.aspirate(single.max_volume, trough_rack(0))
    #         single.move_to(weight_tube(0))
    #         robot.pause()
    #     single.dispense(disp_vol, weight_tube(0))
    #     robot.pause()
    #     print('Read weight, then press Resume button, lol xD')
    #
    # single.dispense(single.current_volume, trough_rack(0))
    # robot.home('z')


# ****************************************************************************************#

#wywolanie funkcji
tube_amount = round(final_vol/diff)