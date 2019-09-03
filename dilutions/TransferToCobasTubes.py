from opentrons import labware, instruments, robot

# creates custom labware if currently not created
tube_rack_35 = "tube_rack_35"
if tube_rack_35 not in labware.list():
    tube_rack_35 = labware.create("tube_rack_35",
                                  grid=(7, 5),
                                  spacing=(16.25, 14.56),
                                  diameter=10,
                                  depth=41)

dest_tube_rack_A = labware.load('tube_rack_35', slot='4')
dest_tube_rack_B = labware.load('tube_rack_35', slot='5')
dest_tube_rack_C = labware.load('tube_rack_35', slot='6')
dest_tube_rack_D = labware.load('tube_rack_35', slot='1')
dest_tube_rack_E = labware.load('tube_rack_35', slot='2')
dest_tube_rack_F = labware.load('tube_rack_35', slot='3')
source_tube_rack_A = labware.load('tube_rack_35', slot='7')
source_tube_rack_B = labware.load('tube_rack_35', slot='8')
source_tube_rack_C = labware.load('tube_rack_35', slot='9')
tip_rack_small_A = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack_small_B = labware.load('opentrons-tiprack-300ul', slot='11')

dest_tube_racks_array = [dest_tube_rack_A, dest_tube_rack_B, dest_tube_rack_C, dest_tube_rack_D, dest_tube_rack_E,
                         dest_tube_rack_F]
source_tube_racks_array = [source_tube_rack_A, source_tube_rack_B, source_tube_rack_C]

single50 = instruments.P50_Single(mount='right',
                                  tip_racks=[tip_rack_small_A, tip_rack_small_B],
                                  aspirate_flow_rate=50,
                                  dispense_flow_rate=100)

global source_current_rack
source_current_rack = 0

global dest_current_rack
dest_current_rack = 0


# main method for transferring the samples from source to destination
def transfer_to_cobas_tubes(transfer_vol):
    j = 0
    for i in range(105):
        source = which_source_tube(source_tube_racks_array, i)
        destination = which_dest_tube(dest_tube_racks_array, j)
        liquid_transfer(single50, transfer_vol, source, destination)
        print('Sample transferred from ', source, ' to ', destination, '\n')
        j = j + 2
        if (j - 1) % 35 == 0:
            j = j - 1


# selecting proper source tube rack
def which_source_tube(source_tube_racks_array, iteration):
    global source_current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        source_current_rack = source_current_rack + 1
    return source_tube_racks_array[source_current_rack][iteration - (tubes_amount_in_rack * source_current_rack)]


# selecting proper destination tube rack
def which_dest_tube(dest_tube_racks_array, iteration):
    global dest_current_rack
    tubes_amount_in_rack = 35
    if iteration % tubes_amount_in_rack == 0 and iteration != 0:
        dest_current_rack = dest_current_rack + 1
    return dest_tube_racks_array[dest_current_rack][iteration - (tubes_amount_in_rack * dest_current_rack)]


# custom method for transferring the liquid
def liquid_transfer(used_pipette, transfer_vol, source, destination):
    used_pipette.pick_up_tip()
    if (transfer_vol > 0) and (transfer_vol <= 50):
        used_pipette.aspirate(transfer_vol, source.bottom(5))
        used_pipette.dispense(used_pipette.current_volume, destination)

    elif (transfer_vol > 50) and (transfer_vol <= 100):
        for i in range(2):
            used_pipette.aspirate(transfer_vol / 2, source.bottom(5))
            used_pipette.dispense(used_pipette.current_volume, destination)

    elif (transfer_vol > 100) and (transfer_vol <= 150):
        for i in range(3):
            used_pipette.aspirate(transfer_vol / 3, source.bottom(5))
            used_pipette.dispense(used_pipette.current_volume, destination)

    blow_outs(2, used_pipette)
    used_pipette.drop_tip()


# how much blow_outs is supposed to be performed
def blow_outs(times, pipette):
    for i in range(times):
        pipette.blow_out()


# ****************************************************************************************#

# invoke method
transfer_vol_invoke = 100

transfer_to_cobas_tubes(transfer_vol_invoke)
