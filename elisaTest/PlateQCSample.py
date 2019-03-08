from threading import Thread

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
single = instruments.P50_Single(mount='right',
                                tip_racks=tip_racks)

multi = instruments.P300_Multi(mount='left',
                               tip_racks=tip_racks)


# pipettes volume ranges:
# single: 5ul - 50ul
# multi: 30ul - 300ul

# sample dispensing
def sample_dispensing(sample_vol):
    single.pick_up_tip()
    i = 0
    while (i < 96):
        curr_vol = single.current_volume
        if curr_vol < sample_vol:
            single.dispense(curr_vol, sample_falcon('C1'))
            single.blow_out(sample_falcon('C1'))
            single.aspirate(single.max_volume, sample_falcon('C1'))
        single.dispense(sample_vol, white_plate(i))
        i += 1
        if i % 8 == 0:
            i = i + 8
    single.drop_tip()


# conjugate adding
def conjugate_transfering(conj_vol):
    multi.start_at_tip(tip_rack1.cols(1))
    multi.pick_up_tip()
    for i in range(0, 12, 2):
        multi.aspirate(conj_vol, trough_rack(0))
        multi.dispense(conj_vol, white_plate.cols(i))
        multi.blow_out(white_plate.cols(i))
        print(conj_vol, ' ul of conjugate added into the ', i + 1, ' column of white plate.')
    multi.drop_tip()


# from white plate to clear plate dispensing
def white_to_clear():
    for i in range(0, 12, 2):
        multi.pick_up_tip()
        # mix(repetitions, volume, location)
        multi.mix(4, 100, white_plate.cols(i))
        multi.aspirate(200, white_plate.cols(i))
        for j in range(i, i + 1):
            multi.dispense(100, clear_plate.cols(j))
        multi.drop_tip()


# washing step
def waste():
    for i in range(11):
        multi.pick_up_tip()
        multi.aspirate(200, clear_plate.cols(i))
        multi.drop_tip()


# washing
def washing(wash_number):
    for i in range(wash_number):
        multi.pick_up_tip()
        for j in range(11):
            multi.aspirate(250, WB_container)
            multi.dispense(250, clear_plate.cols(j))
        multi.drop_tip()
        for j in range(11):
            multi.pick_up_tip()
            multi.aspirate(250, clear_plate.cols(j))
            multi.dispense(250, robot.fixed_trash)
            multi.aspirate(250, clear_plate.cols(j))
            multi.drop_tip()
        print(i + 1, ' wash cycle finished.')


# TMB adding
def TMB_dispensing():
    multi.pick_up_tip()
    for i in range(0, 11, 2):
        multi.aspirate(200, trough_rack(11))
        for j in range(i, i + 2):
            multi.dispense(100, clear_plate.cols(j))
    multi.drop_tip()


# Stop Solution adding
def stopping():
    multi.pick_up_tip()
    for i in range(0, 11, 2):
        multi.aspirate(200, trough_rack(2))
        for j in range(i, i + 2):
            multi.dispense(100, clear_plate.cols(j))
    multi.drop_tip()


# ******************************************************* #
sample_volA = 25
conj_volA = 225
wash_numberA = 5

sample_dispensing(sample_volA)

# stop for pouring Dilution Buffer and Conjugate into the first row of trough
robot.pause()
# TODO print for user
print(
    'Press RESUME button if dilution of Dilution Buffer and Conjugate '
    'is poured into the first column of trough on the 3rd slot.')

conjugate_transfering(conj_volA)
white_to_clear()

print('Take out the clear plate, stick sealing tape on it and hide under styro-box.'
      'Then press RESUME to start count down of 1h incubation')
robot.pause()

# TODO
print('Change empty tip racks for new ones.'
      'Take out white plate (5th slot).'
      'Take out rack with 15ml falcon with PLATE QC Sample (6th slot).'
      'Put a container with washing buffer on the 6th slot.')
# stop for sealing tape sticking and for 1-hour incubation
multi.reset()
WB_container = labware.load('trash-box', slot='5', share=True)

# TODO print('Time remaining: ', 3600-time.process_time()) ???
time.sleep(60 * 60)

waste()
washing(wash_numberA)

# stop for checking air bubbles
print(
    'Take the clear plate out and check if there is no air bubbles in the wells. '
    'Pour TMB into the last column of trough on the 3rd slot. '
    'Then press RESUME button.')
robot.pause()

thread = Thread(target=TMB_dispensing)
thread.start()
# TODO print('Stop for 20min incubation, for sealing tape sticking and unsticking')
time.sleep(20 * 60)

# TODO print('Time remaining: ', 20*60-time.process_time()) ???
stopping()
print('ELISA with 100% Plate QC Sample in duplicates way finished. Congratulations!')
