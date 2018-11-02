from opentrons import labware, instruments

# single channel p50 pipette volumes checking

trough_rack = labware.load('trough-12row', slot='2')
water_tubes = labware.load('tube-rack-2ml', slot='3')
tips300ul_rack1 = labware.load('opentrons-tiprack-300ul', slot='1')
# trash = labware.load('trash-box', slot='12')
# waste = labware.load('tube-rack-15_50ml', slot='6')

# mount oznacza po ktorej stronie jest pipeta
# u nas: single: right
# multi: left
single = instruments.P50_Single(mount='right',
                                tip_racks=[tips300ul_rack1],
                                aspirate_flow_rate=100,
                                dispense_flow_rate=100)

single.pick_up_tip()
class DistributeVolume():

    def dispensing(self, destVol, start, end):
        for i in range(start, end):
            volume = single.current_volume
        if volume < destVol:
            single.dispense(volume, trough_rack(0))
            single.aspirate(single.max_volume, trough_rack(0))
        single.dispense(destVol, water_tubes(i))

        single.dispense(single.current_volume, trough_rack(0))


a = 15
b = 25

distributeVol = DistributeVolume()
distributeVol.dispensing(a, 0, 12)
distributeVol.dispensing(b, 12, 24)


