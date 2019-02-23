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
tips300ul_rack1 = labware.load('opentrons-tiprack-300ul', slot='10')

multi = instruments.P300_Multi(mount='left',
                               tip_racks=[tips300ul_rack1],
                               aspirate_flow_rate=100,
                               dispense_flow_rate=100)


def multi_dispensing(disp_vol, times):
    for i in range(8):
        multi.pick_up_tip()
        for j in range(times):
            curr_vol = multi.current_volume
            if curr_vol < disp_vol:
                multi.dispense(curr_vol, trough_rack(6))
                multi.aspirate(multi.max_volume, trough_rack(6))
            multi.dispense(disp_vol, tray)
            robot.pause()
            print(disp_vol, ' ul dispensed by ', i + 1, ' channel ', j + 1, ' time')
        multi.drop_tip()
    robot.home()


def multi_transfering(disp_vol, times):
    for i in range(8):
        multi.pick_up_tip()
        for j in range(times):
            multi.aspirate(disp_vol, trough_rack(6))
            multi.dispense(disp_vol, tray)
            multi.blow_out(tray)
            robot.pause()
            print(disp_vol, ' ul dispensed by ', i + 1, ' channel ', j + 1, ' time')
        multi.drop_tip()
    robot.home()


# *************************************** #
# each channel 4 times
# multi range: 30ul-300ul
times1 = 2
disp_vol1 = 135
multi_dispensing(disp_vol1, times1)
