# -*- coding: utf8 -*-
""" HelloWorld script using standard pythonpart

Author:
    Christophe MAIGNAN @ API2GETHER - 2023
"""

import NemAll_Python_BaseElements       as BaseElements
import NemAll_Python_BasisElements      as BasisElements
import NemAll_Python_Geometry           as Geometry
import NemAll_Python_IFW_ElementAdapter as ElementAdapter

from BuildingElement     import BuildingElement
from CreateElementResult import CreateElementResult
from PythonPartUtil      import PythonPartUtil

print('Load HelloWorld.py')


def check_allplan_version(build_ele : BuildingElement,
                          version   : float) -> bool:
    """ Check the current Allplan version

    Args:
        build_ele : the building element
        version   : the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Support all versions
    return True


def create_element(build_ele : BuildingElement,
                   doc       : ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """ Creation of element

    Args:
        build_ele : the building element
        doc       : input document

    Returns:
        result of the created element
    """
    model_ele_list = []

    pyp_util = PythonPartUtil()

    # Define common properties
    com_prop = BaseElements.CommonProperties()
    com_prop.GetGlobalProperties()

    # Create 2D line
    line = Geometry.Line2D(0, 0, 1000, 0)

    # Add line to 2d view
    pyp_util.add_pythonpart_view_2d(BasisElements.ModelElement2D(com_prop, line))

    # Create the PythonPart
    model_ele_list = pyp_util.create_pythonpart(build_ele)

    return CreateElementResult(model_ele_list)
