# -*- coding: utf8 -*-
"""HelloWorld script using standard pythonpart

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

from HandlePropertiesService import HandlePropertiesService
from HandleDirection         import HandleDirection
from HandleParameterData     import HandleParameterData
from HandleParameterType     import HandleParameterType
from HandleProperties        import HandleProperties


print('Load HelloWorld')


def check_allplan_version(build_ele : BuildingElement,
                          version   : float) -> bool:
    """Check the current Allplan version

    Args:
        build_ele : the building element
        version   : the current Allplan version

    Returns:
        True/False if version is supported by this script
    """
    # Support all versions
    return True


def move_handle(build_ele   : BuildingElement,
                handle_prop : HandleProperties,
                input_pnt   : Geometry.Point3D,
                doc         : ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Called after modification of the element geometry using handles

    Args:
        build_ele   : building element with the parameter properties
        handle_prop : handle properties
        input_pnt   : input point
        doc         : input document

    Returns:
        Object with the result data of the element creation
    """
    HandlePropertiesService.update_property_value(build_ele, handle_prop, input_pnt)

    return create_element(build_ele, doc)


def create_element(build_ele : BuildingElement,
                   doc       : ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Creation of element

    Args:
        build_ele : the building element
        doc       : input document

    Returns:
        result of the created element
    """
    model_ele_list = []
    handle_list    = []

    pyp_util = PythonPartUtil()

    # Extract parameters values ​​from palette
    line_length = build_ele.LineLength.value

    # Define common properties
    if build_ele.UseGlobalProperties.value:
        com_prop = BaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
    else:
        com_prop = build_ele.CommonProperties.value

    # Create 2D line
    line = Geometry.Line2D(0, 0, line_length, 0)

    # Add line to 2d view
    pyp_util.add_pythonpart_view_2d(BasisElements.ModelElement2D(com_prop, line))

    # Create the PythonPart
    model_ele_list = pyp_util.create_pythonpart(build_ele)

    # Create the handles
    handle_length = HandleProperties("LineLengthHandle",
                                     Geometry.Point3D(line_length, 0, 0),
                                     Geometry.Point3D(),
                                     [HandleParameterData("LineLength", HandleParameterType.POINT_DISTANCE)],
                                     HandleDirection.X_DIR
                                     )

    handle_length.info_text = "Longueur"
    handle_list.append(handle_length)

    return CreateElementResult(model_ele_list, handle_list)
