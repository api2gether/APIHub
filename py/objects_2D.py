# -*- coding: utf8 -*-
"""Objects2D script using standard pythonpart

Author:
    Christophe MAIGNAN @ API2GETHER - 2023
"""
from typing import List

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


print('Load Objects2D')


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

    # Extract parameters values from palette
    choice = build_ele.ChoiceRadioGroup.value

    line_length   = build_ele.LineLength.value
    rect_length   = build_ele.RectLength.value
    rect_width    = build_ele.RectWidth.value
    circle_radius = build_ele.CircleRadius.value

    # Define common properties
    if build_ele.UseGlobalProperties.value:
        com_prop = BaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
    else:
        com_prop = build_ele.CommonProperties.value

    # Create 2D object
    if choice == "line":
        object_2d = Line2D(com_prop, line_length)
    elif choice == "rectangle":
        object_2d = Rectangle2D(com_prop, rect_length, rect_width)
    else:
        object_2d = Circle2D(com_prop, circle_radius)

    object_2d.create_geo()

    # Add object to view
    pyp_util.add_pythonpart_view_2d(object_2d.add_view())

    # Create the handles
    for item in object_2d.handles_prop:
        handle = HandleProperties(item.handle_id,
                                  item.handle_point,
                                  item.ref_point,
                                  [HandleParameterData(item.handle_param_data, HandleParameterType.POINT_DISTANCE)],
                                  item.handle_move_dir
                                  )
        handle.info_text = item.handle_info_text
        handle_list.append(handle)

    # Create the PythonPart
    model_ele_list = pyp_util.create_pythonpart(build_ele)

    return CreateElementResult(model_ele_list, handle_list)


class Objects2D:
    """Definition of class Objects2D
    """
    def __init__(self,
                 object_2d_prop : BaseElements.CommonProperties):
        self.object_2d_prop = object_2d_prop
        self.geo            = None


    def create_geo(self):
        pass


    def add_view(self):
        object_2d = BasisElements.ModelElement2D(self.object_2d_prop, self.geo)
        return object_2d


class Handle:
    """Definition of class Handle
    """
    def __init__(self,
                 handle_id         : str,
                 handle_point      : Geometry.Point3D,
                 ref_point         : Geometry.Point3D,
                 handle_param_data : List[HandleParameterData],
                 handle_move_dir   : HandleDirection,
                 handle_info_text  : str):
        self.handle_id         = handle_id
        self.handle_point      = handle_point
        self.ref_point         = ref_point
        self.handle_param_data = handle_param_data
        self.handle_move_dir   = handle_move_dir
        self.handle_info_text  = handle_info_text


class Line2D(Objects2D):
    """Definition of class Line2D
    """
    def __init__(self,
                 object_2d_prop : BaseElements.CommonProperties,
                 line_length    : float):
        Objects2D.__init__(self, object_2d_prop)
        self.line_length  = line_length
        self.handles_prop = [Handle("LineLengthHandle",
                                    Geometry.Point3D(self.line_length, 0, 0),
                                    Geometry.Point3D(),
                                    "LineLength",
                                    HandleDirection.X_DIR,
                                    "Longueur"
                                    )
                             ]


    def create_geo(self):
        self.geo = Geometry.Line2D(0, 0, self.line_length, 0)


class Rectangle2D(Objects2D):
    """Definition of class Rectangle2D
    """
    def __init__(self,
                 object_2d_prop : BaseElements.CommonProperties,
                 rect_length    : float,
                 rect_width     : float):
        Objects2D.__init__(self, object_2d_prop)
        self.rect_length  = rect_length
        self.rect_width   = rect_width
        self.handles_prop = [Handle("RectLengthHandle",
                                    Geometry.Point3D(self.rect_length, 0, 0),
                                    Geometry.Point3D(),
                                    "RectLength",
                                    HandleDirection.X_DIR,
                                    "Longueur"
                                    ),
                             Handle("RectWidthHandle",
                                    Geometry.Point3D(self.rect_length, self.rect_width, 0),
                                    Geometry.Point3D(self.rect_length, 0, 0),
                                    "RectWidth",
                                    HandleDirection.Y_DIR,
                                    "Largeur"
                                    )
                             ]


    def create_geo(self):
        self.geo  = Geometry.Polygon2D()
        self.geo += Geometry.Point2D()
        self.geo += Geometry.Point2D(self.rect_length, 0)
        self.geo += Geometry.Point2D(self.rect_length, self.rect_width)
        self.geo += Geometry.Point2D(0, self.rect_width)
        self.geo += self.geo.StartPoint


class Circle2D(Objects2D):
    """Definition of class Circle2D
    """
    def __init__(self,
                 object_2d_prop : BaseElements.CommonProperties,
                 circle_radius  : float):
        Objects2D.__init__(self, object_2d_prop)
        self.circle_radius = circle_radius
        self.handles_prop  = [Handle("CircleRadiusHandle",
                                     Geometry.Point3D(self.circle_radius, 0, 0),
                                     Geometry.Point3D(),
                                     "CircleRadius",
                                     HandleDirection.X_DIR,
                                     "Rayon"
                                     )
                              ]


    def create_geo(self):
        self.geo = Geometry.Arc2D(Geometry.Point2D(),self.circle_radius)
