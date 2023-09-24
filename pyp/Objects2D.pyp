<?xml version="1.0" encoding="utf-8"?>

<Element>

    <Script>
        <Name>APIHub\objects_2D.py</Name>
        <Title>Objects2D</Title>
        <Version>2.0</Version>
    </Script>

    <Page>

        <Name>Page1</Name>
        <Text>Général</Text>

        <Parameter>
            <Name>GeometryExpander</Name>
            <Text>Géométrie</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
				<Name>ChoiceRadioGroup</Name>
				<Text>Je souhaite :</Text>
				<Value>line</Value>
				<ValueType>RadioButtonGroup</ValueType>

				<Parameter>
					<Name>ChoiceLine</Name>
					<Text>une ligne</Text>
					<Value>line</Value>
					<ValueType>RadioButton</ValueType>
				</Parameter>

				<Parameter>
					<Name>ChoiceRectangle</Name>
					<Text>un rectangle</Text>
					<Value>rectangle</Value>
					<ValueType>RadioButton</ValueType>
				</Parameter>

				<Parameter>
					<Name>ChoiceCircle</Name>
					<Text>un cercle</Text>
					<Value>circle</Value>
					<ValueType>RadioButton</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ChoiceSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>LineLength</Name>
				<Text>Longueur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>1000.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "line"</Visible>
			</Parameter>

			<Parameter>
				<Name>RectLength</Name>
				<Text>Longueur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>1000.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>RectWidth</Name>
				<Text>Largeur</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>500.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>CircleRadius</Name>
				<Text>Rayon</Text>
				<FontFaceCode>4</FontFaceCode>
				<Value>1000.0</Value>
				<ValueType>Length</ValueType>
				<Visible>ChoiceRadioGroup == "circle"</Visible>
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
        </Parameter>

    </Page>

</Element>
