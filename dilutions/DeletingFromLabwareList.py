from opentrons import labware


def deleting_from_list():
    print('\nLABWARE LIST BEFORE: ', labware.list())
    labware.list().remove("tube_2ml_rack_35")
    print('\nLABWARE LIST AFTER: ', labware.list())


deleting_from_list()
