# =============================================================================
# Copyright (C) 2014 Ryan Holmes
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


from service.const import PortMultiBuyOptions
from service.price import Price as sPrc


MULTIBUY_OPTIONS = (
    (PortMultiBuyOptions.LOADED_CHARGES, 'Loaded Charges', 'Export charges loaded into modules', True),
    (PortMultiBuyOptions.IMPLANTS, 'Implants && Boosters', 'Export implants and boosters', False),
    (PortMultiBuyOptions.CARGO, 'Cargo', 'Export cargo contents', True),
    (PortMultiBuyOptions.OPTIMIZE_PRICES, 'Optimize Prices', 'Replace items by cheaper alternatives', False),
    (PortMultiBuyOptions.CHEAPEN_PRICES, 'Cheapen Prices', 'Replace items by cheapest alternatives', False),
)


def exportMultiBuy(fit, options, callback):
    itemAmounts = {}

    for module in fit.modules:
        if module.item:
            # Mutated items are of no use for multibuy
            if module.isMutated:
                continue
            _addItem(itemAmounts, module.item)
        if module.charge and options[PortMultiBuyOptions.LOADED_CHARGES]:
            _addItem(itemAmounts, module.charge, module.numCharges)

    for drone in fit.drones:
        _addItem(itemAmounts, drone.item, drone.amount)

    for fighter in fit.fighters:
        _addItem(itemAmounts, fighter.item, fighter.amountActive)

    if options[PortMultiBuyOptions.CARGO]:
        for cargo in fit.cargo:
            _addItem(itemAmounts, cargo.item, cargo.amount)

    if options[PortMultiBuyOptions.IMPLANTS]:
        for implant in fit.implants:
            _addItem(itemAmounts, implant.item)

        for booster in fit.boosters:
            _addItem(itemAmounts, booster.item)

    if options[PortMultiBuyOptions.OPTIMIZE_PRICES]:

        def formatCheaperExportCb(replacementsCheaper):
            updatedAmounts = {}
            for item, itemAmount in itemAmounts.items():
                _addItem(updatedAmounts, replacementsCheaper.get(item, item), itemAmount)
            string = _prepareString(fit.ship.item, updatedAmounts)
            callback(string)

        priceSvc = sPrc.getInstance()
        priceSvc.findCheaperReplacements(itemAmounts, formatCheaperExportCb)
    
    if options[PortMultiBuyOptions.CHEAPEN_PRICES]:

        def formatCheapestExportCb(replacementsCheapest):
            updatedAmounts = {}
            for item, itemAmount in itemAmounts.items():
                _addItem(updatedAmounts, replacementsCheapest.get(item, item), itemAmount)
            string = _prepareString(fit.ship.item, updatedAmounts)
            callback(string)

        priceSvc = sPrc.getInstance()
        priceSvc.findCheapestReplacements(itemAmounts, formatCheapestExportCb)
    
    else:
        string = _prepareString(fit.ship.item, itemAmounts)
        if callback:
            callback(string)
        else:
            return string


def _addItem(container, item, quantity=1):
    if item not in container:
        container[item] = 0
    container[item] += quantity


def _prepareString(shipItem, itemAmounts):
    exportLines = []
    exportLines.append(shipItem.name)
    for item in sorted(itemAmounts, key=lambda i: (i.group.category.name, i.group.name, i.name)):
        count = itemAmounts[item]
        if count == 1:
            exportLines.append(item.name)
        else:
            exportLines.append('{} x{}'.format(item.name, count))

    return "\n".join(exportLines)
