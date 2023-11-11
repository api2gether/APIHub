<?xml version="1.0" encoding="utf-8"?>

<Element>

    <Script>
        <Name>APIHub\objects_3D.py</Name>
        <Title>Objects3D</Title>
        <Version>2.0</Version>
    </Script>

    <Page>

        <Name>Page1</Name>
        <Text>Général</Text>

		<Parameter>
			<Name>ColumnId</Name>
			<Text>Repère</Text>
			<Value>P01</Value>
			<ValueType>Attribute</ValueType>
			<AttributeId>18222</AttributeId>
			<FontFaceCode>1</FontFaceCode>
		</Parameter>

		<Parameter>
			<Name>Separator</Name>
			<ValueType>Separator</ValueType>
		</Parameter>

        <Parameter>
            <Name>ConcreteGrade</Name>
            <Text>Classe de béton</Text>
            <Value>-1</Value>
            <ValueType>ReinfConcreteGrade</ValueType>
        </Parameter>

        <Parameter>
            <Name>GeometryExpander</Name>
            <Text>Géométrie</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
				<Name>ChoiceRadioGroup</Name>
				<Text>Forme :</Text>
				<Value>rectangle</Value>
				<ValueType>RadioButtonGroup</ValueType>

			<Parameter>
				<Name>ChoiceRectColumn</Name>
				<Text>rectangulaire</Text>
				<Value>rectangle</Value>
				<ValueType>RadioButton</ValueType>
			</Parameter>

			<Parameter>
				<Name>ChoiceCircColumn</Name>
				<Text>circulaire</Text>
				<Value>circle</Value>
				<ValueType>RadioButton</ValueType>
			</Parameter>
		</Parameter>

			<Parameter>
				<Name>ChoiceSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>ColumnLength</Name>
				<Text>Longueur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>400.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ColumnThick</Name>
				<Text>Largeur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>400.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ColumnRadius</Name>
				<Text>Rayon</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>300.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "circle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ColumnHeight</Name>
				<Text>Hauteur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>-1</Value>
				<ValueType>Length</ValueType>
				<Constraint>PlaneReferences</Constraint>
			</Parameter>

			<Parameter>
				<Name>PlaneReferences</Name>
				<Text> </Text>
				<Value></Value>
				<ValueType>PlaneReferences</ValueType>
				<ValueDialog>PlaneReferences</ValueDialog>
				<Constraint>ColumnHeight</Constraint>
			</Parameter>

        </Parameter>

		<Parameter>
            <Name>AttachmentExpander</Name>
            <Text>Accrochage</Text>
            <ValueType>Expander</ValueType>

        <Parameter>
            <Name>AttachmentPointButtonRow</Name>
            <Text>Point d'accrochage</Text>
            <ValueType>Row</ValueType>

				<Parameter>
					<Name>AttachmentPoint</Name>
					<Text>Attachment point index</Text>
					<Value>5</Value>
					<ValueType>RefPointButton</ValueType>
				</Parameter>
            </Parameter>

		</Parameter>

        <Parameter>
            <Name>FormatExpander</Name>
            <Text>Format</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>UseGlobalProperties</Name>
                <Text>Utiliser les paramètres courants</Text>
                <Value>True</Value>
                <ValueType>CheckBox</ValueType>
            </Parameter>

            <Parameter>
                <Name>CommonProperties</Name>
                <Text></Text>
                <Value></Value>
                <ValueType>CommonProperties</ValueType>
                <Visible>UseGlobalProperties == False</Visible>
            </Parameter>

			<Parameter>
				<Name>HatchCheckBox</Name>
				<Text>Hachurage</Text>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>HatchStyle</Name>
				<Text>Style d'hachurage</Text>
				<Value>-1</Value>
				<ValueType>Hatch</ValueType>
				<Visible>HatchCheckBox == True</Visible>
			</Parameter>

			<Parameter>
				<Name>FillCheckBox</Name>
				<Text>Remplissage</Text>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>FillColor</Name>
				<Text>Couleur du remplissage</Text>
				<Value>-1</Value>
				<ValueType>Color</ValueType>
				<Visible>FillCheckBox == True</Visible>
			</Parameter>

        </Parameter>

    </Page>

	<Page>

		<Name>Page2</Name>
		<Text>Annotation</Text>

		<Parameter>
            <Name>ShowTextCheckBox</Name>
            <Text>Afficher la légende</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

        <Parameter>
            <Name>TextExpander</Name>
            <Text>Format</Text>
            <ValueType>Expander</ValueType>
			<Visible>ShowTextCheckBox == True</Visible>

			<Parameter>
				<Name>TextCommonProperties</Name>
				<Text></Text>
				<Value></Value>
				<ValueType>CommonProperties</ValueType>
			</Parameter>

			<Parameter>
				<Name>TextSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>TextHeight</Name>
				<Text>Hauteur</Text>
				<Value>4</Value>
				<ValueType>Length</ValueType>
			</Parameter>

			<Parameter>
				<Name>TextAlignment</Name>
				<Text>Alignement</Text>
				<Value>Aligner à Gauche</Value>
				<ValueList>Aligner à Gauche|Centrer|Aligner à Droite</ValueList>
				<ValueType>StringComboBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>TextOrigin</Name>
				<Text> </Text>
				<Value>Point3D(0, -1000, 0)</Value>
				<ValueType>Point3D</ValueType>
				<Visible>False</Visible>
			</Parameter>

		</Parameter>

	</Page>

</Element>
