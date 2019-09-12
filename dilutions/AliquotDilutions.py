from opentrons import labware, instruments, robot

current_rack = 0
first_rack = 0
last_rack = 2


def aliquot_dil(transfer_vol):
    # creates custom labware if currently not created
    tube_rack_35 = "tube_rack_35"
    if tube_rack_35 not in labware.list():
        tube_rack_35 = labware.create("tube_rack_35",
                                      grid=(7, 5),
                                      spacing=(16.25, 14.56),
                                      diameter=10,
                                      depth=41)

    # labware placement
    source_tubes_a = labware.load('tube_rack_35', slot='1')
    source_tubes_b = labware.load('tube_rack_35', slot='2')
    source_tubes_c = labware.load('tube_rack_35', slot='3')
    source_tubes_array = [source_tubes_a, source_tubes_b, source_tubes_c]

    dest_tubes_reverse_a = labware.load('tube_rack_35', slot='4')
    dest_tubes_reverse_b = labware.load('tube_rack_35', slot='5')
    dest_tubes_reverse_c = labware.load('tube_rack_35', slot='6')
    dest_tubes_reverse = [dest_tubes_reverse_a, dest_tubes_reverse_b, dest_tubes_reverse_c]

    dest_tubes_normal_a = labware.load('tube_rack_35', slot='7')
    dest_tubes_normal_b = labware.load('tube_rack_35', slot='8')
    dest_tubes_normal_c = labware.load('tube_rack_35', slot='9')
    dest_tubes_normal = [dest_tubes_normal_a, dest_tubes_normal_b, dest_tubes_normal_c]

    tip_rack_big_a = labware.load('tiprack-1000ul', slot='10')
    tip_rack_big_b = labware.load('tiprack-1000ul', slot='11')

    # pipette definition
    single1000 = instruments.P1000_Single(mount='left',
                                          tip_racks=[tip_rack_big_a, tip_rack_big_b],
                                          aspirate_flow_rate=1000,
                                          dispense_flow_rate=1500)
    global current_rack
    current_rack = 0

    for i in range(105):
        single1000.pick_up_tip()

        source_tube = which_source_tube(i, source_tubes_array)
        single1000.mix(8, 250, source_tube, 4.0)

        destination_tube = which_destination_tube(True, dest_tubes_reverse, dest_tubes_normal, i).top(-20)
        transfer(single1000, transfer_vol, source_tube, destination_tube)

        destination_tube = which_destination_tube(False, dest_tubes_reverse, dest_tubes_normal, i).top(-38)
        transfer(single1000, transfer_vol, source_tube, destination_tube)

        single1000.drop_tip()

        # Pause for waste remove
        if i == 52:
            robot.pause()
            robot.comment(
                'Remove the waste from the trash bin.'
                '\nThen select RESUME and the protocol will be executed further.')


def transfer(pipette, transfer_vol, source_tube, dest_tube):
    pipette.transfer(transfer_vol,
                     source_tube,
                     dest_tube,
                     new_tip='never', blow_out=True)
    blow_outs(2, pipette)


# source tubes iterating
def which_source_tube(iteration, source_tubes):
    global current_rack
    if iteration % 35 == 0 and iteration != 0:
        current_rack = current_rack + 1
    current_tube = source_tubes[current_rack][iteration - (35 * current_rack)]
    print('\nSOURCE:', current_tube, '\tsource rack:', current_rack)
    return source_tubes[current_rack][iteration - (35 * current_rack)]


# destination place iterating
def which_destination_tube(is_increase, dest_tubes_reverse, dest_tubes_normal, iteration):
    global first_rack
    global last_rack
    if is_increase:
        if iteration % 35 == 0 and iteration != 0:
            first_rack = first_rack + 1
        dest_tube_norm = dest_tubes_normal[first_rack][iteration - (35 * first_rack)]
        print('DEST NORMAL:', dest_tube_norm, '\tdest rack:', first_rack)
        return dest_tubes_normal[first_rack][iteration - (35 * first_rack)]
    else:
        if (105 - iteration) % 35 == 0 and iteration != 0:
            last_rack = last_rack - 1
        dest_tube_rev = dest_tubes_reverse[last_rack][105 - last_rack * 35 - iteration - 1]
        print('DEST REVERSE:', dest_tube_rev, '\tdest rack:', last_rack, '\n***************************************')
        return dest_tubes_reverse[last_rack][105 - last_rack * 35 - iteration - 1]


def blow_outs(times, pipette):
    for i in range(times):
        pipette.blow_out()


# ********************************************************************************* #
# invoke method
transfer_vol_a = 200
aliquot_dil(transfer_vol_a)
