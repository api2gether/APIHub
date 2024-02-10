# -*- coding: utf8 -*-
"""Reinforced Concrete Column script using standard pythonpart

Author:
    Christophe MAIGNAN @ API2GETHER - 2024
"""
from typing import List

import math
import csv

import NemAll_Python_BaseElements       as BaseElements
import NemAll_Python_BasisElements      as BasisElements
import NemAll_Python_Geometry           as Geometry
import NemAll_Python_AllplanSettings    as Settings
import NemAll_Python_IFW_ElementAdapter as ElementAdapter
import NemAll_Python_IFW_Input          as IFWInput
import NemAll_Python_ArchElements       as ArchElements
import NemAll_Python_Reinforcement      as Reinforcement

from BuildingElement              import BuildingElement
from BuildingElementAttributeList import BuildingElementAttributeList
from CreateElementResult          import CreateElementResult
from PythonPartUtil               import PythonPartUtil
from ControlPropertiesUtil        import ControlPropertiesUtil

from HandlePropertiesService import HandlePropertiesService
from HandleDirection         import HandleDirection
from HandleParameterData     import HandleParameterData
from HandleParameterType     import HandleParameterType
from HandleProperties        import HandleProperties

from Utils.RotationUtil import RotationUtil

import StdReinfShapeBuilder.GeneralReinfShapeBuilder  as GeneralShapeBuilder
import StdReinfShapeBuilder.LinearBarPlacementBuilder as LinearBarBuilder

from StdReinfShapeBuilder.ConcreteCoverProperties      import ConcreteCoverProperties
from StdReinfShapeBuilder.ReinforcementShapeProperties import ReinforcementShapeProperties
from StdReinfShapeBuilder.RotationAngles               import RotationAngles
from StdReinfShapeBuilder.BarShapePlacementUtil        import BarShapePlacementUtil


print('Load Reinforced Concrete Column')


def check_allplan_version(build_ele : BuildingElement,
                          version   : float) -> bool:
    """Check the current Allplan version

    Args:
        build_ele : the building element
        version   : the current Allplan version

    Returns:
        True/False if version is supported by this script
    """
    # Support versions >= 2024
    version = Settings.AllplanVersion.MainReleaseName()
    if float(version) >= 2024:
        return True
    else:
        return False


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


def initialize_control_properties(build_ele      : BuildingElement,
                                  ctrl_prop_util : ControlPropertiesUtil,
                                  doc            : ElementAdapter.DocumentAdapter) -> None:
    """Called after the properties and their values are read, but before
    the property palette is displayed.

    Args:
        build_ele      : building element
        ctrl_prop_util : control properties utility
        doc            : document
    """
    if build_ele.CSVFilePath.value:
        ctrl_prop_util.set_enable_condition("ImportDataButton", "True")

    set_constructive_dispositions(build_ele, ctrl_prop_util)
    calcul_as_real(build_ele)


def modify_control_properties(build_ele      : BuildingElement,
                              ctrl_prop_util : ControlPropertiesUtil,
                              value_name     : str,
                              event_id       : int,
                              doc            : ElementAdapter.DocumentAdapter) -> bool:
    """Called after each change within the property palette

    Args:
        build_ele      : building element
        ctrl_prop_util : control properties utility
        value_name     : name(s) of the modified value (multiple names are separated by ,)
        event_id       : event ID
        doc            : document

    Returns:
        True if an update of the property palette is necessary, False otherwise
    """
    if value_name == "ChoiceRadioGroup":
        if build_ele.ChoiceRadioGroup.value == "circle":
            build_ele.ColumnRotAngleZ.value = 0
            build_ele.TextRotAngle.value    = 0

            return True

    if event_id == build_ele.IMPORT_REINF_DATA_FROM_CSV:
        # Path of CSV file
        csv_file_path = build_ele.CSVFilePath.value

        # Initializing a list to store the data
        data = []

        # Opening and reading the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            # Iterating over each row in the CSV file
            for row in csv_reader:
                # Search column name
                if row['Repère'] == build_ele.ColumnId.value:
                    # Extracting the required data
                    long_rebars_diameter = row.get('Diamètre Armatures Longitudinales', '').strip()
                    long_rebars_quantity = row.get('Quantité Armatures Longitudinales', '').strip()
                    stir_rebars_diameter = row.get('Diamètre Armatures Transversales', '').strip()
                    A_stirrup_spacing    = row.get('Espacement A Armatures Transversales', '').strip()
                    B_stirrup_spacing    = row.get('Espacement B Armatures Transversales', '').strip()
                    C_stirrup_spacing    = row.get('Espacement C Armatures Transversales', '').strip()

                    # Change value if not empty
                    if all([long_rebars_diameter, long_rebars_quantity, stir_rebars_diameter, A_stirrup_spacing, B_stirrup_spacing, C_stirrup_spacing]):
                        long_rebars_diameter = int(long_rebars_diameter)
                        valid_diameters = [8, 10, 12, 14, 16, 20]
                        if long_rebars_diameter in valid_diameters:
                            build_ele.FirstBarDiameter.value  = long_rebars_diameter
                            build_ele.SecondBarDiameter.value = long_rebars_diameter

                        concr_cover = build_ele.ReinfConcreteCover.value
                        # Rectangular column
                        if build_ele.ChoiceRadioGroup.value == "rectangle":

                            length      = max(build_ele.ColumnLength.value, build_ele.ColumnThick.value) - 2 * concr_cover
                            thickness   = min(build_ele.ColumnLength.value, build_ele.ColumnThick.value) - 2 * concr_cover
                            nbr_rebars  = int(long_rebars_quantity) - 4 # 4 => one main longitudinal rebar for each corner

                            esp_min = 100
                            esp_max = 400

                            min_value_in_length = max(0, math.ceil(length / esp_max) - 1)
                            max_value_in_length = max(min_value_in_length, math.floor(length / esp_min) - 1)

                            min_value_in_thick = max(0, math.ceil(thickness / esp_max) - 1)
                            max_value_in_thick = max(min_value_in_thick, math.floor(thickness / esp_min) - 1)

                            init_qtt_in_length = max(min_value_in_length, math.ceil((nbr_rebars - 2 * min_value_in_thick) / 2))
                            init_qtt_in_thick  = min_value_in_thick

                            if init_qtt_in_length > max_value_in_length:
                                build_ele.ScndBarRectQttInLength.value = max_value_in_length
                                init_qtt_in_thick = nbr_rebars - 2 * max_value_in_length
                            else:
                                build_ele.ScndBarRectQttInLength.value = init_qtt_in_length

                            if init_qtt_in_thick > max_value_in_thick:
                                build_ele.ScndBarRectQttInThick.value = max_value_in_thick
                            else:
                                build_ele.ScndBarRectQttInThick.value = init_qtt_in_thick

                            main_stirrup_max_spac = min(20 * build_ele.FirstBarDiameter.value, 400, thickness)

                        else:
                            diameter = 2 * (build_ele.ColumnRadius.value - concr_cover)

                            min_value_circ = max(4, math.ceil(diameter / esp_max))
                            max_value_circ = max(min_value_circ, math.floor(diameter / esp_min))

                            nbr_rebars = max(min_value_circ, min(nbr_rebars, max_value_circ))
                            build_ele.RebarCircQtt.value = nbr_rebars

                            main_stirrup_max_spac = min(20 * build_ele.FirstBarDiameter.value, 400, min(build_ele.ColumnLength.value, build_ele.ColumnThick.value))

                        # Stirrup diameter and spacing
                        scnd_stirrup_max_spac  = 0.6 * main_stirrup_max_spac

                        A_stirrup_spacing = max(main_stirrup_max_spac, float(A_stirrup_spacing))
                        B_stirrup_spacing = max(scnd_stirrup_max_spac, float(B_stirrup_spacing))
                        C_stirrup_spacing = max(scnd_stirrup_max_spac, float(C_stirrup_spacing))

                        main_stirrup = build_ele.MainStirrup.value
                        main_stirrup._replace(Spacing = A_stirrup_spacing)
                        valid_diameters = [6, 8, 10]
                        stir_rebars_diameter = int(stir_rebars_diameter)
                        if stir_rebars_diameter in valid_diameters:
                            main_stirrup._replace(Diameter = stir_rebars_diameter)

                        stirrup_list = build_ele.StirrupList.value
                        stirrup_list[0] = stirrup_list[0]._replace(Spacing = B_stirrup_spacing)
                        stirrup_list[1] = stirrup_list[1]._replace(Spacing = C_stirrup_spacing)
                        break

        calcul_as_real(build_ele)
        return True

    if event_id == build_ele.CALC_LONG_REBAR_DIAM:
        as_min = build_ele.AsMinDouble.value
        list_diam_mm = [8, 10, 12, 14, 16, 20]
        dict_section_cm2 = {diam: math.pi * (diam * 0.1 / 2) ** 2 for diam in list_diam_mm}
        if build_ele.ChoiceRadioGroup.value == "rectangle":
            nbr_rebars = 4 + 2 * (build_ele.ScndBarRectQttInLength.value + build_ele.ScndBarRectQttInThick.value)
        else:
            nbr_rebars = build_ele.RebarCircQtt.value

        for diametre, section in dict_section_cm2.items():
            if section * nbr_rebars >= as_min:
                build_ele.FirstBarDiameter.value = build_ele.SecondBarDiameter.value = diametre
                break

        calcul_as_real(build_ele)

        return True

    if value_name in ('ShowReinfCheckBox',
                      'ChoiceRadioGroup',
                      'ColumnLength',
                      'ColumnThick',
                      'ColumnRadius',
                      'TakeColumnDim',
                      'FirstBarDiameter',
                      'SecondBarDiameter',
                      'ScndBarAsFirstBar',
                      'ScndBarRectQttInLength',
                      'ScndBarRectQttInThick',
                      'RebarCircQtt',
                      'MainStirrup',
                      'StirrupList'):

        if build_ele.TakeColumnDim.value:
            build_ele.NextColumnLength.value = build_ele.ColumnLength.value
            build_ele.NextColumnThick.value  = build_ele.ColumnThick.value
            build_ele.NextColumnRadius.value = build_ele.ColumnRadius.value

        if build_ele.ScndBarAsFirstBar.value:
            build_ele.SecondBarDiameter.value = build_ele.FirstBarDiameter.value

        set_constructive_dispositions(build_ele, ctrl_prop_util)
        calcul_as_real(build_ele)

        return True

    if value_name == "ColumnRotAngleZ":
        build_ele.TextRotAngle.value = -build_ele.ColumnRotAngleZ.value

        return True

    if value_name == "CSVFilePath":
        if build_ele.CSVFilePath.value:
            ctrl_prop_util.set_enable_condition("ImportDataButton", "True")
            return True

    return False


def on_control_event(build_ele : BuildingElement,
                     event_id  : int,
                     doc       : ElementAdapter.DocumentAdapter) -> None:
    """ Called, when an event is triggered with a control (e.g. a button) in a property palette

    Args:
        build_ele : building element with the parameter properties
        event_id  : event id of the triggered control
        doc       : document of the Allplan drawing files
    """


def create_preview(build_ele : BuildingElement,
                   doc       : ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Function for the creation of the library preview elements.

    Args:
        build_ele : the building element
        doc       : input document

    Returns:
        Preview elements. Only elements included in the property "elements" will be shown in the library preview
    """
    com_prop = Settings.AllplanGlobalSettings.GetCurrentCommonProperties()
    com_prop.GetGlobalProperties()

    axis = Geometry.AxisPlacement3D(Geometry.Point3D())
    geo  = Geometry.BRep3D.CreateCuboid(axis, 300, 300, 5000)

    model_ele_list = [BasisElements.ModelElement3D(com_prop, geo)]

    return CreateElementResult(elements = model_ele_list)


def create_element(build_ele : BuildingElement,
                   doc       : ElementAdapter.DocumentAdapter) -> CreateElementResult:
    """Creation of element

    Args:
        build_ele : the building element
        doc       : input document

    Returns:
        result of the created element
    """
    model_ele_list  = []
    handle_list     = []

    attr_list      = BuildingElementAttributeList()
    pyp_util       = PythonPartUtil()

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
    col_z_rotation   = build_ele.ColumnRotAngleZ.value

    has_next_col    = build_ele.NextColumnCheckBox.value
    next_col_length = build_ele.NextColumnLength.value
    next_col_thick  = build_ele.NextColumnThick.value
    next_col_radius = build_ele.NextColumnRadius.value

    attach_point = build_ele.AttachmentPoint.value

    plane_ref: ArchElements.PlaneReferences = build_ele.PlaneReferences.value
    column_bottom = plane_ref.GetAbsBottomElevation()

    slab_height = build_ele.SlabHeight.value

    texture = BasisElements.TextureDefinition(build_ele.MaterialButton.value)

    # Define common properties
    com_prop = build_ele.CommonProperties.value

    # Define help properties
    help_prop = BaseElements.CommonProperties()
    help_prop.GetGlobalProperties()
    help_prop.HelpConstruction = True

    # Define reinforcement properties
    is_showing_reinf = build_ele.ShowReinfCheckBox.value
    reinf_prop       = BaseElements.CommonProperties()
    reinf_prop.Layer = build_ele.ReinfLayerProperties.value

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
    angle               = Geometry.Angle()
    angle.Deg           = build_ele.TextRotAngle.value
    text_prop.TextAngle = angle

    text_origin = build_ele.TextOrigin.value

    # Define handle properties
    is_showing_handles = build_ele.ShowHandlesCheckBox.value

    # Create 3D object
    if choice == "rectangle":
        main_column = Cuboid(build_ele, True, com_prop, attach_point, column_bottom, texture, column_length, column_thickness, column_height, col_z_rotation, slab_height)
        next_column = Cuboid(build_ele, False, help_prop, attach_point, column_height, texture, next_col_length, next_col_thick, 1000, col_z_rotation, slab_height)

        # Constructions line to align center point
        frst_line   = Geometry.Line3D(0, 0, 0, column_length, column_thickness, 0)
        scnd_line   = Geometry.Line3D(0, 0, 0, next_col_length, next_col_thick, 0)
        from_point  = scnd_line.GetCenterPoint()
        to_point    = frst_line.GetCenterPoint()

    else:
        main_column = Cylinder(build_ele, True, com_prop, attach_point, column_bottom, texture, column_radius, column_height, slab_height)
        next_column = Cylinder(build_ele, False, help_prop, attach_point, column_height, texture, next_col_radius, 1000, slab_height)

        from_point = to_point = Geometry.Point3D()

    main_column.create_geo()

    # Get intersection volume between main and next column
    base_column = Geometry.Move(main_column.create_geo(), Geometry.Vector3D(0, 0, column_height))
    next_column = Geometry.Move(next_column.create_geo(), Geometry.Vector3D(from_point, to_point))
    err, intersect_column = Geometry.Intersect(base_column, next_column)

    # Add object to view
    pyp_util.add_pythonpart_view_2d3d(main_column.add_view())

    if has_next_col:
        pyp_util.add_pythonpart_view_2d(BasisElements.ModelElement3D(help_prop, texture, intersect_column))

    # Create the handles
    if is_showing_handles:
        # Z rotation
        if choice == "rectangle":
            handle = HandleProperties(handle_id         = "ColumnRotationHandle",
                                      handle_point      = main_column.points_list[10],
                                      ref_point         = main_column.points_list[0],
                                      handle_param_data = [HandleParameterData("ColumnRotAngleZ", HandleParameterType.ANGLE)],
                                      handle_move_dir   = HandleDirection.ANGLE,
                                      info_text         = "Rotation suivant Z")
            handle_list.append(handle)

        for item in main_column.handles_prop:
            handle = HandleProperties(handle_id         = item.handle_id,
                                      handle_point      = item.handle_point,
                                      ref_point         = item.ref_point,
                                      handle_param_data = [HandleParameterData(item.handle_param_data, HandleParameterType.POINT_DISTANCE)],
                                      handle_move_dir   = item.handle_move_dir,
                                      distance_factor   = item.distance_factor,
                                      info_text         = item.handle_info_text
                                      )
            handle_list.append(handle)

    # Create the annotation
    if is_showing_annotation:
        # Set text value
        text = f"{column_id} {main_column.name_dim}"
        if column_concrete_gr_value > 4:
            text += f"\n{column_concrete_gr}"
        # Set origin of text
        origin = text_origin - main_column.points_list[0]
        # Text remains horizontal
        placement_mat = Geometry.Matrix3D()
        if choice == "rectangle":
            rotation_axis  = Geometry.Line3D(Geometry.Point3D(), Geometry.Point3D(0, 0, 1))
            rotation_angle = Geometry.Angle.FromDeg(-col_z_rotation)
            placement_mat.SetRotation(rotation_axis,rotation_angle)
        origin = Geometry.Transform(origin, placement_mat)
        # Transform Point3D to Point2D
        origin = Geometry.Point2D(origin)
        # Add text to view
        pyp_util.add_pythonpart_view_2d(BasisElements.TextElement(text_com_prop, text_prop, text, origin))

        text_handle = HandleProperties(handle_id         = "Text",
                                       handle_point      = text_origin,
                                       ref_point         = main_column.points_list[0],
                                       handle_param_data = [HandleParameterData("TextOrigin", HandleParameterType.POINT, False)],
                                       handle_move_dir   = HandleDirection.XYZ_DIR,
                                       info_text         = "Origine du texte"
                                       )
        text_handle.handle_type = IFWInput.ElementHandleType.HANDLE_SQUARE_RED
        handle_list.append(text_handle)

    # Create hatch
    if has_hatch:
        pyp_util.add_pythonpart_view_2d(BasisElements.HatchingElement(com_prop, hatch_prop, main_column.create_hatch_geo()))

    # Create fill
    if has_fill:
        pyp_util.add_pythonpart_view_2d(BasisElements.FillingElement(com_prop, fill_prop, main_column.create_hatch_geo()))

    # Create reinforcement
    if is_showing_reinf:
        reinf_ele_list = main_column.create_reinforcement()

        # Apply reinforcement properties
        for rebar in reinf_ele_list:
            rebar.SetCommonProperties(reinf_prop)

        pyp_util.add_reinforcement_elements(reinf_ele_list)

    #
    # Attributes
    #

    # Attribute set object @18358@
    attr_list.add_attribute(18358, "Column")

    # Code @18199@
    attr_list.add_attribute(18199, "ReinforcedConcreteColumn")

    # Trade @209@
    attr_list.add_attribute(209, 13)

    # Status @49@
    attr_list.add_attribute(49, 0)

    # Load bearing @573@
    attr_list.add_attribute(573, 1)

    # Concrete grade @1905@
    attr_list.add_attribute(1905, column_concrete_gr)

    # Geometry
    length, thickness, radius, height, surface, volume = main_column.calcul_dimensions()

    attr_list.add_attribute(220, length)
    attr_list.add_attribute(221, thickness)
    attr_list.add_attribute(107, radius)
    attr_list.add_attribute(222, height)
    attr_list.add_attribute(293, surface)
    attr_list.add_attribute(226, volume)

    #
    # Reinforcement attributes
    #

    if is_showing_reinf:
        weight, quantity, col_concr_cover, height, height_under_beam, \
            frst_long_rebars, scnd_long_rebars, length_long_rebars, \
                stirrup_A_placement, stirrup_B_placement, stirrup_C_placement, stirrup_sum_qtt_diam, stirrup_sum_dim, \
                    crosstie_along_length, crosstie_along_thick, \
                        next_col_dim, start_rebars_qtt, start_rebars_mid_length = main_column.create_reinf_attributes()

        # Weight of bar
        attr_list.add_attribute(756, weight)

        # Quantity
        attr_list.add_attribute(201, quantity)

        # Concrete cover => ALLFA_value_03
        attr_list.add_attribute(845, col_concr_cover)

        # Column dimensions => ALLFA_value_06
        attr_list.add_attribute(848, main_column.name_dim)

        # Height => ALLFA_value_07
        attr_list.add_attribute(849, height)

        # Height under beam => ALLFA_value_08
        attr_list.add_attribute(850, height_under_beam)

        # First longitudinal rebars => ALLFA_value_09
        attr_list.add_attribute(851, frst_long_rebars)

        # Second longitudinal rebars => ALLFA_value_10
        attr_list.add_attribute(852, scnd_long_rebars)

        # Length of longitudinal rebars => ALLFA_value_11
        attr_list.add_attribute(853, length_long_rebars)

        # Stirrup placement [A] => ALLFA_value_12
        attr_list.add_attribute(854, stirrup_A_placement)

        # Stirrup placement [B] => ALLFA_value_13
        attr_list.add_attribute(855, stirrup_B_placement)

        # Stirrup placement [C] => ALLFA_value_14
        attr_list.add_attribute(856, stirrup_C_placement)

        # Stirrup summary for quantity / diameter => ALLFA_value_15
        attr_list.add_attribute(857, stirrup_sum_qtt_diam)

        # Stirrup summary for dimensions => ALLFA_value_16
        attr_list.add_attribute(858, stirrup_sum_dim)

        # Crosstie along length => ALLFA_value_17
        attr_list.add_attribute(859, crosstie_along_length)

        # Crosstie along thickness => ALLFA_value_18
        attr_list.add_attribute(860, crosstie_along_thick)

        # Next column dimensions => ALLFA_value_19
        attr_list.add_attribute(861, next_col_dim)

        # Starter rebars quantity => ALLFA_value_20
        attr_list.add_attribute(862, start_rebars_qtt)

        # Starter rebars mid length => ALLFA_value_01
        attr_list.add_attribute(843, start_rebars_mid_length)

    attr_list.add_attributes_from_parameters(build_ele)
    pyp_util.add_attribute_list(attr_list)

    # Reference point
    placement_mat = Geometry.Matrix3D()
    if choice == "rectangle":
        rotation_axis  = Geometry.Line3D(Geometry.Point3D(), Geometry.Point3D(0, 0, 1))
        rotation_angle = Geometry.Angle.FromDeg(col_z_rotation)
        placement_mat.SetRotation(rotation_axis,rotation_angle)
    placement_mat.SetTranslation(Geometry.Vector3D(main_column.placement_pt))

    # Create the PythonPart
    model_ele_list = pyp_util.create_pythonpart(build_ele, placement_mat)

    return CreateElementResult(model_ele_list, handle_list)


def set_constructive_dispositions(build_ele      : BuildingElement,
                                  ctrl_prop_util : ControlPropertiesUtil) -> None:
    """Calcul of constructive dispositions

    Args:
        build_ele      : the building element
        ctrl_prop_util : control properties utility
    """
    # Set distance between rebars
    esp_min = 100
    esp_max = 400

    if build_ele.ChoiceRadioGroup.value == "rectangle":
        # Concrete section in cm²
        Ac = (build_ele.ColumnLength.value * build_ele.ColumnThick.value) * 1e-2
        # Rebars quantity
        length    = build_ele.ColumnLength.value - 2 * build_ele.ReinfConcreteCover.value
        thickness = build_ele.ColumnThick.value - 2 * build_ele.ReinfConcreteCover.value

        min_value_in_length = max(0, math.ceil(length / esp_max) - 1)
        max_value_in_length = max(min_value_in_length, math.floor(length / esp_min) - 1)

        min_value_in_thick = max(0, math.ceil(thickness / esp_max) - 1)
        max_value_in_thick = max(min_value_in_thick, math.floor(thickness / esp_min) - 1)

        if build_ele.ScndBarRectQttInLength.value > 0 or build_ele.ScndBarRectQttInThick.value > 0:
            main_stirrup_max_dist = min(20 * min(build_ele.FirstBarDiameter.value, build_ele.SecondBarDiameter.value), 400, min(build_ele.ColumnLength.value, build_ele.ColumnThick.value))
        else:
            main_stirrup_max_dist = min(20 * build_ele.FirstBarDiameter.value, 400, min(build_ele.ColumnLength.value, build_ele.ColumnThick.value))

        top_stirrup_length = max(build_ele.ColumnLength.value, build_ele.ColumnThick.value)

        build_ele.ScndBarRectQttInLength.value = min_value_in_length if build_ele.ScndBarRectQttInLength.value < min_value_in_length else (max_value_in_length if build_ele.ScndBarRectQttInLength.value > max_value_in_length else build_ele.ScndBarRectQttInLength.value)
        build_ele.ScndBarRectQttInThick.value = min_value_in_thick if build_ele.ScndBarRectQttInThick.value < min_value_in_thick else (max_value_in_thick if build_ele.ScndBarRectQttInThick.value > max_value_in_thick else build_ele.ScndBarRectQttInThick.value)

        # Change the min and max values ​​if they are different, otherwise reset and lock the value
        if min_value_in_length != max_value_in_length:
            ctrl_prop_util.set_min_value("ScndBarRectQttInLength", str(min_value_in_length))
            ctrl_prop_util.set_max_value("ScndBarRectQttInLength", str(max_value_in_length))
            ctrl_prop_util.set_enable_condition("ScndBarRectQttInLength", "True")
        else:
            ctrl_prop_util.set_min_value("ScndBarRectQttInLength", "0")
            ctrl_prop_util.set_max_value("ScndBarRectQttInLength", "10")
            ctrl_prop_util.set_enable_condition("ScndBarRectQttInLength", "False")

        # Change the min and max values ​​if they are different, otherwise reset and lock the value
        if min_value_in_thick != max_value_in_thick:
            ctrl_prop_util.set_min_value("ScndBarRectQttInThick", str(min_value_in_thick))
            ctrl_prop_util.set_max_value("ScndBarRectQttInThick", str(max_value_in_thick))
            ctrl_prop_util.set_enable_condition("ScndBarRectQttInThick", "True")
        else:
            ctrl_prop_util.set_min_value("ScndBarRectQttInThick", "0")
            ctrl_prop_util.set_max_value("ScndBarRectQttInThick", "10")
            ctrl_prop_util.set_enable_condition("ScndBarRectQttInThick", "False")

    else:
        # Concrete section in cm²
        Ac = (math.pi * build_ele.ColumnRadius.value ** 2) * 1e-2
        # Rebars quantity
        diameter = 2 * math.pi * (build_ele.ColumnRadius.value - build_ele.ReinfConcreteCover.value)

        min_value = max(4, math.ceil(diameter / esp_max))
        max_value = max(min_value, math.floor(diameter / esp_min))

        main_stirrup_max_dist = min(20 * build_ele.FirstBarDiameter.value, 400, 2 * build_ele.ColumnRadius.value)
        top_stirrup_length    = 2 * build_ele.ColumnRadius.value

        build_ele.RebarCircQtt.value = min_value if build_ele.RebarCircQtt.value < min_value else (max_value if build_ele.RebarCircQtt.value > max_value else build_ele.RebarCircQtt.value)

        # Change the min and max values ​​if they are different, otherwise reset and lock the value
        if min_value != max_value:
            ctrl_prop_util.set_min_value("RebarCircQtt", str(min_value))
            ctrl_prop_util.set_max_value("RebarCircQtt", str(max_value))
            ctrl_prop_util.set_enable_condition("RebarCircQtt", "True")
        else:
            ctrl_prop_util.set_min_value("RebarCircQtt", "0")
            ctrl_prop_util.set_max_value("RebarCircQtt", "10")
            ctrl_prop_util.set_enable_condition("RebarCircQtt", "False")

    # As min and As max in cm²
    build_ele.AsMinDouble.value = 0.002 * Ac
    build_ele.AsMaxDouble.value = 0.04 * Ac

    # Set distance between stirrups
    stirrup_list = build_ele.StirrupList.value

    end_stirrup_max_dist  = 0.6 * main_stirrup_max_dist
    bottom_stirrup_length = 2 * stirrup_list[0][1]

    ctrl_prop_util.set_max_value("MainStirrup", f",10,{main_stirrup_max_dist}")
    ctrl_prop_util.set_max_value("StirrupList", f",{end_stirrup_max_dist},,")

    stirrup_list[0] = stirrup_list[0]._replace(Length = float(bottom_stirrup_length))
    stirrup_list[1] = stirrup_list[1]._replace(Length = float(top_stirrup_length))


def calcul_as_real(build_ele : BuildingElement) -> None:
    """Calcul of As real

    Args:
        build_ele : the building element
    """
    if build_ele.ChoiceRadioGroup.value == "rectangle":
        as_frst_rebar = 4 * math.pi * (build_ele.FirstBarDiameter.value / 10) ** 2 / 4
        as_scnd_rebar = 2 * (build_ele.ScndBarRectQttInLength.value + build_ele.ScndBarRectQttInThick.value) * math.pi * (build_ele.SecondBarDiameter.value / 10) ** 2 / 4
        build_ele.AsRealDouble.value = as_frst_rebar + as_scnd_rebar
    else:
        build_ele.AsRealDouble.value = build_ele.RebarCircQtt.value * math.pi * (build_ele.FirstBarDiameter.value / 10) ** 2 / 4


class Objects3D:
    """Definition of class Objects3D
    """
    def __init__(self,
                 build_ele     : BuildingElement,
                 is_main_col   : bool,
                 object_prop   : BaseElements.CommonProperties,
                 attach_point  : int,
                 column_bottom : float,
                 texture       : BasisElements.TextureDefinition):
        self.build_ele      = build_ele
        self.is_main_col    = is_main_col
        self.object_prop    = object_prop
        self.geo            = None
        self.attach_point   = attach_point
        self.texture        = texture
        self.x_offset       = 0
        self.y_offset       = 0
        self.z_offset       = column_bottom
        self.points_list    = []
        self.reinf_ele_list = []


    def calcul_dimensions(self) -> tuple:
        pass


    def create_geo(self) -> Geometry.BRep3D:
        pass


    def create_hatch_geo(self) -> Geometry.Polygon2D:
        pass


    def add_view(self) -> BasisElements.ModelElement3D:
        object_3d = BasisElements.ModelElement3D(self.object_prop, self.texture, self.geo)
        return object_3d


    def attachment_point(self) -> Geometry.Point3D:
        pass


    def apply_transfo_matrix_to_handles(self) -> None:
        placement_mat = Geometry.Matrix3D()
        if self.__class__.__name__ == "Cuboid":
            rotation_axis  = Geometry.Line3D(Geometry.Point3D(), Geometry.Point3D(0, 0, 1))
            rotation_angle = Geometry.Angle.FromDeg(self.col_z_rotation)
            placement_mat.SetRotation(rotation_axis,rotation_angle)
        placement_mat.SetTranslation(Geometry.Vector3D(self.placement_pt))

        self.points_list = [Geometry.Transform(point, placement_mat) for point in self.points_list]


    def create_reinforcement(self) -> List[Reinforcement.BarPlacement]:
        self.reinf_ele = Reinforcement3D(self.build_ele)
        reinf_ele_list = self.reinf_ele.create_rebars()

        return reinf_ele_list


    def create_reinf_attributes(self) -> tuple:
        pass


class Handle:
    """Definition of class Handle
    """
    def __init__(self,
                 handle_id         : str,
                 handle_point      : Geometry.Point3D,
                 ref_point         : Geometry.Point3D,
                 handle_param_data : str,
                 handle_move_dir   : HandleDirection,
                 handle_info_text  : str,
                 distance_factor   : float):
        self.handle_id         = handle_id
        self.handle_point      = handle_point
        self.ref_point         = ref_point
        self.handle_param_data = handle_param_data
        self.handle_move_dir   = handle_move_dir
        self.handle_info_text  = handle_info_text
        self.distance_factor   = distance_factor


class Cuboid(Objects3D):
    """Definition of class Cuboid
    """
    def __init__(self,
                 build_ele      : BuildingElement,
                 is_main_col    : bool,
                 object_prop    : BaseElements.CommonProperties,
                 attach_point   : int,
                 column_bottom  : float,
                 texture        : BasisElements.TextureDefinition,
                 column_length  : float,
                 column_thick   : float,
                 column_height  : float,
                 col_z_rotation : float,
                 slab_height    : float):
        Objects3D.__init__(self, build_ele, is_main_col, object_prop, attach_point, column_bottom, texture)
        self.column_length  = column_length
        self.column_thick   = column_thick
        self.column_height  = column_height
        self.col_z_rotation = col_z_rotation
        self.slab_height    = slab_height
        self.name_dim       = f"{round(column_thick / 10)}x{round(column_length / 10)}"
        self.placement_pt   = self.attachment_point()
        # Set points list
        """
        Points List :
        5        6         7
          ---------------
          |              |
        3 |      8       | 4
          |              |
          ---------------
        0   10   1         2
        """
        self.points_list = [Geometry.Point3D(),                                                 # 0
                            Geometry.Point3D(self.column_length / 2, 0, 0),                     # 1
                            Geometry.Point3D(self.column_length, 0, 0),                         # 2
                            Geometry.Point3D(0, self.column_thick / 2, 0),                      # 3
                            Geometry.Point3D(self.column_length, self.column_thick / 2, 0),     # 4
                            Geometry.Point3D(0, self.column_thick, 0),                          # 5
                            Geometry.Point3D(self.column_length / 2, self.column_thick, 0),     # 6
                            Geometry.Point3D(self.column_length, self.column_thick, 0),         # 7
                            Geometry.Point3D(self.column_length / 2, self.column_thick / 2, 0), # 8
                            Geometry.Point3D(0, 0, self.column_height),                         # 9
                            Geometry.Point3D(self.column_length / 4, 0, 0),                     # 10
                            Geometry.Point3D(0, 0, self.column_height - self.slab_height)       # 11
                            ]
        self.apply_transfo_matrix_to_handles()
        # Set handles
        self.handles_prop  = [Handle("ColumnHeightHandle",
                                     self.points_list[9],
                                     self.points_list[0],
                                     "ColumnHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur",
                                     1
                                     ),
                              Handle("SlabHeightHandle",
                                     self.points_list[11],
                                     self.points_list[9],
                                     "SlabHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur Poutre / Dalle",
                                     1
                                     )
                              ]
        # Handle dictionary : [handle point, base point, factor] with 2 handles if in middle
        handle_length_dict = {1 : [self.points_list[7], self.points_list[5], 1],
                              2 : [[self.points_list[7], self.points_list[6], 2],
                                   [self.points_list[5], self.points_list[6], 2]],
                              3 : [self.points_list[5], self.points_list[7], 1],
                              4 : [self.points_list[4], self.points_list[3], 1],
                              5 : [[self.points_list[4], self.points_list[8], 2],
                                   [self.points_list[3], self.points_list[8], 2]],
                              6 : [self.points_list[3], self.points_list[4], 1],
                              7 : [self.points_list[2], self.points_list[0], 1],
                              8 : [[self.points_list[2], self.points_list[1], 2],
                                   [self.points_list[0], self.points_list[1], 2]],
                              9 : [self.points_list[0], self.points_list[2], 1]
                              }
        handle_thick_dict  = {1 : [self.points_list[2], self.points_list[7], 1],
                              2 : [self.points_list[1], self.points_list[6], 1],
                              3 : [self.points_list[0], self.points_list[5], 1],
                              4 : [[self.points_list[7], self.points_list[4], 2],
                                   [self.points_list[2], self.points_list[4], 2]],
                              5 : [[self.points_list[6], self.points_list[8], 2],
                                   [self.points_list[1], self.points_list[8], 2]],
                              6 : [[self.points_list[5], self.points_list[3], 2],
                                   [self.points_list[0], self.points_list[3], 2]],
                              7 : [self.points_list[7], self.points_list[2], 1],
                              8 : [self.points_list[6], self.points_list[1], 1],
                              9 : [self.points_list[5], self.points_list[0], 1]
                              }
        # Length handle
        if self.attach_point in [2, 5, 8]:
            handles_param = handle_length_dict[self.attach_point]
            for ensemble in handles_param:
                handle_pnt, base_pnt, factor = ensemble
                self.handles_prop.append(Handle("ColumnLengthHandle",
                                                handle_pnt,
                                                base_pnt,
                                                "ColumnLength",
                                                HandleDirection.X_DIR,
                                                "Longueur",
                                                factor
                                                )
                                         )
        else:
            handle_pnt, base_pnt, factor = handle_length_dict[self.attach_point]
            self.handles_prop.append(Handle("ColumnLengthHandle",
                                            handle_pnt,
                                            base_pnt,
                                            "ColumnLength",
                                            HandleDirection.X_DIR,
                                            "Longueur",
                                            factor
                                            )
                                     )
        # Thickness handle
        if self.attach_point in [4, 5, 6]:
            handles_param = handle_thick_dict[self.attach_point]
            for ensemble in handles_param:
                handle_pnt, base_pnt, factor = ensemble
                self.handles_prop.append(Handle("ColumnThickHandle",
                                                handle_pnt,
                                                base_pnt,
                                                "ColumnThick",
                                                HandleDirection.Y_DIR,
                                                "Largeur",
                                                factor
                                                )
                                         )
        else:
            handle_pnt, base_pnt, factor = handle_thick_dict[self.attach_point]
            self.handles_prop.append(Handle("ColumnThickHandle",
                                            handle_pnt,
                                            base_pnt,
                                            "ColumnThick",
                                            HandleDirection.Y_DIR,
                                            "Largeur",
                                            factor
                                            )
                                     )


    def calcul_dimensions(self) -> tuple:
        err, volume, surface, center_of_gravity = Geometry.CalcMass(self.geo)
        volume    = volume * 1e-9
        length    = self.column_length * 1e-3
        thickness = self.column_thick * 1e-3
        radius    = 0
        height    = self.column_height * 1e-3
        surface   = length * thickness

        return (length, thickness, radius, height, surface, volume)


    def create_geo(self) -> Geometry.BRep3D:
        placement = Geometry.AxisPlacement3D(Geometry.Point3D(),
                                             Geometry.Vector3D(1, 0, 0),
                                             Geometry.Vector3D(0, 0, 1)
                                             )
        self.geo  = Geometry.BRep3D.CreateCuboid(placement,
                                                 self.column_length,
                                                 self.column_thick,
                                                 self.column_height
                                                 )

        if not self.is_main_col:
            self.geo = Geometry.Move(self.geo, Geometry.Vector3D(0, 0, self.z_offset))

        return self.geo


    def create_hatch_geo(self) -> Geometry.Polygon2D:
        hatch_geo = Geometry.Polygon2D.CreateRectangle(Geometry.Point2D(),
                                                       Geometry.Point2D(self.column_length, self.column_thick)
                                                       )

        return hatch_geo


    def attachment_point(self) -> Geometry.Point3D:
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


    def create_reinf_attributes(self) -> tuple:
        # Init values
        weight                    = 0
        quantity                  = 0
        col_concr_cover           = ""
        height                    = ""
        height_under_beam         = ""
        frst_long_rebars          = ""
        scnd_long_rebars          = ""
        length_long_rebars        = ""
        stirrup_A_placement       = ""
        stirrup_B_placement       = ""
        stirrup_C_placement       = ""
        stirrup_sum_qtt_diam      = ""
        stirrup_sum_dim           = ""
        crosstie_along_length     = ""
        crosstie_along_thick      = ""
        next_col_dim              = ""
        start_rebars_qtt          = ""
        start_rebars_mid_length   = ""

        for rebar in self.reinf_ele.reinforcement:
            bending_shape = Reinforcement.BarPlacement.GetBendingShape(rebar)
            steel_grade   = bending_shape.GetSteelGrade()
            diameter      = bending_shape.GetDiameter()
            count         = rebar.GetBarCount()
            length        = bending_shape.GetShapePolyline()
            length        = Geometry.CalcLength(length) * 1e-3
            weight_per_ml = Reinforcement.ReinforcementSettings.GetBarWeight(steel_grade, diameter)
            weight       += count * length * weight_per_ml

        quantity = 1

        col_concr_cover = f"e={round(self.reinf_ele.concrete_cover / 10, 1)}cm"

        height = f"{round(self.reinf_ele.col_height / 10)}"

        height_under_beam = f"{round((self.reinf_ele.col_height - self.reinf_ele.slab_height) / 10)}"

        if (self.reinf_ele.scnd_bar_qtt_length + self.reinf_ele.scnd_bar_qtt_thick == 0):
            frst_long_rebars = f"4HA{self.reinf_ele.frst_bar_diam}"
            scnd_long_rebars = ""
        elif (self.reinf_ele.scnd_bar_qtt_length + self.reinf_ele.scnd_bar_qtt_thick > 0) and (self.reinf_ele.frst_bar_diam == self.reinf_ele.scnd_bar_diam):
            frst_long_rebars = f"{4 + (self.reinf_ele.scnd_bar_qtt_length + self.reinf_ele.scnd_bar_qtt_thick) * 2}HA{self.reinf_ele.frst_bar_diam}"
            scnd_long_rebars = ""
        else:
            frst_long_rebars = f"4HA{self.reinf_ele.frst_bar_diam}"
            scnd_long_rebars = f"{(self.reinf_ele.scnd_bar_qtt_length + self.reinf_ele.scnd_bar_qtt_thick) * 2}HA{self.reinf_ele.scnd_bar_diam}"

        length_long_rebars  = f"{round((self.reinf_ele.col_height - self.reinf_ele.concrete_cover) / 10)}"

        stirrup_A_placement = f"{self.reinf_ele.count_stirrup[2]} x {self.reinf_ele.count_stirrup[3]}"
        stirrup_B_placement = f"{self.reinf_ele.count_stirrup[0]} x {self.reinf_ele.count_stirrup[1]}"
        stirrup_C_placement = f"{self.reinf_ele.count_stirrup[4]} x {self.reinf_ele.count_stirrup[5]}"

        stirrup_qtt          = self.reinf_ele.count_stirrup[0] + self.reinf_ele.count_stirrup[2] + self.reinf_ele.count_stirrup[4]
        stirrup_sum_qtt_diam = f"{stirrup_qtt}HA{self.reinf_ele.main_stirrup[1]}"
        stirrup_sum_dim      = f"({round((self.reinf_ele.col_thick - self.reinf_ele.concrete_cover * 2)/ 10)}x{round((self.reinf_ele.col_length - self.reinf_ele.concrete_cover * 2)/ 10)})"

        if self.reinf_ele.count_crosstie['length'] > 0:
            crosstie_along_length = f"{stirrup_qtt * self.reinf_ele.count_crosstie['length']} x L={round((self.reinf_ele.col_thick - self.reinf_ele.concrete_cover * 2)/ 10)}"
        if self.reinf_ele.count_crosstie['thickness'] > 0:
            crosstie_along_thick  = f"{stirrup_qtt * self.reinf_ele.count_crosstie['thickness']} x L={round((self.reinf_ele.col_length - self.reinf_ele.concrete_cover * 2)/ 10)}"

        if self.reinf_ele.has_next_col:
            next_col_dim = f"{round(self.reinf_ele.next_col_thick / 10)} x {round(self.reinf_ele.next_col_length / 10)}"

            start_rebars_qtt        = f"{self.reinf_ele.starter_bar_qtt}HA{self.reinf_ele.starter_bar_diam}"
            start_rebars_mid_length = f"{round((self.reinf_ele.starter_bar_length / 2)/ 10)}"

        return (weight,
                quantity,
                col_concr_cover,
                height,
                height_under_beam,
                frst_long_rebars,
                scnd_long_rebars,
                length_long_rebars,
                stirrup_A_placement,
                stirrup_B_placement,
                stirrup_C_placement,
                stirrup_sum_qtt_diam,
                stirrup_sum_dim,
                crosstie_along_length,
                crosstie_along_thick,
                next_col_dim,
                start_rebars_qtt,
                start_rebars_mid_length
                )


class Cylinder(Objects3D):
    """Definition of class Cylinder
    """
    def __init__(self,
                 build_ele     : BuildingElement,
                 is_main_col   : bool,
                 object_prop   : BaseElements.CommonProperties,
                 attach_point  : int,
                 column_bottom : float,
                 texture       : BasisElements.TextureDefinition,
                 column_rad    : float,
                 column_height : float,
                 slab_height   : float):
        Objects3D.__init__(self, build_ele, is_main_col, object_prop, attach_point, column_bottom, texture)
        self.column_radius = column_rad
        self.column_height = column_height
        self.slab_height   = slab_height
        self.name_dim      = f"Ø{round(2 * column_rad / 10)}"
        self.placement_pt  = self.attachment_point()
        # Set points list
        """
        Points List :
        6        7         8
          ---------------
          |              |
        4 |      0       | 5
          |              |
          ---------------
        1        2         3
        """
        self.points_list = [Geometry.Point3D(),                                             # 0
                            Geometry.Point3D(-self.column_radius, -self.column_radius, 0),  # 1
                            Geometry.Point3D(0, -self.column_radius, 0),                    # 2
                            Geometry.Point3D(self.column_radius, -self.column_radius, 0),   # 3
                            Geometry.Point3D(-self.column_radius, 0, 0),                    # 4
                            Geometry.Point3D(self.column_radius, 0, 0),                     # 5
                            Geometry.Point3D(-self.column_radius, self.column_radius, 0),   # 6
                            Geometry.Point3D(0, self.column_radius, 0),                     # 7
                            Geometry.Point3D(self.column_radius, self.column_radius, 0),    # 8
                            Geometry.Point3D(0, 0, self.column_height),                     # 9
                            Geometry.Point3D(0, 0, self.column_height - self.slab_height)   # 10
                            ]
        self.apply_transfo_matrix_to_handles()
        # Set handles
        self.handles_prop  = [Handle("ColumnHeightHandle",
                                     self.points_list[9],
                                     self.points_list[0],
                                     "ColumnHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur",
                                     1
                                     ),
                              Handle("SlabHeightHandle",
                                     self.points_list[10],
                                     self.points_list[9],
                                     "SlabHeight",
                                     HandleDirection.Z_DIR,
                                     "Hauteur Poutre / Dalle",
                                     1
                                     )
                              ]
        # Handle dictionary : [handle point, base point, text, factor] with 2 handles if in middle
        handle_radius_dict = {1 : [self.points_list[8], self.points_list[6], "Diamètre", 0.5],
                              2 : [[self.points_list[8], self.points_list[7], "Rayon", 1],
                                   [self.points_list[6], self.points_list[7], "Rayon", 1]],
                              3 : [self.points_list[6], self.points_list[8], "Diamètre", 0.5],
                              4 : [self.points_list[5], self.points_list[4], "Diamètre", 0.5],
                              5 : [[self.points_list[5], self.points_list[0], "Rayon", 1],
                                   [self.points_list[4], self.points_list[0], "Rayon", 1]],
                              6 : [self.points_list[4], self.points_list[5], "Diamètre", 0.5],
                              7 : [self.points_list[3], self.points_list[1], "Diamètre", 0.5],
                              8 : [[self.points_list[3], self.points_list[2], "Rayon", 1],
                                   [self.points_list[1], self.points_list[2], "Rayon", 1]],
                              9 : [self.points_list[1], self.points_list[3], "Diamètre", 0.5]
                              }
        # Radius handle
        if self.attach_point in [2, 5, 8]:
            handles_param = handle_radius_dict[self.attach_point]
            for ensemble in handles_param:
                handle_pnt, base_pnt, text, factor = ensemble
                self.handles_prop.append(Handle("ColumnRadiusHandle",
                                                handle_pnt,
                                                base_pnt,
                                                "ColumnRadius",
                                                HandleDirection.X_DIR,
                                                text,
                                                factor
                                                )
                                         )
        else:
            handle_pnt, base_pnt, text, factor = handle_radius_dict[self.attach_point]
            self.handles_prop.append(Handle("ColumnRadiusHandle",
                                            handle_pnt,
                                            base_pnt,
                                            "ColumnRadius",
                                            HandleDirection.X_DIR,
                                            text,
                                            factor
                                            )
                                     )


    def calcul_dimensions(self) -> tuple:
        err, volume, surface, center_of_gravity = Geometry.CalcMass(self.geo)
        volume    = volume * 1e-9
        length    = 0
        thickness = 0
        radius    = self.column_radius * 1e-3
        height    = self.column_height * 1e-3
        surface   = math.pi * radius ** 2

        return (length, thickness, radius, height, surface, volume)


    def create_geo(self) -> Geometry.BRep3D:
        placement = Geometry.AxisPlacement3D(Geometry.Point3D(),
                                             Geometry.Vector3D(1, 0, 0),
                                             Geometry.Vector3D(0, 0, 1)
                                             )
        self.geo  = Geometry.BRep3D.CreateCylinder(placement,
                                                   self.column_radius,
                                                   self.column_height
                                                   )

        if not self.is_main_col:
            self.geo = Geometry.Move(self.geo, Geometry.Vector3D(0, 0, self.z_offset))

        return self.geo


    def create_hatch_geo(self) -> Geometry.Polygon2D:
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


    def attachment_point(self) -> Geometry.Point3D:
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


    def create_reinf_attributes(self) -> tuple:
        # Init values
        weight                    = 0
        quantity                  = 0
        col_concr_cover           = ""
        height                    = ""
        height_under_beam         = ""
        frst_long_rebars          = ""
        scnd_long_rebars          = ""
        length_long_rebars        = ""
        stirrup_A_placement       = ""
        stirrup_B_placement       = ""
        stirrup_C_placement       = ""
        stirrup_sum_qtt_diam      = ""
        stirrup_sum_dim           = ""
        crosstie_along_length     = ""
        crosstie_along_thick      = ""
        next_col_dim              = ""
        start_rebars_qtt          = ""
        start_rebars_mid_length   = ""

        for rebar in self.reinf_ele.reinforcement:
            bending_shape = Reinforcement.BarPlacement.GetBendingShape(rebar)
            steel_grade   = bending_shape.GetSteelGrade()
            diameter      = bending_shape.GetDiameter()
            count         = rebar.GetBarCount()
            length        = bending_shape.GetShapePolyline()
            length        = Geometry.CalcLength(length) * 1e-3
            weight_per_ml = Reinforcement.ReinforcementSettings.GetBarWeight(steel_grade, diameter)
            weight       += count * length * weight_per_ml

        quantity = 1

        col_concr_cover = f"e={round(self.reinf_ele.concrete_cover / 10, 1)}cm"

        height = f"{round(self.reinf_ele.col_height / 10)}"

        height_under_beam = f"{round((self.reinf_ele.col_height - self.reinf_ele.slab_height) / 10)}"

        frst_long_rebars = f"{self.reinf_ele.rebar_qtt_circ}HA{self.reinf_ele.frst_bar_diam}"

        length_long_rebars  = f"{round((self.reinf_ele.col_height - self.reinf_ele.concrete_cover) / 10)}"

        stirrup_A_placement = f"{self.reinf_ele.count_stirrup[2]} x {self.reinf_ele.count_stirrup[3]}"
        stirrup_B_placement = f"{self.reinf_ele.count_stirrup[0]} x {self.reinf_ele.count_stirrup[1]}"
        stirrup_C_placement = f"{self.reinf_ele.count_stirrup[4]} x {self.reinf_ele.count_stirrup[5]}"

        stirrup_qtt          = self.reinf_ele.count_stirrup[0] + self.reinf_ele.count_stirrup[2] + self.reinf_ele.count_stirrup[4]
        stirrup_sum_qtt_diam = f"{stirrup_qtt}HA{self.reinf_ele.main_stirrup[1]}"
        stirrup_sum_dim      = f"(Ø{round((2 * (self.reinf_ele.col_radius - self.reinf_ele.concrete_cover)/ 10))})"

        if self.reinf_ele.has_next_col:
            next_col_dim = f"Ø{round(2 * self.reinf_ele.next_col_radius / 10)}"

            start_rebars_qtt        = f"{self.reinf_ele.starter_bar_qtt}HA{self.reinf_ele.starter_bar_diam}"
            start_rebars_mid_length = f"{round((self.reinf_ele.starter_bar_length / 2)/ 10)}"

        return (weight,
                quantity,
                col_concr_cover,
                height,
                height_under_beam,
                frst_long_rebars,
                scnd_long_rebars,
                length_long_rebars,
                stirrup_A_placement,
                stirrup_B_placement,
                stirrup_C_placement,
                stirrup_sum_qtt_diam,
                stirrup_sum_dim,
                crosstie_along_length,
                crosstie_along_thick,
                next_col_dim,
                start_rebars_qtt,
                start_rebars_mid_length
                )


class Reinforcement3D:
    """Definition of class Reinforcement3D
    """
    def __init__(self,
                 build_ele  : BuildingElement):

        self.reinforcement = []

        self.choice = build_ele.ChoiceRadioGroup.value

        self.base_pnt    = Geometry.Point3D()
        self.col_length  = build_ele.ColumnLength.value
        self.col_thick   = build_ele.ColumnThick.value
        self.col_radius  = build_ele.ColumnRadius.value
        self.col_height  = build_ele.ColumnHeight.value
        self.slab_height = build_ele.SlabHeight.value

        self.has_next_col    = build_ele.NextColumnCheckBox.value
        self.next_col_length = build_ele.NextColumnLength.value
        self.next_col_thick  = build_ele.NextColumnThick.value
        self.next_col_radius = build_ele.NextColumnRadius.value

        self.concrete_grade = build_ele.ConcreteGrade.value
        self.concrete_cover = build_ele.ReinfConcreteCover.value

        self.bending_rol = 4

        self.frst_bar_diam        = build_ele.FirstBarDiameter.value
        self.scnd_bar_diam        = build_ele.SecondBarDiameter.value
        self.scnd_bar_qtt_length  = build_ele.ScndBarRectQttInLength.value
        self.scnd_bar_qtt_thick   = build_ele.ScndBarRectQttInThick.value
        self.rebar_qtt_circ       = build_ele.RebarCircQtt.value
        self.starter_bar_diam     = build_ele.StarterBarDiameter.value
        self.starter_bar_qtt      = build_ele.StterBarQtt.value
        self.starter_bar_length   = build_ele.StarterBarLength.value

        self.main_stirrup = build_ele.MainStirrup.value
        self.stirrup_list = build_ele.StirrupList.value

        self.placement_regions       = []
        self.region_start_end_points = []
        self.count_stirrup           = []
        self.count_crosstie          = {'length' : 0, 'thickness' : 0}


    def create_rebars(self) -> List[Reinforcement.BarPlacement]:

        if self.choice == "rectangle":

            #
            # Stirrups
            #

            cover_props = ConcreteCoverProperties.all(self.concrete_cover)

            stirrup_shape_props = ReinforcementShapeProperties.rebar(self.main_stirrup[1],
                                                                     self.bending_rol,
                                                                     -1,
                                                                     self.concrete_grade,
                                                                     Reinforcement.BendingShapeType.Stirrup
                                                                     )

            stirrup_shape = GeneralShapeBuilder.create_stirrup(self.col_length,
                                                               self.col_thick,
                                                               RotationUtil(0, 0, 0),
                                                               stirrup_shape_props,
                                                               cover_props,
                                                               Reinforcement.StirrupType.Column
                                                               )

            if stirrup_shape.IsValid():
                self.create_stirrups(stirrup_shape)

            #
            # Longitudinals rebars
            #

            place_util = BarShapePlacementUtil()
            place_util.add_shape("stirrup", stirrup_shape)

            # First longitudinals rebars (in corners)
            shape = self.create_longitudinal_shape(self.frst_bar_diam)

            for corner in range(2,6):
                placement_pnt = place_util.get_placement_in_corner("stirrup",
                                                                   corner,
                                                                   shape.GetDiameter() * 1.3, # apply a factor for the rebar's real footprint
                                                                   RotationAngles(0, 0, 0)
                                                                   )
                # Move shape to the placement point
                shape.Move(Geometry.Vector3D(placement_pnt))
                # Create rebar
                rebar = Reinforcement.BarPlacement(
                    1,
                    1,
                    Geometry.Vector3D(),
                    Geometry.Point3D(),
                    Geometry.Point3D(),
                    shape
                    )
                # Shape back to origin, ready for next placement
                shape.Move(Geometry.Vector3D(placement_pnt, Geometry.Point3D()))

                self.reinforcement.append(rebar)

            # Second longitudinals rebars (in length)
            shape = self.create_longitudinal_shape(self.scnd_bar_diam)

            if self.scnd_bar_qtt_length > 0:
                self.create_scnd_longitudinal_rebars([3, 5], "length", place_util, shape, self.scnd_bar_qtt_length)

            # Second longitudinals rebars (in thickness)
            if self.scnd_bar_qtt_thick > 0:
                self.create_scnd_longitudinal_rebars([4, 6], "thickness", place_util, shape, self.scnd_bar_qtt_thick)


        else:

            #
            # Stirrups
            #

            stirrup_shape_props = ReinforcementShapeProperties.rebar(self.main_stirrup[1],
                                                                     self.bending_rol,
                                                                     -1,
                                                                     self.concrete_grade,
                                                                     Reinforcement.BendingShapeType.Stirrup
                                                                     )

            stirrup_shape = GeneralShapeBuilder.create_circle_stirrup_with_user_hooks(self.col_radius,
                                                                                      RotationUtil(0, 0, -10),
                                                                                      stirrup_shape_props,
                                                                                      self.concrete_cover,
                                                                                      100,
                                                                                      100,
                                                                                      90,
                                                                                      100,
                                                                                      90
                                                                                      )

            if stirrup_shape.IsValid():
                self.create_stirrups(stirrup_shape)

            #
            # Longitudinals rebars
            #

            shape = self.create_longitudinal_shape(self.frst_bar_diam)

            if shape.IsValid():
                placement_line = Geometry.Line3D(0, 0, 0, self.col_radius - self.concrete_cover - (self.main_stirrup[1] / 2) - (self.frst_bar_diam * 1.3), 0, 0)
                angle          = Geometry.Angle()
                angle.Deg      = 360 / self.rebar_qtt_circ
                rotation_axis  = Geometry.Line3D(Geometry.Point3D(),
                                                 Geometry.Point3D(0, 0, 1)
                                                 )
                transformation_matrix = Geometry.Matrix3D()

                for i in range(self.rebar_qtt_circ):
                    transformation_matrix.SetRotation(rotation_axis, angle)
                    placement_line = Geometry.Transform(placement_line, transformation_matrix)
                    # Move shape to the placement point
                    shape.Move(Geometry.Vector3D(Geometry.Point3D(), placement_line.EndPoint))
                    # Create rebar
                    rebar = Reinforcement.BarPlacement(
                        1,
                        1,
                        Geometry.Vector3D(),
                        Geometry.Point3D(),
                        Geometry.Point3D(),
                        shape
                        )
                    # Shape back to origin, ready for next placement
                    shape.Move(Geometry.Vector3D(placement_line.EndPoint, Geometry.Point3D()))

                    self.reinforcement.append(rebar)

        self.create_starter_rebars()

        return self.reinforcement


    def create_placement_regions(self) -> None:
        # Set regions with length, distance between stirrups and diameter
        self.placement_regions = [(self.stirrup_list[0][2], self.stirrup_list[0][1], self.main_stirrup[1]),
                                  (0, self.main_stirrup[2], self.main_stirrup[1]), # 0 => length is calculated automatically
                                  (self.stirrup_list[1][2], self.stirrup_list[1][1], self.main_stirrup[1])
                                  ]

        self.region_start_end_points = LinearBarBuilder.calculate_length_of_regions(
            self.placement_regions,
            Geometry.Point3D(),
            Geometry.Point3D(0, 0, self.col_height - self.slab_height),
            50,
            50
            )


    def create_stirrups(self,
                        shape : Reinforcement.BendingShape) -> None:

        if not self.region_start_end_points:
            self.create_placement_regions()

        for index, start_end_point in enumerate(self.region_start_end_points):
            region_start_point, region_end_point = start_end_point

            stirrup = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                index + 1,
                shape,
                region_start_point,
                region_end_point,
                0,
                0,
                self.placement_regions[index][1]
                )

            # Save the number of stirrups with spacing
            self.count_stirrup.append(stirrup.GetBarCount())
            self.count_stirrup.append(round(self.placement_regions[index][1] / 10))

            self.reinforcement.append(stirrup)


    def create_longitudinal_shape(self,
                                  diameter : int) -> Reinforcement.BendingShape:
        shape_props = ReinforcementShapeProperties.rebar(diameter,
                                                         self.bending_rol,
                                                         -1,
                                                         self.concrete_grade,
                                                         Reinforcement.BendingShapeType.LongitudinalBar
                                                         )

        cover_props = ConcreteCoverProperties.left_right_bottom(0, # bottom after rotation
                                                                self.concrete_cover, # top after rotation
                                                                0
                                                                )

        shape = GeneralShapeBuilder.create_longitudinal_shape_with_hooks(self.col_height,
                                                                         RotationUtil(0, -90, 0),
                                                                         shape_props,
                                                                         cover_props,
                                                                         -1,
                                                                         -1
                                                                         )

        return shape


    def create_scnd_longitudinal_rebars(self,
                                        list_sides         : List[int],
                                        distrib_along_side : str,
                                        place_util         : BarShapePlacementUtil,
                                        shape              : Reinforcement.BendingShape,
                                        qtt_rebars         : int) -> None:
        # Set crosstie shape
        if not self.region_start_end_points:
            self.create_placement_regions()

        if distrib_along_side == "length":
            length       = self.col_thick
            model_angles = RotationUtil(0, 0, -90)
        else:
            length       = self.col_length
            model_angles = RotationUtil(0, 0, 0)

        cross_shape_props = ReinforcementShapeProperties.rebar(self.main_stirrup[1],
                                                                self.bending_rol,
                                                                -1,
                                                                self.concrete_grade,
                                                                Reinforcement.BendingShapeType.LongitudinalBar
                                                                )

        cover_props = ConcreteCoverProperties.all(self.concrete_cover)

        cross_shape = GeneralShapeBuilder.create_longitudinal_shape_with_user_hooks(length,
                                                                                    model_angles,
                                                                                    cross_shape_props,
                                                                                    cover_props,
                                                                                    0,
                                                                                    0,
                                                                                    180,
                                                                                    180
                                                                                    )
        # Set longitudinal rebars
        for side in list_sides:
            placement_line, placement_cover_left, placement_cover_right = \
                place_util.get_placement_in_side_corners("stirrup",
                                                         side,
                                                         shape.GetDiameter() * 1.3, # apply a factor for the rebar's real footprint
                                                         RotationAngles(0, 0, 0)
                                                         )
            placement_line = Geometry.Line3D(placement_line)
            # Adjustment of the placement line to start from the axis of the corner rebars
            placement_line.TrimStart(self.frst_bar_diam * 1.3 / 2)
            placement_line.TrimEnd(self.frst_bar_diam * 1.3 / 2)
            # Calcul of distance between rebars
            distance = Geometry.Point3D.GetDistance(placement_line.StartPoint, placement_line.EndPoint) / (qtt_rebars + 1)
            # Correction for center distance between rebars
            distance -= self.scnd_bar_diam / 2

            rebar = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                2,
                shape,
                placement_line.StartPoint,
                placement_line.EndPoint,
                distance,
                distance,
                qtt_rebars
                )

            self.reinforcement.append(rebar)

        # Crosstie every rebar if distance > 15cm
        if distance < 150:
            start = 1 # only odd numbers
            step  = 2 # one rebar of two
        else:
            start = 0
            step  = 1 # all rebars

        self.count_crosstie[distrib_along_side] = 0

        for bar in range(start, qtt_rebars, step):
            placement = (distance + self.main_stirrup[1]) * (bar + 1)

            for index, start_end_point in enumerate(self.region_start_end_points):
                region_start_point, region_end_point = start_end_point

                if distrib_along_side == "length":
                    from_point = Geometry.Point3D(placement, length, region_start_point.Z + 10)
                    to_point   = Geometry.Point3D(placement, length, region_end_point.Z + 10)
                else:
                    from_point = Geometry.Point3D(0, placement, region_start_point.Z - 15)
                    to_point   = Geometry.Point3D(0, placement, region_end_point.Z - 15)

                crosstie = LinearBarBuilder.create_linear_bar_placement_from_to_by_dist(
                    index + 10,
                    cross_shape,
                    from_point,
                    to_point,
                    0,
                    0,
                    self.placement_regions[index][1]
                    )

                self.reinforcement.append(crosstie)

            # Save the number of crossties with side
            self.count_crosstie[distrib_along_side] += 1


    def create_starter_rebars(self) -> None:
        if self.has_next_col:
            shape_props = ReinforcementShapeProperties.rebar(self.starter_bar_diam,
                                                             self.bending_rol,
                                                             -1,
                                                             self.concrete_grade,
                                                             Reinforcement.BendingShapeType.LongitudinalBar
                                                             )

            cover_props = ConcreteCoverProperties.all(0)

            shape = GeneralShapeBuilder.create_longitudinal_shape_with_hooks(self.starter_bar_length,
                                                                             RotationUtil(0, -90, 0),
                                                                             shape_props,
                                                                             cover_props,
                                                                             -1,
                                                                             -1
                                                                             )

            if shape.IsValid():
                placement_z = self.col_height - self.starter_bar_length / 2

                if self.choice == "rectangle":
                    # Create intersection polygon
                    intersect_length  = min(self.col_length, self.next_col_length) - 100
                    intersect_thick   = min(self.col_thick, self.next_col_thick) - 100
                    intersect_polygon = Geometry.Polygon2D.CreateRectangle(Geometry.Point2D(), Geometry.Point2D(intersect_length, intersect_thick))
                    # Get center point of columns
                    frst_line   = Geometry.Line2D(0, 0, self.col_length, self.col_thick)
                    scnd_line   = Geometry.Line2D(0, 0, intersect_length, intersect_thick)
                    from_point  = scnd_line.GetCenterPoint()
                    to_point    = frst_line.GetCenterPoint()
                    # Align columns center point
                    intersect_polygon = Geometry.Move(intersect_polygon, Geometry.Vector2D(from_point, to_point))
                    # Get all sides
                    err, list_lines = intersect_polygon.GetSegments()
                    """
                    placement of polygon segments
                    [O] => bottom
                    [1] => right
                    [2] => top
                    [3] => left
                    """
                    # Keep only the highest sides
                    if intersect_length >= intersect_thick:
                        list_lines = [line for index, line in enumerate(list_lines) if index not in [1, 3]]
                    else:
                        list_lines = [line for index, line in enumerate(list_lines) if index not in [0, 2]]
                    # Rebards placement on the sides
                    for line in list_lines:
                        rebar = LinearBarBuilder.create_linear_bar_placement_from_to_by_count(
                            1,
                            shape,
                            Geometry.Point3D(0, 0, placement_z) + Geometry.Point3D(line.GetStartPoint()),
                            Geometry.Point3D(0, 0, placement_z) + Geometry.Point3D(line.GetEndPoint()),
                            0,
                            0,
                            math.floor(self.starter_bar_qtt / 2)
                            )

                        self.reinforcement.append(rebar)

                    # If odd quantity of starter rebars add the last one at the center point
                    if (self.starter_bar_qtt % 2) != 0:
                        shape.Move(Geometry.Vector3D(Geometry.Point3D(), Geometry.Point3D(0, 0, placement_z) + Geometry.Point3D(frst_line.GetCenterPoint())))
                        rebar = Reinforcement.BarPlacement(
                            1,
                            1,
                            Geometry.Vector3D(),
                            Geometry.Point3D(),
                            Geometry.Point3D(),
                            shape
                            )
                        self.reinforcement.append(rebar)

                else:
                    from_point = Geometry.Point3D(0, 0, placement_z)
                    to_point   = Geometry.Point3D(min(self.col_radius, self.next_col_radius) - 100, 0, placement_z)

                    placement_line = Geometry.Line3D(from_point, to_point)
                    angle          = Geometry.Angle()
                    angle.Deg      = 360 / self.starter_bar_qtt
                    rotation_axis  = Geometry.Line3D(Geometry.Point3D(),
                                                    Geometry.Point3D(0, 0, 1)
                                                    )
                    transformation_matrix = Geometry.Matrix3D()

                    for i in range(self.starter_bar_qtt):
                        transformation_matrix.SetRotation(rotation_axis, angle)
                        placement_line = Geometry.Transform(placement_line, transformation_matrix)
                        # Move shape to the placement point
                        shape.Move(Geometry.Vector3D(Geometry.Point3D(), placement_line.EndPoint))
                        # Create rebar
                        rebar = Reinforcement.BarPlacement(
                            1,
                            1,
                            Geometry.Vector3D(),
                            Geometry.Point3D(),
                            Geometry.Point3D(),
                            shape
                            )
                        # Shape back to origin, ready for next placement
                        shape.Move(Geometry.Vector3D(placement_line.EndPoint, Geometry.Point3D()))

                        self.reinforcement.append(rebar)
