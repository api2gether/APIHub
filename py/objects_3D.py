# -*- coding: utf8 -*-
"""Objects3D script using standard pythonpart

Author:
    Christophe MAIGNAN @ API2GETHER - 2023
"""
import math

import NemAll_Python_BaseElements       as BaseElements
import NemAll_Python_BasisElements      as BasisElements
import NemAll_Python_Geometry           as Geometry
import NemAll_Python_IFW_ElementAdapter as ElementAdapter
import NemAll_Python_IFW_Input          as IFWInput
import NemAll_Python_ArchElements       as ArchElements

from BuildingElement              import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from CreateElementResult          import CreateElementResult
from PythonPartUtil               import PythonPartUtil

from HandlePropertiesService import HandlePropertiesService
from HandleDirection         import HandleDirection
from HandleParameterData     import HandleParameterData
from HandleParameterType     import HandleParameterType
from HandleProperties        import HandleProperties


print('Load Objects3D')


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

    attr_list = BuildingElementAttributeList()
    pyp_util  = PythonPartUtil()

    # Extract parameters values from palette
    column_id = build_ele.ColumnId.value

    column_concrete_gr_value = build_ele.ConcreteGrade.value

    concrete_grade_dict = {1: 'C12/15',
                           2: 'C16/20',
                           3: 'C20/25',
                           4: 'C25/30',
                           5: 'C30/37',
                           6: 'C35/45',
                           7: 'C40/50',
                           8: 'C45/55',
                           9: 'C50/60',
                           10: 'C55/67',
                           11: 'C60/75',
                           12: 'C70/85',
                           13: 'C80/95',
                           14: 'C90/105',
                           15: 'C100/115',
                           }
    column_concrete_gr = concrete_grade_dict[column_concrete_gr_value]

    choice = build_ele.ChoiceRadioGroup.value

    column_length    = build_ele.ColumnLength.value
    column_thickness = build_ele.ColumnThick.value
    column_radius    = build_ele.ColumnRadius.value
    column_height    = build_ele.ColumnHeight.value

    attach_point = build_ele.AttachmentPoint.value

    plane_ref: ArchElements.PlaneReferences = build_ele.PlaneReferences.value
    column_bottom = plane_ref.GetAbsBottomElevation()

    # Define common properties
    if build_ele.UseGlobalProperties.value:
        com_prop = BaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
    else:
        com_prop = build_ele.CommonProperties.value

    # Define hatch properties
    has_hatch  = build_ele.HatchCheckBox.value
    hatch_prop = BasisElements.HatchingProperties()
    hatch_prop.HatchID = build_ele.HatchStyle.value

    # Define fill properties
    has_fill  = build_ele.FillCheckBox.value
    fill_prop = BasisElements.FillingProperties()
    fill_prop.FirstColor = BaseElements.GetColorById(build_ele.FillColor.value)

    # Define text properties
    is_showing_annotation = build_ele.ShowTextCheckBox.value

    text_com_prop = BaseElements.CommonProperties()
    text_com_prop = build_ele.TextCommonProperties.value

    text_dict = {"Aligner à Gauche" : BasisElements.TextAlignment.eLeftMiddle,
                 "Centrer"          : BasisElements.TextAlignment.eMiddleMiddle,
                 "Aligner à Droite" : BasisElements.TextAlignment.eRightMiddle
                 }

    text_prop           = BasisElements.TextProperties()
    text_prop.Height    = text_prop.Width = build_ele.TextHeight.value
    text_prop.Alignment = text_dict[build_ele.TextAlignment.value]
    text_origin         = build_ele.TextOrigin.value

    # Create 3D object
    if choice == "rectangle":
        my_column = Cuboid(com_prop, attach_point, column_bottom, column_length, column_thickness, column_height)
    else:
        my_column = Cylinder(com_prop, attach_point, column_bottom, column_radius, column_height)

    my_column.create_geo()

    # Add object to view
    pyp_util.add_pythonpart_view_2d3d(my_column.add_view())

    # Create the handles
    for item in my_column.handles_prop:
        handle = HandleProperties(item.handle_id,
                                  item.handle_point,
                                  item.ref_point,
                                  [HandleParameterData(item.handle_param_data, HandleParameterType.POINT_DISTANCE)],
                                  item.handle_move_dir
                                  )
        handle.info_text = item.handle_info_text
        handle_list.append(handle)

    # Create the annotation
    if is_showing_annotation:
        text   = f"{column_id} {my_column.name_dim}"
        if column_concrete_gr_value > 4:
            text += f"\n{column_concrete_gr}"
        origin = Geometry.Point2D(text_origin)
        pyp_util.add_pythonpart_view_2d(BasisElements.TextElement(text_com_prop, text_prop, text, origin))

        text_handle = HandleProperties("Text",
                                       text_origin,
                                       Geometry.Point3D(),
                                       [HandleParameterData("TextOrigin", HandleParameterType.POINT, False)],
                                       HandleDirection.XYZ_DIR
                                       )
        text_handle.handle_type = IFWInput.ElementHandleType.HANDLE_SQUARE_RED
        text_handle.info_text   = "Origine du texte"
        handle_list.append(text_handle)

    # Create hatch
    if has_hatch:
        pyp_util.add_pythonpart_view_2d(BasisElements.HatchingElement(com_prop, hatch_prop, my_column.create_hatch_geo()))

    # Create fill
    if has_fill:
        pyp_util.add_pythonpart_view_2d(BasisElements.FillingElement(com_prop, fill_prop, my_column.create_hatch_geo()))

    #
    # Add attributes
    #

    # Attribute set object @18358@
    attr_list.add_attribute(18358, "Column")

    # Trade @209@
    attr_list.add_attribute(209, 13)

    # Status @49@
    attr_list.add_attribute(49, 0)

    # Load bearing @573@
    attr_list.add_attribute(573, 1)

    # Concrete grade @1905@
    attr_list.add_attribute(1905, column_concrete_gr)

    # Geometry
    length, thickness, radius, height, surface, volume = my_column.calcul_dimensions()

    attr_list.add_attribute(220, length)
    attr_list.add_attribute(221, thickness)
    attr_list.add_attribute(107, radius)
    attr_list.add_attribute(222, height)
    attr_list.add_attribute(293, surface)
    attr_list.add_attribute(226, volume)

    attr_list.add_attributes_from_parameters(build_ele)
    pyp_util.add_attribute_list(attr_list)

    # Reference point
    placement_mat = Geometry.Matrix3D()
    placement_mat.SetTranslation(Geometry.Vector3D(my_column.placement_pt))

    # Create the PythonPart
    model_ele_list = pyp_util.create_pythonpart(build_ele, placement_mat)

    return CreateElementResult(model_ele_list, handle_list)


class Objects3D:
    """Definition of class Objects3D
    """
    def __init__(self,
                 object_prop   : BaseElements.CommonProperties,
                 attach_point  : int,
                 column_bottom : float):
        self.object_prop   = object_prop
        self.geo           = None
        self.attach_point  = attach_point
        self.x_offset      = 0
        self.y_offset      = 0
        self.z_offset      = column_bottom


    def calcul_dimensions(self):
        pass


    def create_geo(self):
        pass


    def create_hatch_geo(self):
        pass


    def add_view(self):
        object_3d = BasisElements.ModelElement3D(self.object_prop, self.geo)
        return object_3d


    def attachment_point(self):
        pass


class Handle:
    """Definition of class Handle
    """
    def __init__(self,
                 placement_pt      : Geometry.Point3D,
                 handle_id         : str,
                 handle_point      : Geometry.Point3D,
                 ref_point         : Geometry.Point3D,
                 handle_param_data : str,
                 handle_move_dir   : HandleDirection,
                 handle_info_text  : str):
        self.handle_id         = handle_id
        self.handle_point      = placement_pt + handle_point
        self.ref_point         = placement_pt + ref_point
        self.handle_param_data = handle_param_data
        self.handle_move_dir   = handle_move_dir
        self.handle_info_text  = handle_info_text


class Cuboid(Objects3D):
    """Definition of class Cuboid
    """
    def __init__(self,
                 object_prop   : BaseElements.CommonProperties,
                 attach_point  : int,
                 column_bottom : float,
                 column_length : float,
                 column_thick  : float,
                 column_height : float):
        Objects3D.__init__(self, object_prop, attach_point, column_bottom)
        self.column_length = column_length
        self.column_thick  = column_thick
        self.column_height = column_height
        self.name_dim      = f"{round(column_length / 10)}x{round(column_thick / 10)}"
        self.placement_pt  = self.attachment_point()
        self.handles_prop  = [Handle(self.placement_pt,
                                     "ColumnLengthHandle",
                                     Geometry.Point3D(self.column_length, 0, 0),
                                     Geometry.Point3D(),
                                     "ColumnLength",
                                     HandleDirection.X_DIR,
                                     "Longueur"
                                     ),
                              Handle(self.placement_pt,
                                     "ColumnThickHandle",
                                     Geometry.Point3D(self.column_length, self.column_thick, 0),
                                     Geometry.Point3D(self.column_length, 0, 0),
                                     "ColumnThick",
                                     HandleDirection.Y_DIR,
                                     "Largeur"
                                     ),
                              Handle(self.placement_pt,
                                     "ColumnHeightHandle",
                                     Geometry.Point3D(0, 0, self.column_height),
                                     Geometry.Point3D(),
                                     "ColumnHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur"
                                     )
                              ]


    def calcul_dimensions(self):
        length    = self.column_length * 1e-3
        thickness = self.column_thick * 1e-3
        radius    = 0
        height    = self.column_height * 1e-3
        surface   = length * thickness
        volume    = surface * height

        return (length, thickness, radius, height, surface, volume)


    def create_geo(self):
        placement = Geometry.AxisPlacement3D(Geometry.Point3D(),
                                             Geometry.Vector3D(1, 0, 0),
                                             Geometry.Vector3D(0, 0, 1)
                                             )
        self.geo  = Geometry.BRep3D.CreateCuboid(placement,
                                                 self.column_length,
                                                 self.column_thick,
                                                 self.column_height
                                                 )


    def create_hatch_geo(self):
        hatch_geo = Geometry.Polygon2D.CreateRectangle(Geometry.Point2D(),
                                                       Geometry.Point2D(self.column_length, self.column_thick)
                                                       )

        return hatch_geo


    def attachment_point(self):
        if self.attach_point in {2, 5, 8}:
            self.x_offset = -self.column_length / 2
        elif self.attach_point in {3, 6, 9}:
            self.x_offset = -self.column_length

        if self.attach_point in {1, 2, 3}:
            self.y_offset = -self.column_thick
        elif self.attach_point in {4, 5, 6}:
            self.y_offset = -self.column_thick / 2

        placement_pt = Geometry.Point3D(self.x_offset, self.y_offset, self.z_offset)

        return placement_pt


class Cylinder(Objects3D):
    """Definition of class Cylinder
    """
    def __init__(self,
                 object_prop   : BaseElements.CommonProperties,
                 attach_point  : int,
                 column_bottom : float,
                 column_rad    : float,
                 column_height : float):
        Objects3D.__init__(self, object_prop, attach_point, column_bottom)
        self.column_radius = column_rad
        self.column_height = column_height
        self.name_dim      = f"Ø{round(2 * column_rad / 10)}"
        self.placement_pt  = self.attachment_point()
        self.handles_prop  = [Handle(self.placement_pt,
                                     "ColumnRadiusHandle",
                                     Geometry.Point3D(self.column_radius, 0, 0),
                                     Geometry.Point3D(),
                                     "ColumnRadius",
                                     HandleDirection.X_DIR,
                                     "Rayon"
                                     ),
                              Handle(self.placement_pt,
                                     "ColumnHeightHandle",
                                     Geometry.Point3D(0, 0, self.column_height),
                                     Geometry.Point3D(),
                                     "ColumnHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur"
                                     )
                              ]


    def calcul_dimensions(self):
        length    = 0
        thickness = 0
        radius    = self.column_radius * 1e-3
        height    = self.column_height * 1e-3
        surface   = math.pi * radius ** 2
        volume    = surface * height

        return (length, thickness, radius, height, surface, volume)


    def create_geo(self):
        placement = Geometry.AxisPlacement3D(Geometry.Point3D(),
                                             Geometry.Vector3D(1, 0, 0),
                                             Geometry.Vector3D(0, 0, 1)
                                             )
        self.geo  = Geometry.Cylinder3D(placement,
                                        self.column_radius,
                                        self.column_radius,
                                        Geometry.Point3D(0, 0, self.column_height)
                                        )


    def create_hatch_geo(self):
        line          = Geometry.Line3D(0, 0, 0, self.column_radius, 0, 0)
        angle         = Geometry.Angle()
        angle.Deg     = 10
        rotation_axis = Geometry.Line3D(Geometry.Point3D(),
                                        Geometry.Point3D(0, 0, 1)
                                        )
        transformation_matrix = Geometry.Matrix3D()

        hatch_geo  = Geometry.Polygon2D()
        for i in range(36):
            transformation_matrix.SetRotation(rotation_axis, angle)
            line       = Geometry.Transform(line, transformation_matrix)
            hatch_geo += Geometry.Point2D(line.EndPoint.X, line.EndPoint.Y)
        hatch_geo += hatch_geo.StartPoint

        return hatch_geo


    def attachment_point(self):
        if self.attach_point in {1, 4, 7}:
            self.x_offset = self.column_radius
        elif self.attach_point in {3, 6, 9}:
            self.x_offset = -self.column_radius

        if self.attach_point in {1, 2, 3}:
            self.y_offset = -self.column_radius
        elif self.attach_point in {7, 8, 9}:
            self.y_offset = self.column_radius

        placement_pt = Geometry.Point3D(self.x_offset, self.y_offset, self.z_offset)

        return placement_pt
