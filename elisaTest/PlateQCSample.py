from opentrons import labware, instruments, robot
import time

# labware
tip_rack1 = labware.load('opentrons-tiprack-300ul', slot='1')
clear_plate = labware.load("96-flat", slot='2')
trough_rack = labware.load('trough-12row', slot='3')
tip_rack2 = labware.load('opentrons-tiprack-300ul', slot='4')
white_plate = labware.load("96-flat", slot='5')
sample_falcon = labware.load('opentrons-tuberack-15_50ml', slot='6')
tip_rack3 = labware.load('opentrons-tiprack-300ul', slot='7')
tip_rack4 = labware.load('opentrons-tiprack-300ul', slot='8')
tip_rack5 = labware.load('opentrons-tiprack-300ul', slot='9')
tip_rack6 = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack7 = labware.load('opentrons-tiprack-300ul', slot='11')
# add exchaning sample_falcon slot 6 for tip_rack
tip_racks = [tip_rack1, tip_rack2, tip_rack3, tip_rack4, tip_rack5, tip_rack6, tip_rack7]

# pipettes
single = instruments.P50_Sigle(mount='right',
                               tip_racks=[tip_rack1, tip_rack2, tip_rack3, tip_rack4, tip_rack5, tip_rack6, tip_rack7])

multi = instruments.P300_Multi(mount='left',
                               tip_racks=[tip_rack1, tip_rack2, tip_rack3, tip_rack4, tip_rack5, tip_rack6, tip_rack7])


# pipettes volume ranges:
# single: 5ul - 50ul
# multi: 30ul - 300ul

# sample dispensing
def sample_dispensing(sample_vol, wells_number):
    for i in range(column):
        single.pick_up_tip()
        for j in range(row):
            curr_vol = single.current_volume
            if curr_vol < sample_vol:
                single.dispense(curr_vol, sample_falcon('C1'))
                single.aspirate(single.max_volume, sample_falcon('C1'))
            single.dispense(sample_vol, white_plate.cols(xxxxx))
            # to trzeba ogarnac
        # print(sample_vol, ' ul poured into the ', column, ' white plate well.')
    single.drop_tip()


# stop for pouring Dilution Buffer and Conjugate into the first row of trough
robot.pause()
print(
    'Press RESUME button if dilution of Dilution Buffer and Conjugate are poured into the first column of trough on the 3rd slot.')


# conjugate adding
def conjugate_transfering(conj_vol):
    multi.pick_up_tip()
    for i in range(6):
        multi.aspirate(conj_vol, trough_rack(0))
        multi.dispense(conj_vol, white_plate.cols(i * 2))
        multi.blow_out(white_plate.cols(1 * 2))
        print(conj_vol, ' ul of conjugate dispensed into the ', i + 1, ' column of white plate.')
    multi.drop_tip()


# from white plate to clear plate dispensing
def white_to_clear():
    for i in range(6):
        multi.pick_up_tip()
        multi.mix(4, 100, white_plate.cols(i * 2))
        # mix(repetitions, volume, location)
        multi.aspirate(multi.max_volume, white_plate.cols(i * 2))
        for j in range(11):
            multi.dispense(100, clear_plate.cols[j:j + 2:1])
            # clear_plate.cols[0:11:2] means: every second column from 0th to 11th column
        multi.drop_tip()


# stop for sealing tape sticking and for 1-hour incubation
robot.pause()
print('Press RESUME to start 1-hour incubation.')
time.sleep(60 * 60)
# print('Time remaining: ', 3600-time.process_time()) ???

# washing step
def washing():
    # aspirating
    for i in range(11):
        multi.pick_up_tip()
        multi.aspirate(multi.max_volume, clear_plate.cols(i))
        multi.drop_tip()
    # washing
    for i in range(wash_number):
        multi.pick_up_tip()
        for j in range(11):
            multi.aspirate(250, trough_rack(xxxxx))
            #trough_rack(xxxxx) - to jest do rozwiazania
            multi.dispense(250, clear_plate.cols(j))
        multi.drop_tip()
        for k in range(11):
            multi.pick_up_tip()
            multi.aspirate(multi.max_volume, clear_plate.cols(k))
            multi.drop_tip()
        print(i, 'wash cycle finished.')

# stop for checking air bubbles
robot.pause()
print('Take the clear plate out and check if there is no air bubbles in the wells. Pour TMB into the last column of trough on the 3rd slot. Then press RESUME button.')


#TMB adding
def TMB_dispensing():
    multi.pick_up_tip()
    for i in range(11):
        multi.aspirate(multi.max_volume, trough_rack(11))
        multi.dispense(100, clear_plate.cols[i:i + 2:1])
    multi.drop_tip()

# stop for 20min incubation, for sealing tape sticking and unsticking
robot.pause()
time.sleep(20*60)
# print('Time remaining: ', 20*60-time.process_time()) ???

#Stop Solution adding
def stopping():
    multi.pick_up_tip()
    for i in range(11):
        multi.aspirate(multi.max_volume, trough_rack(2))
        multi.dispense(100, clear_plate.cols[i:i + 2:1])
    multi.drop_tip()

print('ELISA with 100% Plate QC Sample in duplicates way finished. Congratulations!')
# ******************************************************* #
sample_vol = 25
wells_number = 96
conj_vol = 225
wash_number = 5
