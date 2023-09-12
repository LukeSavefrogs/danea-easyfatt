from xml.sax.saxutils import escape
from pathlib import Path
import re
import sys
import unittest

import veryeasyfatt.app.process_csv as csv

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from tests.utils.decorators import with_temporary_file


class XMLDocumentTestCase(unittest.TestCase):
    _executable_name = Path("./src/veryeasyfatt/bootstrap.py").resolve()

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content="""
        <?xml version="1.0" encoding="UTF-8"?>
        <!-- File in formato Easyfatt-XML creato con Danea Easyfatt - www.danea.it/software/easyfatt -->
        <!-- Per importare o creare un file in formato Easyfatt-Xml, consultare la documentazione tecnica: www.danea.it/software/easyfatt/xml -->
        <EasyfattDocuments AppVersion="2" Creator="Danea Easyfatt Enterprise  2023.54b" CreatorUrl="http://www.danea.it/software/easyfatt" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://www.danea.it/public/easyfatt-xml.xsd">
        <Company>
            <Name>ACME Inc.</Name>
            <Address>Via Anagnina, 0</Address>
            <Postcode>00173</Postcode>
            <City>Roma</City>
            <Province>RM</Province>
            <Country>Italia</Country>
            <FiscalCode>00000000000</FiscalCode>
            <VatCode>00000000000</VatCode>
            <Tel>0000000000</Tel>
            <Email>acme@acme.com</Email>
            <HomePage>https://example.com/</HomePage>
        </Company>
        <Documents>
            <Document>
                <CustomerCode>99999</CustomerCode>
                <CustomerWebLogin></CustomerWebLogin>
                <CustomerName>&quot;&amp;&apos;&gt;&lt;&quot;</CustomerName>
                <CustomerAddress>VIA TUSCOLANA, 0</CustomerAddress>
                <CustomerPostcode>00182</CustomerPostcode>
                <CustomerCity>ROMA</CustomerCity>
                <CustomerProvince>RM</CustomerProvince>
                <CustomerCountry>Italia</CustomerCountry>
                <CustomerFiscalCode>PDFDNR38H51B374Q</CustomerFiscalCode>
                <CustomerReference>TEST</CustomerReference>
                <CustomerCellPhone>0123456789</CustomerCellPhone>
                <CustomerEmail>test@gmail.com</CustomerEmail>
                <DeliveryName>TEST's temporary address</DeliveryName>
                <DeliveryAddress>VIA TUSCOLANA, 1000</DeliveryAddress>
                <DeliveryPostcode>00174</DeliveryPostcode>
                <DeliveryCity>ROMA</DeliveryCity>
                <DeliveryProvince>RM</DeliveryProvince>
                <DeliveryCountry>Italia</DeliveryCountry>
                <DocumentType>C</DocumentType>
                <Date>2023-01-30</Date>
                <Number>725</Number>
                <Numbering></Numbering>
                <CostDescription></CostDescription>
                <CostVatCode></CostVatCode>
                <CostAmount></CostAmount>
                <ContribDescription></ContribDescription>
                <ContribPerc></ContribPerc>
                <ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
                <ContribAmount></ContribAmount>
                <ContribVatCode></ContribVatCode>
                <TotalWithoutTax>92.21</TotalWithoutTax>
                <VatAmount>20.29</VatAmount>
                <WithholdingTaxAmount>0</WithholdingTaxAmount>
                <WithholdingTaxAmountB>0</WithholdingTaxAmountB>
                <WithholdingTaxNameB></WithholdingTaxNameB>
                <Total>112.5</Total>
                <PriceList>Dom. OFFERTA</PriceList>
                <PricesIncludeVat>true</PricesIncludeVat>
                <TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
                <WithholdingTaxPerc>0</WithholdingTaxPerc>
                <WithholdingTaxPerc2>0</WithholdingTaxPerc2>
                <PaymentName></PaymentName>
                <PaymentBank></PaymentBank>
                <PaymentAdvanceAmount></PaymentAdvanceAmount>
                <Carrier></Carrier>
                <TransportReason></TransportReason>
                <GoodsAppearance></GoodsAppearance>
                <NumOfPieces></NumOfPieces>
                <TransportDateTime></TransportDateTime>
                <ShipmentTerms></ShipmentTerms>
                <TransportedWeight></TransportedWeight>
                <TrackingNumber></TrackingNumber>
                <InternalComment></InternalComment>
                <CustomField1>7:00&gt;&gt;18:00</CustomField1>
                <CustomField2></CustomField2>
                <CustomField3></CustomField3>
                <CustomField4></CustomField4>
                <FootNotes></FootNotes>
                <ExpectedConclusionDate></ExpectedConclusionDate>
                <SalesAgent></SalesAgent>
                <Rows>
                    <Row>
                        <Code>000029</Code>
                        <Description>ACQUA EGERIA LT.1,5X6 PET EFFERVESCENTE NATURALE PLASTICA</Description>
                        <Qty>30</Qty>
                        <Um>CF</Um>
                        <Price>3.75</Price>
                        <Discounts></Discounts>
                        <VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
                        <Total>112.5</Total>
                        <Stock>true</Stock>
                        <Notes></Notes>
                    </Row>
                </Rows>
            </Document>
            <Document>
                <CustomerCode>99999</CustomerCode>
                <CustomerWebLogin></CustomerWebLogin>
                <CustomerName>Second document</CustomerName>
                <CustomerAddress>VIA TUSCOLANA, 0</CustomerAddress>
                <CustomerPostcode>00182</CustomerPostcode>
                <CustomerCity>ROMA</CustomerCity>
                <CustomerProvince>RM</CustomerProvince>
                <CustomerCountry>Italia</CustomerCountry>
                <CustomerFiscalCode>PDFDNR38H51B374Q</CustomerFiscalCode>
                <CustomerReference>TEST</CustomerReference>
                <CustomerCellPhone>0123456789</CustomerCellPhone>
                <CustomerEmail>test@gmail.com</CustomerEmail>
                <DeliveryName>TEST's temporary address</DeliveryName>
                <DeliveryAddress>VIA TUSCOLANA, 1000</DeliveryAddress>
                <DeliveryPostcode>00174</DeliveryPostcode>
                <DeliveryCity>ROMA</DeliveryCity>
                <DeliveryProvince>RM</DeliveryProvince>
                <DeliveryCountry>Italia</DeliveryCountry>
                <DocumentType>C</DocumentType>
                <Date>2023-01-30</Date>
                <Number>725</Number>
                <Numbering></Numbering>
                <CostDescription></CostDescription>
                <CostVatCode></CostVatCode>
                <CostAmount></CostAmount>
                <ContribDescription></ContribDescription>
                <ContribPerc></ContribPerc>
                <ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
                <ContribAmount></ContribAmount>
                <ContribVatCode></ContribVatCode>
                <TotalWithoutTax>92.21</TotalWithoutTax>
                <VatAmount>20.29</VatAmount>
                <WithholdingTaxAmount>0</WithholdingTaxAmount>
                <WithholdingTaxAmountB>0</WithholdingTaxAmountB>
                <WithholdingTaxNameB></WithholdingTaxNameB>
                <Total>112.5</Total>
                <PriceList>Dom. OFFERTA</PriceList>
                <PricesIncludeVat>true</PricesIncludeVat>
                <TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
                <WithholdingTaxPerc>0</WithholdingTaxPerc>
                <WithholdingTaxPerc2>0</WithholdingTaxPerc2>
                <PaymentName></PaymentName>
                <PaymentBank></PaymentBank>
                <PaymentAdvanceAmount></PaymentAdvanceAmount>
                <Carrier></Carrier>
                <TransportReason></TransportReason>
                <GoodsAppearance></GoodsAppearance>
                <NumOfPieces></NumOfPieces>
                <TransportDateTime></TransportDateTime>
                <ShipmentTerms></ShipmentTerms>
                <TransportedWeight></TransportedWeight>
                <TrackingNumber></TrackingNumber>
                <InternalComment></InternalComment>
                <CustomField1>7:00&gt;&gt;18:00</CustomField1>
                <CustomField2></CustomField2>
                <CustomField3></CustomField3>
                <CustomField4></CustomField4>
                <FootNotes></FootNotes>
                <ExpectedConclusionDate></ExpectedConclusionDate>
                <SalesAgent></SalesAgent>
                <Rows>
                    <Row>
                    <Code>000029</Code>
                    <Description>ACQUA EGERIA LT.1,5X6 PET EFFERVESCENTE NATURALE PLASTICA</Description>
                    <Qty>30</Qty>
                    <Um>CF</Um>
                    <Price>3.75</Price>
                    <Discounts></Discounts>
                    <VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
                    <Total>112.5</Total>
                    <Stock>true</Stock>
                    <Notes></Notes>
                    </Row>
                </Rows>
            </Document>
        </Documents>
        </EasyfattDocuments>
    """,
    )
    def test_special_characters(self, xml_document: Path):
        xml_text = xml_document.read_text(encoding='utf8').strip()
        csv_content = csv.genera_csv(xml_text)

        self.assertEqual(
            csv_content,
            [
                '@"&\'><" 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)07:00>>16:00^0^',
                "@Second document 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)07:00>>16:00^0^",
            ],
        )

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content="""
        <?xml version="1.0" encoding="UTF-8"?>
        <!-- File in formato Easyfatt-XML creato con Danea Easyfatt - www.danea.it/software/easyfatt -->
        <!-- Per importare o creare un file in formato Easyfatt-Xml, consultare la documentazione tecnica: www.danea.it/software/easyfatt/xml -->
        <EasyfattDocuments AppVersion="2" Creator="Danea Easyfatt Enterprise  2023.54b" CreatorUrl="http://www.danea.it/software/easyfatt" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://www.danea.it/public/easyfatt-xml.xsd">
        <Company>
            <Name>ACME Inc.</Name>
            <Address>Via Anagnina, 0</Address>
            <Postcode>00173</Postcode>
            <City>Roma</City>
            <Province>RM</Province>
            <Country>Italia</Country>
            <FiscalCode>00000000000</FiscalCode>
            <VatCode>00000000000</VatCode>
            <Tel>0000000000</Tel>
            <Email>acme@acme.com</Email>
            <HomePage>https://example.com/</HomePage>
        </Company>
        <Documents>
            <Document>
                <CustomerCode>99999</CustomerCode>
                <CustomerWebLogin></CustomerWebLogin>
                <CustomerName>Mario Rossi</CustomerName>
                <CustomerAddress>VIA TUSCOLANA, 0</CustomerAddress>
                <CustomerPostcode>00182</CustomerPostcode>
                <CustomerCity>ROMA</CustomerCity>
                <CustomerProvince>RM</CustomerProvince>
                <CustomerCountry>Italia</CustomerCountry>
                <CustomerFiscalCode>PDFDNR38H51B374Q</CustomerFiscalCode>
                <CustomerReference>TEST</CustomerReference>
                <CustomerCellPhone>0123456789</CustomerCellPhone>
                <CustomerEmail>test@gmail.com</CustomerEmail>
                <DeliveryName>Mario Rossi's temporary address</DeliveryName>
                <DeliveryAddress>VIA TUSCOLANA, 1000</DeliveryAddress>
                <DeliveryPostcode>00174</DeliveryPostcode>
                <DeliveryCity>ROMA</DeliveryCity>
                <DeliveryProvince>RM</DeliveryProvince>
                <DeliveryCountry>Italia</DeliveryCountry>
                <DocumentType>C</DocumentType>
                <Date>2023-01-30</Date>
                <Number>725</Number>
                <Numbering></Numbering>
                <CostDescription></CostDescription>
                <CostVatCode></CostVatCode>
                <CostAmount></CostAmount>
                <ContribDescription></ContribDescription>
                <ContribPerc></ContribPerc>
                <ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
                <ContribAmount></ContribAmount>
                <ContribVatCode></ContribVatCode>
                <TotalWithoutTax>92.21</TotalWithoutTax>
                <VatAmount>20.29</VatAmount>
                <WithholdingTaxAmount>0</WithholdingTaxAmount>
                <WithholdingTaxAmountB>0</WithholdingTaxAmountB>
                <WithholdingTaxNameB></WithholdingTaxNameB>
                <Total>112.5</Total>
                <PriceList>Dom. OFFERTA</PriceList>
                <PricesIncludeVat>true</PricesIncludeVat>
                <TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
                <WithholdingTaxPerc>0</WithholdingTaxPerc>
                <WithholdingTaxPerc2>0</WithholdingTaxPerc2>
                <PaymentName></PaymentName>
                <PaymentBank></PaymentBank>
                <PaymentAdvanceAmount></PaymentAdvanceAmount>
                <Carrier></Carrier>
                <TransportReason></TransportReason>
                <GoodsAppearance></GoodsAppearance>
                <NumOfPieces></NumOfPieces>
                <TransportDateTime></TransportDateTime>
                <ShipmentTerms></ShipmentTerms>
                <TransportedWeight></TransportedWeight>
                <TrackingNumber></TrackingNumber>
                <InternalComment></InternalComment>
                <CustomField1>7:00&gt;&gt;18:00</CustomField1>
                <CustomField2></CustomField2>
                <CustomField3></CustomField3>
                <CustomField4></CustomField4>
                <FootNotes></FootNotes>
                <ExpectedConclusionDate></ExpectedConclusionDate>
                <SalesAgent></SalesAgent>
                <Rows>
                    <Row>
                        <Code>000029</Code>
                        <Description>ACQUA EGERIA LT.1,5X6 PET EFFERVESCENTE NATURALE PLASTICA</Description>
                        <Qty>30</Qty>
                        <Um>CF</Um>
                        <Price>3.75</Price>
                        <Discounts></Discounts>
                        <VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
                        <Total>112.5</Total>
                        <Stock>true</Stock>
                        <Notes></Notes>
                    </Row>
                </Rows>
            </Document>
        </Documents>
        </EasyfattDocuments>
    """,
    )
    def test_single_document(self, xml_document: Path):
        """Test that the CSV is generated correctly when there is only one document in the XML file.

        See [#89](https://github.com/LukeSavefrogs/danea-easyfatt/issues/89).
        """
        xml_text = xml_document.read_text(encoding='utf8').strip()
        csv_content = csv.genera_csv(xml_text)

        self.assertEqual(
            csv_content,
            [
                "@Mario Rossi 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)07:00>>16:00^0^",
            ],
        )

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content="""
        <?xml version="1.0" encoding="UTF-8"?>
        <!-- File in formato Easyfatt-XML creato con Danea Easyfatt - www.danea.it/software/easyfatt -->
        <!-- Per importare o creare un file in formato Easyfatt-Xml, consultare la documentazione tecnica: www.danea.it/software/easyfatt/xml -->
        <EasyfattDocuments AppVersion="2" Creator="Danea Easyfatt Enterprise  2023.54b" CreatorUrl="http://www.danea.it/software/easyfatt" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://www.danea.it/public/easyfatt-xml.xsd">
        <Company>
            <Name>ACME Inc.</Name>
            <Address>Via Anagnina, 0</Address>
            <Postcode>00173</Postcode>
            <City>Roma</City>
            <Province>RM</Province>
            <Country>Italia</Country>
            <FiscalCode>00000000000</FiscalCode>
            <VatCode>00000000000</VatCode>
            <Tel>0000000000</Tel>
            <Email>acme@acme.com</Email>
            <HomePage>https://example.com/</HomePage>
        </Company>
        <Documents>
            <Document>
                <CustomerCode>99999</CustomerCode>
                <CustomerWebLogin></CustomerWebLogin>
                <CustomerName>Mario Rossi</CustomerName>
                <CustomerAddress>VIA TUSCOLANA, 0</CustomerAddress>
                <CustomerPostcode>00182</CustomerPostcode>
                <CustomerCity>ROMA</CustomerCity>
                <CustomerProvince>RM</CustomerProvince>
                <CustomerCountry>Italia</CustomerCountry>
                <CustomerFiscalCode>PDFDNR38H51B374Q</CustomerFiscalCode>
                <CustomerReference>TEST</CustomerReference>
                <CustomerCellPhone>0123456789</CustomerCellPhone>
                <CustomerEmail>test@gmail.com</CustomerEmail>
                <DeliveryName>Mario Rossi's temporary address</DeliveryName>
                <DeliveryAddress>VIA TUSCOLANA, 1000</DeliveryAddress>
                <DeliveryPostcode>00174</DeliveryPostcode>
                <DeliveryCity>ROMA</DeliveryCity>
                <DeliveryProvince>RM</DeliveryProvince>
                <DeliveryCountry>Italia</DeliveryCountry>
                <DocumentType>C</DocumentType>
                <Date>2023-01-30</Date>
                <Number>725</Number>
                <Numbering></Numbering>
                <CostDescription></CostDescription>
                <CostVatCode></CostVatCode>
                <CostAmount></CostAmount>
                <ContribDescription></ContribDescription>
                <ContribPerc></ContribPerc>
                <ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
                <ContribAmount></ContribAmount>
                <ContribVatCode></ContribVatCode>
                <TotalWithoutTax>92.21</TotalWithoutTax>
                <VatAmount>20.29</VatAmount>
                <WithholdingTaxAmount>0</WithholdingTaxAmount>
                <WithholdingTaxAmountB>0</WithholdingTaxAmountB>
                <WithholdingTaxNameB></WithholdingTaxNameB>
                <Total>112.5</Total>
                <PriceList>Dom. OFFERTA</PriceList>
                <PricesIncludeVat>true</PricesIncludeVat>
                <TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
                <WithholdingTaxPerc>0</WithholdingTaxPerc>
                <WithholdingTaxPerc2>0</WithholdingTaxPerc2>
                <PaymentName></PaymentName>
                <PaymentBank></PaymentBank>
                <PaymentAdvanceAmount></PaymentAdvanceAmount>
                <Carrier></Carrier>
                <TransportReason></TransportReason>
                <GoodsAppearance></GoodsAppearance>
                <NumOfPieces></NumOfPieces>
                <TransportDateTime></TransportDateTime>
                <ShipmentTerms></ShipmentTerms>
                <TransportedWeight>1234 Kg</TransportedWeight>
                <TrackingNumber></TrackingNumber>
                <InternalComment></InternalComment>
                <CustomField1>7:00&gt;&gt;18:00</CustomField1>
                <CustomField2></CustomField2>
                <CustomField3></CustomField3>
                <CustomField4></CustomField4>
                <FootNotes></FootNotes>
                <ExpectedConclusionDate></ExpectedConclusionDate>
                <SalesAgent></SalesAgent>
                <Rows>
                    <Row>
                        <Code>000029</Code>
                        <Description>ACQUA EGERIA LT.1,5X6 PET EFFERVESCENTE NATURALE PLASTICA</Description>
                        <Qty>30</Qty>
                        <Um>CF</Um>
                        <Price>3.75</Price>
                        <Discounts></Discounts>
                        <VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
                        <Total>112.5</Total>
                        <Stock>true</Stock>
                        <Notes></Notes>
                    </Row>
                </Rows>
            </Document>
        </Documents>
        </EasyfattDocuments>
    """,
    )
    def test_weight(self, xml_document: Path):
        """Test that the CSV is generated correctly when there is only one document in the XML file.

        See [#89](https://github.com/LukeSavefrogs/danea-easyfatt/issues/89).
        """
        xml_text = xml_document.read_text(encoding='utf8').strip()
        csv_content = csv.genera_csv(xml_text)

        self.assertEqual(
            csv_content,
            [
                "@Mario Rossi 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)07:00>>16:00^1234^",
            ],
        )

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content="""
        <?xml version="1.0" encoding="UTF-8"?>
        <!-- File in formato Easyfatt-XML creato con Danea Easyfatt - www.danea.it/software/easyfatt -->
        <!-- Per importare o creare un file in formato Easyfatt-Xml, consultare la documentazione tecnica: www.danea.it/software/easyfatt/xml -->
        <EasyfattDocuments AppVersion="2" Creator="Danea Easyfatt Enterprise  2023.54b" CreatorUrl="http://www.danea.it/software/easyfatt" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://www.danea.it/public/easyfatt-xml.xsd">
        <Company>
            <Name>ACME Inc.</Name>
            <Address>Via Anagnina, 0</Address>
            <Postcode>00173</Postcode>
            <City>Roma</City>
            <Province>RM</Province>
            <Country>Italia</Country>
            <FiscalCode>00000000000</FiscalCode>
            <VatCode>00000000000</VatCode>
            <Tel>0000000000</Tel>
            <Email>acme@acme.com</Email>
            <HomePage>https://example.com/</HomePage>
        </Company>
        <Documents>
            <Document>
                <CustomerCode>99999</CustomerCode>
                <CustomerWebLogin></CustomerWebLogin>
                <CustomerName>Mario Rossi</CustomerName>
                <CustomerAddress>VIA TUSCOLANA, 0</CustomerAddress>
                <CustomerPostcode>00182</CustomerPostcode>
                <CustomerCity>ROMA</CustomerCity>
                <CustomerProvince>RM</CustomerProvince>
                <CustomerCountry>Italia</CustomerCountry>
                <CustomerFiscalCode>PDFDNR38H51B374Q</CustomerFiscalCode>
                <CustomerReference>TEST</CustomerReference>
                <CustomerCellPhone>0123456789</CustomerCellPhone>
                <CustomerEmail>test@gmail.com</CustomerEmail>
                <DeliveryName>Mario Rossi's temporary address</DeliveryName>
                <DeliveryAddress>VIA TUSCOLANA, 1000</DeliveryAddress>
                <DeliveryPostcode>00174</DeliveryPostcode>
                <DeliveryCity>ROMA</DeliveryCity>
                <DeliveryProvince>RM</DeliveryProvince>
                <DeliveryCountry>Italia</DeliveryCountry>
                <DocumentType>C</DocumentType>
                <Date>2023-01-30</Date>
                <Number>725</Number>
                <Numbering></Numbering>
                <CostDescription></CostDescription>
                <CostVatCode></CostVatCode>
                <CostAmount></CostAmount>
                <ContribDescription></ContribDescription>
                <ContribPerc></ContribPerc>
                <ContribSubjectToWithholdingTax></ContribSubjectToWithholdingTax>
                <ContribAmount></ContribAmount>
                <ContribVatCode></ContribVatCode>
                <TotalWithoutTax>92.21</TotalWithoutTax>
                <VatAmount>20.29</VatAmount>
                <WithholdingTaxAmount>0</WithholdingTaxAmount>
                <WithholdingTaxAmountB>0</WithholdingTaxAmountB>
                <WithholdingTaxNameB></WithholdingTaxNameB>
                <Total>112.5</Total>
                <PriceList>Dom. OFFERTA</PriceList>
                <PricesIncludeVat>true</PricesIncludeVat>
                <TotalSubjectToWithholdingTax>0</TotalSubjectToWithholdingTax>
                <WithholdingTaxPerc>0</WithholdingTaxPerc>
                <WithholdingTaxPerc2>0</WithholdingTaxPerc2>
                <PaymentName></PaymentName>
                <PaymentBank></PaymentBank>
                <PaymentAdvanceAmount></PaymentAdvanceAmount>
                <Carrier></Carrier>
                <TransportReason></TransportReason>
                <GoodsAppearance></GoodsAppearance>
                <NumOfPieces></NumOfPieces>
                <TransportDateTime></TransportDateTime>
                <ShipmentTerms></ShipmentTerms>
                <TransportedWeight></TransportedWeight>
                <TrackingNumber></TrackingNumber>
                <InternalComment></InternalComment>
                <CustomField1></CustomField1>
                <CustomField2></CustomField2>
                <CustomField3></CustomField3>
                <CustomField4>9:00&gt;&gt;18:00</CustomField4>
                <FootNotes></FootNotes>
                <ExpectedConclusionDate></ExpectedConclusionDate>
                <SalesAgent></SalesAgent>
                <Rows>
                    <Row>
                        <Code>000029</Code>
                        <Description>ACQUA EGERIA LT.1,5X6 PET EFFERVESCENTE NATURALE PLASTICA</Description>
                        <Qty>30</Qty>
                        <Um>CF</Um>
                        <Price>3.75</Price>
                        <Discounts></Discounts>
                        <VatCode Perc="22" Class="Imponibile" Description="Imponibile 22%">22</VatCode>
                        <Total>112.5</Total>
                        <Stock>true</Stock>
                        <Notes></Notes>
                    </Row>
                </Rows>
            </Document>
        </Documents>
        </EasyfattDocuments>
    """,
    )
    def test_time_boundaries(self, xml_document: Path):
        """Test that the CSV is generated correctly when there is only one document in the XML file.

        See [#89](https://github.com/LukeSavefrogs/danea-easyfatt/issues/89).
        """
        base_xml_text = xml_document.read_text(encoding='utf8').strip()

        for boundary_format in [
            "09:00 >> 18:00",
            "09:00>>18:00",
            "09:00 >>18:00",
            "09:00 > 18:00",
            "09:00>18:00",
            "09:00 >18:00",
            "09:00 - 18:00",
            "09:00-18:00",
            "09:00 -18:00",
            "09:00 a 18:00",
        ]:
            xml_text = re.sub(
                r"(<CustomField4>).*?(</CustomField4>)",
                rf"\g<1>{boundary_format}\g<2>",
                base_xml_text,
            )
            csv_content = csv.genera_csv(xml_text)

            self.assertEqual(
                csv_content,
                [
                    "@Mario Rossi 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)09:00>>18:00^0^",
                ],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
