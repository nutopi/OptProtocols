from opentrons import labware, instruments, robot

# creates custom labware if currently not created
custom_tube = "tray"
if custom_tube not in labware.list():
    tray = labware.create("tray",
                          grid=(1, 1),
                          spacing=(0, 0),
                          diameter=60,
                          depth=15)

tray = labware.load("tray", slot='5')
trough_rack = labware.load('trough-12row', slot='11')
tip_rack1 = labware.load('opentrons-tiprack-300ul', slot='10')
tip_rack2 = labware.load('opentrons-tiprack-300ul', slot='7')
tip_rack3 = labware.load('opentrons-tiprack-300ul', slot='4')
tip_racks = [tip_rack1, tip_rack2, tip_rack3]
# tips300ul_rack1 = labware.load('opentrons-tiprack-300ul', slot='10')

multi = instruments.P300_Multi(mount='left',
                               tip_racks=[tip_rack1, tip_rack2, tip_rack3],
                               aspirate_flow_rate=100,
                               dispense_flow_rate=100)


def multi_dispensing(disp_vol, times):
    for i in range(times):
        multi.pick_up_tip()
        curr_vol = multi.current_volume
        if curr_vol < disp_vol:
            multi.dispense(curr_vol, trough_rack(6))
            multi.aspirate(multi.max_volume, trough_rack(6))
        multi.dispense(disp_vol, tray)
        robot.pause()
        # TODO
        print(disp_vol, ' ul dispensed ', i + 1, ' time')
        multi.drop_tip()

    robot.home()


def multi_transfering(disp_vol, times):
    for i in range(times):
        multi.pick_up_tip()
        multi.aspirate(disp_vol, trough_rack(6))
        multi.dispense(disp_vol, tray)
        multi.blow_out(tray)
        robot.pause()
        print(disp_vol, ' ul dispensed ', i + 1, ' time')
        multi.drop_tip()

    robot.home()


# *************************************** #
# each channel 4 times
# multi range: 30ul-300ul
times1 = 32
disp_vol1 = 135
multi_transfering(disp_vol1, times1)
