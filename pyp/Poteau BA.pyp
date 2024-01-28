<?xml version="1.0" encoding="utf-8"?>

<Element>

    <Script>
        <Name>APIHub\reinf_concr_column.py</Name>
        <Title>Poteau Béton Armé - API2GETHER</Title>
        <Version>1.0</Version>
    </Script>

	<Constants>

        <Constant>
            <Name>CALC_LONG_REBAR_DIAM</Name>
            <Value>1000</Value>
            <ValueType>Integer</ValueType>
        </Constant>

    </Constants>

    <Page>

        <Name>Page1</Name>
        <Text>Données globales</Text>
        <TextId>e_GLOBAL_DATA</TextId>

		<Parameter>
            <Name>APILinkRow</Name>
            <Text>🌐</Text>
            <ValueType>Row</ValueType>

			<Parameter>
				<Name>APILink</Name>
				<Text>API2GETHER</Text>
				<EventId>9999</EventId>
				<ValueType>Button</ValueType>
				<Value>https://api2gether.com/</Value>
			</Parameter>

		</Parameter>

		<Parameter>
			<Name>WebLinkSeparator</Name>
			<ValueType>Separator</ValueType>
		</Parameter>

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
            <Text>Type de béton</Text>
			<TextId>e_CONCRETE_GRADE</TextId>
            <Value>-1</Value>
            <ValueType>ReinfConcreteGrade</ValueType>
        </Parameter>

        <Parameter>
            <Name>GeometryExpander</Name>
            <Text>Géométrie</Text>
			<TextId>e_GEOMETRY</TextId>
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
				<Name>ColumnRectangularPicture</Name>
				<Value>images\GeometryColumnRectangular.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ColumnCircularPicture</Name>
				<Value>images\GeometryColumnCircular.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
				<Visible>ChoiceRadioGroup == "circle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ColumnThickRow</Name>
				<Text>Epaisseur</Text>
				<TextId>e_THICKNESS</TextId>
				<ValueType>Row</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>

				<Parameter>
					<Name>ColumnThick</Name>
					<Text></Text>
					<Value>300.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>150</MinValue>
					<MaxValue>1000</MaxValue>
				</Parameter>

				<Parameter>
					<Name>Param01</Name>
					<Value>images\Param01.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ColumnLengthRow</Name>
				<Text>Longueur</Text>
				<TextId>e_LENGTH</TextId>
				<ValueType>Row</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>

				<Parameter>
					<Name>ColumnLength</Name>
					<Text> </Text>
					<Value>300.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>150</MinValue>
					<MaxValue>1000</MaxValue>
				</Parameter>

				<Parameter>
					<Name>Param02</Name>
					<Value>images\Param02.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ColumnRadiusRow</Name>
				<Text>Rayon</Text>
				<TextId>e_RADIUS</TextId>
				<ValueType>Row</ValueType>
				<Visible>ChoiceRadioGroup == "circle"</Visible>

				<Parameter>
					<Name>ColumnRadius</Name>
					<Text></Text>
					<Value>150.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>100</MinValue>
					<MaxValue>500</MaxValue>
				</Parameter>

				<Parameter>
					<Name>Param03</Name>
					<Value>images\Param03.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ColumnHeightRow</Name>
				<Text>Hauteur</Text>
				<TextId>e_HEIGHT</TextId>
				<ValueType>Row</ValueType>

				<Parameter>
					<Name>ColumnHeight</Name>
					<Text></Text>
					<Value>-1</Value>
					<ValueType>Length</ValueType>
					<Constraint>PlaneReferences</Constraint>
				</Parameter>

				<Parameter>
					<Name>Param04</Name>
					<Value>images\Param04.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>PlaneReferences</Name>
				<Text> </Text>
				<Value></Value>
				<ValueType>PlaneReferences</ValueType>
				<ValueDialog>PlaneReferences</ValueDialog>
				<Constraint>ColumnHeight</Constraint>
			</Parameter>

			<Parameter>
				<Name>GeometrySeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>SlabHeightRow</Name>
				<Text>Epaisseur dalle / poutre</Text>
				<ValueType>Row</ValueType>

				<Parameter>
					<Name>SlabHeight</Name>
					<Text></Text>
					<Value>200</Value>
					<ValueType>Length</ValueType>
				</Parameter>

				<Parameter>
					<Name>Param05</Name>
					<Value>images\Param05.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>GeometrySeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>NextColumnCheckBox</Name>
				<Text>Poteau supérieur ?</Text>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>TakeColumnDim</Name>
				<Text>Reprendre les dimensions ?</Text>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
				<Visible>NextColumnCheckBox == True</Visible>
			</Parameter>

			<Parameter>
				<Name>NextColumnThickRow</Name>
				<Text>Epaisseur</Text>
				<TextId>e_THICKNESS</TextId>
				<ValueType>Row</ValueType>
				<Visible>NextColumnCheckBox == True and ChoiceRadioGroup == "rectangle"</Visible>

				<Parameter>
					<Name>NextColumnThick</Name>
					<Text></Text>
					<Value>300.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>150</MinValue>
					<MaxValue>1000</MaxValue>
					<Enable>TakeColumnDim == False</Enable>
				</Parameter>

				<Parameter>
					<Name>Param01Bis</Name>
					<Value>images\Param01Bis.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>NextColumnLengthRow</Name>
				<Text>Longueur</Text>
				<TextId>e_LENGTH</TextId>
				<ValueType>Row</ValueType>
				<Visible>NextColumnCheckBox == True and ChoiceRadioGroup == "rectangle"</Visible>

				<Parameter>
					<Name>NextColumnLength</Name>
					<Text> </Text>
					<Value>300.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>150</MinValue>
					<MaxValue>1000</MaxValue>
					<Enable>TakeColumnDim == False</Enable>
				</Parameter>

				<Parameter>
					<Name>Param02Bis</Name>
					<Value>images\Param02Bis.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>NextColumnRadiusRow</Name>
				<Text>Rayon</Text>
				<TextId>e_RADIUS</TextId>
				<ValueType>Row</ValueType>
				<Visible>NextColumnCheckBox == True and ChoiceRadioGroup == "circle"</Visible>

				<Parameter>
					<Name>NextColumnRadius</Name>
					<Text></Text>
					<Value>150.0</Value>
					<ValueType>Length</ValueType>
					<MinValue>100</MinValue>
					<MaxValue>500</MaxValue>
					<Enable>TakeColumnDim == False</Enable>
				</Parameter>

				<Parameter>
					<Name>Param03Bis</Name>
					<Value>images\Param03Bis.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
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
			<TextId>e_FORMAT</TextId>
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
				<TextId>e_HEIGHT</TextId>
				<Value>2.5</Value>
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

	<Page>

		<Name>Page3</Name>
		<Text>Armature</Text>
		<TextId>e_REINFORCEMENT</TextId>

		<Parameter>
            <Name>ShowReinfCheckBox</Name>
            <Text>Afficher les armatures</Text>
            <Value>False</Value>
            <ValueType>CheckBox</ValueType>
        </Parameter>

		<Parameter>
            <Name>RebarOptionsExpander</Name>
            <Text>Options</Text>
            <ValueType>Expander</ValueType>
			<Visible>ShowReinfCheckBox == True</Visible>

			<Parameter>
				<Name>ReinfConcreteCover</Name>
				<Text>Enrobage</Text>
				<TextId>e_CONCRETE_COVER</TextId>
				<Value>30</Value>
				<ValueType>ReinfConcreteCover</ValueType>
			</Parameter>
		</Parameter>

		<Parameter>
            <Name>MainRebarExpander</Name>
            <Text>Barres longitudinales</Text>
			<TextId>e_LONGITUDINAL_BARS</TextId>
            <ValueType>Expander</ValueType>
			<Visible>ShowReinfCheckBox == True</Visible>

			<Parameter>
				<Name>CalculatorRow</Name>
				<Text>Calcul du Diamètre</Text>
				<ValueType>Row</ValueType>

				<Parameter>
					<Name>CalculatorButton</Name>
					<Text> </Text>
					<EventId>CALC_LONG_REBAR_DIAM</EventId>
					<Value>images\Calculator.png</Value>
					<ValueType>PictureButton</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
                <Name>AsRow01</Name>
                <Text> </Text>
                <ValueType>Row</ValueType>

                <Parameter>
                    <Name>AsMinText</Name>
                    <Text></Text>
                    <Value>As min</Value>
                    <ValueType>Text</ValueType>
                </Parameter>

				<Parameter>
                    <Name>EmptyText</Name>
                    <Text></Text>
                    <Value></Value>
                    <ValueType>Text</ValueType>
                </Parameter>

                <Parameter>
                    <Name>AsMaxText</Name>
                    <Text></Text>
                    <Value>As max</Value>
                    <ValueType>Text</ValueType>
                </Parameter>
            </Parameter>

			<Parameter>
                <Name>AsRow02</Name>
                <Text>As (cm²)</Text>
                <ValueType>Row</ValueType>

				<Parameter>
					<Name>AsMinDouble</Name>
					<Text></Text>
					<Value>0.0</Value>
					<ValueType>Double</ValueType>
					<Enable>False</Enable>
				</Parameter>

				<Parameter>
					<Name>AsRealDouble</Name>
					<Text></Text>
					<Value>0.0</Value>
					<ValueType>Double</ValueType>
					<Enable>False</Enable>
					<BackgroundColor>(255, 0, 0) if AsRealDouble &lt; AsMinDouble or AsRealDouble &gt; AsMaxDouble else (-1, -1, -1)</BackgroundColor>
				</Parameter>

				<Parameter>
					<Name>AsMaxDouble</Name>
					<Text></Text>
					<Value>0.0</Value>
					<ValueType>Double</ValueType>
					<Enable>False</Enable>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ReinfColumnRectangularPicture01</Name>
				<Value>images\ReinfColumnRectangular_01.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>FirstBarText</Name>
				<Text>Barres d'angle (A)</Text>
				<FontFaceCode>4</FontFaceCode>
				<ValueType>Text</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>FirstBarDiameter</Name>
				<Text>Diamètre</Text>
				<TextId>e_BAR_DIAMETER</TextId>
				<Value>12</Value>
				<ValueList>8|10|12|14|16|20</ValueList>
				<ValueType>IntegerComboBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>RebarSeparator</Name>
				<ValueType>Separator</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ScndBarText</Name>
				<Text>Barres latérales (B)</Text>
				<FontFaceCode>4</FontFaceCode>
				<ValueType>Text</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ScndBarAsFirstBar</Name>
				<Text>Diamètres identiques</Text>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>SecondBarDiameter</Name>
				<Text>Diamètre</Text>
				<TextId>e_BAR_DIAMETER</TextId>
				<Value>10</Value>
				<ValueList>8|10|12|14|16|20</ValueList>
				<ValueType>IntegerComboBox</ValueType>
				<Enable>ScndBarAsFirstBar == False</Enable>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>WarningRow</Name>
				<Text> </Text>
				<Value>1</Value>
				<ValueType>Row</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle" and FirstBarDiameter &lt; SecondBarDiameter and (ScndBarRectQttInLength &gt; 0 or ScndBarRectQttInThick &gt; 0)</Visible>

				<Parameter>
					<Name>WarningPicture01</Name>
					<Value>images\StatusInvalid.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>

				<Parameter>
					<Name>WarningBarDiameter</Name>
					<Text>dynamic</Text>
					<ValueTextDyn>
return f"barres latérales (Ø{SecondBarDiameter}) supérieures aux barres d'angle (Ø{FirstBarDiameter})"
					</ValueTextDyn>
					<FontStyle>1</FontStyle>
					<FontFaceCode>1</FontFaceCode>
					<ValueType>Text</ValueType>
				</Parameter>

				<Parameter>
					<Name>WarningPicture02</Name>
					<Value>images\StatusInvalid.png</Value>
					<ValueType>Picture</ValueType>
				</Parameter>
			</Parameter>

			<Parameter>
				<Name>ReinfColumnRectangularPicture02</Name>
				<Value>images\ReinfColumnRectangular_02.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ReinfColumnCircularPicture</Name>
				<Value>images\ReinfColumnCircular.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
				<Visible>ChoiceRadioGroup == "circle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ScndBarRectQttInLength</Name>
				<Text>n (l)</Text>
				<Value>0</Value>
				<ValueType>Integer</ValueType>
				<ValueSlider>True</ValueSlider>
				<MinValue>0</MinValue>
				<MaxValue>10</MaxValue>
				<IntervalValue>1</IntervalValue>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>ScndBarRectQttInThick</Name>
				<Text>n (t)</Text>
				<Value>0</Value>
				<ValueType>Integer</ValueType>
				<ValueSlider>True</ValueSlider>
				<MinValue>0</MinValue>
				<MaxValue>10</MaxValue>
				<IntervalValue>1</IntervalValue>
				<Visible>ChoiceRadioGroup == "rectangle"</Visible>
			</Parameter>

			<Parameter>
				<Name>RebarCircQtt</Name>
				<Text>n</Text>
				<Value>6</Value>
				<ValueType>Integer</ValueType>
				<ValueSlider>True</ValueSlider>
				<MinValue>0</MinValue>
				<MaxValue>10</MaxValue>
				<IntervalValue>1</IntervalValue>
				<Visible>ChoiceRadioGroup == "circle"</Visible>
			</Parameter>

		</Parameter>

		<Parameter>
            <Name>StirrupExpander</Name>
            <Text>Cadre</Text>
			<TextId>e_STIRRUPS</TextId>
            <ValueType>Expander</ValueType>
			<Visible>ShowReinfCheckBox == True</Visible>

			<Parameter>
				<Name>ReinfColumnHeightPicture</Name>
				<Value>images\ReinfColumnHeight.png</Value>
				<Orientation>Left</Orientation>
				<ValueType>Picture</ValueType>
			</Parameter>

			<Parameter>
				<Name>MainStirrup</Name>
				<Text>,Diamètre,Espacement</Text>
				<TextId>,e_BAR_DIAMETER,e_SPACING</TextId>
				<Value>images\ParamA.png|6|200</Value>
				<ValueList>,6|8|10,</ValueList>
				<MinValue>,6,100</MinValue>
				<MaxValue>,10,400</MaxValue>
				<ValueType>namedtuple(Picture,IntegerComboBox,Length)</ValueType>
				<NamedTuple>
					<TypeName>MainStirrup</TypeName>
					<FieldNames>Picture,Diameter,Length</FieldNames>
				</NamedTuple>
			</Parameter>

			<Parameter>
				<Name>StirrupSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>StirrupList</Name>
				<Text>,Espacement,Distance</Text>
				<TextId>,e_SPACING,e_DISTANCE</TextId>
				<Value>[images\ParamB.png|120|450;
						images\ParamC.png|120|450]
				</Value>
				<ValueType>namedtuple(Picture,Length,Length,Separator)</ValueType>
				<NamedTuple>
					<TypeName>Stirrup</TypeName>
					<FieldNames>Picture,Spacing,Length,Separator</FieldNames>
				</NamedTuple>
				<MinValue>,100,,</MinValue>
				<MaxValue>,360,,</MaxValue>
				<Enable>,,False</Enable>
			</Parameter>

		</Parameter>

		<Parameter>
            <Name>StarterBarExpander</Name>
            <Text>Attentes</Text>
            <ValueType>Expander</ValueType>
			<Visible>ShowReinfCheckBox == True and NextColumnCheckBox == True</Visible>

			<Parameter>
				<Name>StterBarQtt</Name>
				<Text>Quantité</Text>
				<Value>4</Value>
				<ValueType>Integer</ValueType>
				<ValueSlider>True</ValueSlider>
				<MinValue>4</MinValue>
				<MaxValue>20</MaxValue>
				<IntervalValue>1</IntervalValue>
			</Parameter>

			<Parameter>
				<Name>StarterBarDiameter</Name>
				<Text>Diamètre</Text>
				<TextId>e_BAR_DIAMETER</TextId>
				<Value>12</Value>
				<ValueList>8|10|12|14|16|20</ValueList>
				<ValueType>IntegerComboBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>StarterBarLength</Name>
				<Text>Longueur</Text>
				<TextId>e_LENGTH</TextId>
				<Value>1000</Value>
				<MinValue>100</MinValue>
				<MaxValue>2000</MaxValue>
				<ValueType>Length</ValueType>
			</Parameter>

		</Parameter>

	</Page>

	<Page>

		<Name>Page4</Name>
		<Text>Format</Text>

		<Parameter>
            <Name>ColumnFormatExpander</Name>
            <Text>Paramètres</Text>
        	<TextId>e_PROPERTIES</TextId>
            <ValueType>Expander</ValueType>

			<Parameter>
				<Name>2DText</Name>
				<Text>Représentation 2D</Text>
       	 		<TextId>e_FORMAT_2D</TextId>
				<FontStyle>1</FontStyle>
				<FontFaceCode>1</FontFaceCode>
				<ValueType>Text</ValueType>
			</Parameter>

			<Parameter>
				<Name>CommonProperties</Name>
				<Text></Text>
				<Value>CommonProperties(Layer(3803)),CommonProperties(Pen(3)),CommonProperties(Stroke(1)),CommonProperties(Color(1)),CommonProperties(PenByLayer(1)),CommonProperties(StrokeByLayer(1)),CommonProperties(ColorByLayer(1))</Value>
				<ValueType>CommonProperties</ValueType>
				<Visible>|CommonProperties.DrawOrder:False</Visible>
			</Parameter>

			<Parameter>
				<Name>FormatSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>HatchCheckBox</Name>
				<Text>Hachurage</Text>
        		<TextId>e_HATCH</TextId>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>HatchStyle</Name>
				<Text> </Text>
				<Value>-1</Value>
				<ValueType>Hatch</ValueType>
				<Visible>HatchCheckBox == True</Visible>
			</Parameter>

			<Parameter>
				<Name>FillCheckBox</Name>
				<Text>Surface de remplissage</Text>
        		<TextId>e_FILLING</TextId>
				<Value>False</Value>
				<ValueType>CheckBox</ValueType>
			</Parameter>

			<Parameter>
				<Name>FillColor</Name>
				<Text> </Text>
				<Value>-1</Value>
				<ValueType>Color</ValueType>
				<Visible>FillCheckBox == True</Visible>
			</Parameter>

			<Parameter>
				<Name>FormatSeparator</Name>
				<ValueType>Separator</ValueType>
			</Parameter>

			<Parameter>
				<Name>3DText</Name>
				<Text>Représentation 3D</Text>
				<TextId>e_FORMAT_3D</TextId>
				<FontStyle>1</FontStyle>
				<FontFaceCode>1</FontFaceCode>
				<ValueType>Text</ValueType>
			</Parameter>

			<Parameter>
				<Name>MaterialButton</Name>
				<Text>Surfaces</Text>
				<TextId>e_SURFACE</TextId>
				<Value>Materials\Concrete\Cast\Cast_Concrete005</Value>
				<ValueType>MaterialButton</ValueType>
				<DisableButtonIsShown>True</DisableButtonIsShown>
			</Parameter>
		</Parameter>

		<Parameter>
            <Name>ReinfFormatExpander</Name>
			<Text>Armature</Text>
			<TextId>e_REINFORCEMENT</TextId>
            <ValueType>Expander</ValueType>

			<Parameter>
				<Name>ReinfLayerProperties</Name>
				<Text>Layer</Text>
				<Value>3864</Value>
				<ValueType>Layer</ValueType>
			</Parameter>
		</Parameter>

	</Page>

</Element>
