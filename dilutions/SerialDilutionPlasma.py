from opentrons import labware, instruments, robot


def serial_dil(diff, final_vol, tube_amount, begin_vol):
    labware_list = labware.list()

    # creates custom labware if currently not created
    if tube_2ml_rack_35 not in labware.list():
        tube_2ml_rack_35 = labware.create("tube_2ml_rack_35",
                                          grid=(7, 5),
                                          spacing=(16.25, 14.56),
                                          diameter=10,
                                          depth=30)

    tubes1 = labware.load('tube_2ml_rack_35', slot='1)
    tubes2 = labware.load('tube_2ml_rack_35', slot='2)
    tubes3 = labware.load('tube_2ml_rack_35', slot='3)
    tip_rack_small = labware.load('opentrons-tiprack-300ul', slot='4)
    tip_rack_big = labware.load('tiprack-1000ul', slot='5')
    plasma_falcon = labware.load('opentrons-tuberack-15_50ml', slot='6')

    tubes=[tubes1, tubes2, tubes3]

    single50 = instruments.P50_Single(mount='right',
                                      tip_racks=tip_rack_small,
                                      aspirate_flow_rate=100,
                                      dispense_flow_rate=100)

    single1000 = instruments.P1000_Single(mount='left',
                                          tip_racks=tip_rack_big,
                                          aspirate_flow_rate=100,
                                          dispense_flow_rate=100)

    current_vol = begin_vol

    # dispensing plasma A from 0 ul to final volume
    for i in range(tube_amount):
        if current_vol>=5:
            height = 1.8 * current_vol - 105
            if i * diff < 100:
                single50.transfer(i*diff, plasma_falcon('A3').top(height), tubes)
                current_vol=current_vol-i*diff
            else:
                single1000.transfer(i*diff, plasma_falcon('A3').top(height), tubes)
                current_vol = current_vol - i * diff
        else:
            if i * diff < 100:
                single50.transfer(i * diff, plasma_falcon('A3').bottom(3), tubes)
                current_vol = current_vol - i * diff
            else:
                single1000.transfer(i * diff, plasma_falcon('A3').bottom(3), tubes)
                current_vol = current_vol - i * diff

    current_vol = begin_vol

    # tubes iteration from scratch
    tubes=[tubes1, tubes2, tubes3]

    # dispensing plasma B from final volume to 0 ul
    for i in range(tube_amount):
        if current_vol>=5:
            height = 1.8*current_vol-105
            if final_vol-i*diff<100:
                single50.transfer(final_vol-i*diff, plasma_falcon('A4').top(height), tubes))
                current_vol=current_vol-(final_vol-i*diff)
            else:
                single1000.transfer(final_vol-i*diff, plasma_falcon('A4').top(height), tubes)
                current_vol = current_vol - (final_vol-i*diff)

        else:
            if final_vol-i * diff < 100:
                single50.transfer(final_vol-i * diff, plasma_falcon('A4').bottom(3), tubes)
                current_vol = current_vol - (final_vol-i * diff)
            else:
                single1000.transfer(final_vol-i * diff, plasma_falcon('A4').bottom(3), tubes)
                current_vol = current_vol - (final_vol-i * diff)


    # ****************************************************************************************#

    # wywolanie funkcji
        tube_amount = round(final_vol / diff)
