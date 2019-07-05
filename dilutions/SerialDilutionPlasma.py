from opentrons import labware, instruments, robot


def serial_dil(begin_vol, final_vol, tube_amount):
    #TODO make a condition to check
    #begin_vol > final_vol * tube_amount

    labware_list = labware.list()

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
    diff = round(final_vol / tube_amount)

    # dispensing plasma A from 0 ul to final volume
    single50.pick_up_tip()
    single1000.pick_up_tip()

    for i in range(tube_amount):
        current_tube = i + 1
        if current_vol >= 5000:
            height = 1.8 * current_vol - 109
            if i * diff < 100:
                single50.transfer(i * diff, plasma_falcon('A3').top(height), tubes)
                current_vol = current_vol - i * diff
                # print('current volume of plasma A: ', current_vol)
                print(i * diff, ' ul of plasma A added to tube ', current_tube)
            else:
                single1000.transfer(i * diff, plasma_falcon('A3').top(height), tubes)
                current_vol = current_vol - i * diff
                # print('current volume of plasma A: ', current_vol)
                print(i * diff, ' ul of plasma A added to tube ', current_tube)
        else:
            if i * diff < 100:
                single50.transfer(i * diff, plasma_falcon('A3').bottom(3), tubes)
                current_vol = current_vol - i * diff
                # print('current volume of plasma A: ', current_vol)
                print(i * diff, ' ul of plasma A added to tube ', current_tube)
            else:
                single1000.transfer(i * diff, plasma_falcon('A3').bottom(3), tubes)
                current_vol = current_vol - i * diff
                # print('current volume of plasma A: ', current_vol)
                print(i * diff, ' ul of plasma A added to tube ', current_tube)

    current_vol = begin_vol

    # tubes iteration from scratch
    tubes = [tubes1, tubes2, tubes3, tubes4]

    # dispensing plasma B from final volume to 0 ul
    single50.pick_up_tip()
    single1000.pick_up_tip()

    for i in range(tube_amount):
        current_tube = i + 1
        if current_vol >= 5000:
            height = 1.8 * current_vol - 109
            if final_vol - i * diff < 100:
                single50.transfer(final_vol - i * diff, plasma_falcon('A4').top(height), tubes)
                current_vol = current_vol - (final_vol - i * diff)
                # print('current volume of plasma B: ', current_vol)
                print(final_vol - i * diff, ' ul of plasma B added to tube ', current_tube)
            else:
                single1000.transfer(final_vol - i * diff, plasma_falcon('A4').top(height), tubes)
                current_vol = current_vol - (final_vol - i * diff)
                # print('current volume of plasma B: ', current_vol)
                print(final_vol - i * diff, ' ul of plasma B added to tube ', current_tube)

        else:
            if final_vol - i * diff < 100:
                single50.transfer(final_vol - i * diff, plasma_falcon('A4').bottom(3), tubes)
                current_vol = current_vol - (final_vol - i * diff)
                # print('current volume of plasma B: ', current_vol)
                print(final_vol - i * diff, ' ul of plasma B added to tube ', current_tube)
            else:
                single1000.transfer(final_vol - i * diff, plasma_falcon('A4').bottom(3), tubes)
                current_vol = current_vol - (final_vol - i * diff)
                # print('current volume of plasma B: ', current_vol)
                print(final_vol - i * diff, ' ul of plasma B added to tube ', current_tube)

    print(tube_amount, 'dilutions prepared.')


# ****************************************************************************************#

# wywolanie funkcji
begin_vol1 = 30000
final_vol1 = 600
tube_amount1 = 35
#diff = round(final_vol1 / tube_amount1)
serial_dil(begin_vol1, final_vol1, tube_amount1)
