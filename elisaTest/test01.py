from opentrons import labware, instruments, robot

white_plate = labware.load('96-flat', slot='10')
clear_plate = labware.load('96-flat', slot='11')
trough_rack = labware.load('trough-12row', slot='8')
stds_tubes = labware.load('tube-rack-2ml', slot='7')
tips300ul_rack1 = labware.load('opentrons-tiprack-300ul', slot='4')
tips300ul_rack2 = labware.load('opentrons-tiprack-300ul', slot='5')
trash = labware.load('trash-box', slot='12')
# trash = labware.load('trash-box', '12')
# singlets way test

single = instruments.P50_Single(mount='left',
                                tip_racks=[tips300ul_rack1, tips300ul_rack2],
                                trash_container=trash,
                                aspirate_flow_rate=100,
                                dispense_flow_rate=100)

multi = instruments.P300_Multi(mount='left',
                               tip_racks=[tips300ul_rack1, tips300ul_rack2],
                               trash_container=trash,
                               aspirate_flow_rate=100,
                               dispense_flow_rate=100)

for i in range(7):
    single.distribute(25, stds_tubes(i), white_plate(i))
    single.drop_tip()

single.distribute(25, trough_rack(0), white_plate('H1'))

for i in range(16, 96):
    multi.distribute(trough_rack(0), white_plate(i))
    if i % 8 == 0:
        if (i / 8 + 1) % 2 == 0:
            i = i + 8
