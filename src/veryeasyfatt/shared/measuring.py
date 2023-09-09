""" This module contains the unit registry used for all measurements in the application. """
import pint

unit_registry = pint.UnitRegistry(
    autoconvert_offset_to_baseunit=True, on_redefinition="raise"
)
""" The unit registry used for all measurements in the application. """


unit_registry.default_format = "~P"
unit_registry.define("quintal = 100 * kg = q = centner")
