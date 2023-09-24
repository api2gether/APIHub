<?xml version="1.0" encoding="utf-8"?>

<Element>

    <Script>
        <Name>APIHub\hello_world.py</Name>
        <Title>HelloWorld</Title>
        <Version>3.0</Version>
    </Script>

    <Page>

        <Name>Page1</Name>
        <Text>Général</Text>

        <Parameter>
            <Name>GeometryExpander</Name>
            <Text>Géométrie</Text>
            <ValueType>Expander</ValueType>

            <Parameter>
                <Name>LineLength</Name>
                <Text>Longueur</Text>
                <Value>1000.0</Value>
                <ValueType>Length</ValueType>
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
