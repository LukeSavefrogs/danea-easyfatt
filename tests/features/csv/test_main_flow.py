"""Integration tests for the main CSV generation flow.

Tests cover:
- The entire CSV creation flow (XML → CSV file)
- Clipboard copy when the user confirms (answers 'Y')
- No clipboard copy when the user declines (answers 'N')
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Hack needed to include scripts from the `scripts` directory (under root)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

# Mock the private `easyfatt_db_connector` package (unavailable in test environments)
# before importing any veryeasyfatt module that transitively depends on it.
_mock_edb = MagicMock()
sys.modules.setdefault("easyfatt_db_connector", _mock_edb)
sys.modules.setdefault("easyfatt_db_connector.xml", _mock_edb.xml)
sys.modules.setdefault("easyfatt_db_connector.xml.document", _mock_edb.xml.document)

# Mock Windows-only modules unavailable on Linux/macOS test environments.
sys.modules.setdefault("winreg", MagicMock())

from tests.utils.decorators import with_temporary_file
from veryeasyfatt.app.constants import ApplicationGoals
from veryeasyfatt.app.main import main

_SAMPLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!-- File in formato Easyfatt-XML creato con Danea Easyfatt - www.danea.it/software/easyfatt -->
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
        <DeliveryName>Mario Rossi temporary address</DeliveryName>
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
"""

_EXPECTED_CSV_LINE = "@Mario Rossi 99999@VIA TUSCOLANA, 1000 00174 ROMA(20)07:00>>16:00^0^"
# Note: the default_interval "07:00-16:00" is normalised to "07:00>>16:00" by
# routexl_time_boundaries() (hyphens and other separators are all converted to ">>")


def _make_mock_settings(input_xml_path: Path, output_csv_path: Path) -> MagicMock:
    """Create a mock settings object with the required attributes for testing."""
    mock = MagicMock()
    mock.files.input.easyfatt = input_xml_path
    mock.files.input.addition = None
    mock.files.output.csv = output_csv_path
    mock.easyfatt.customers.export_filename = []
    mock.options.output.csv_template = (
        "@{CustomerName} {CustomerCode}@{eval_IndirizzoSpedizione} {eval_CAPSpedizione} "
        "{eval_CittaSpedizione}(20){eval_intervalloSpedizione}^{eval_pesoSpedizione}^"
    )
    mock.features.shipping.default_interval = "07:00-16:00"
    return mock


class CSVFlowTestCase(unittest.TestCase):
    """Integration tests for the main CSV generation flow."""

    def setUp(self):
        """Create a temporary output CSV file path before each test."""
        fd, temp_file = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        self._output_csv = Path(temp_file)

    def tearDown(self):
        """Remove the temporary output CSV file after each test."""
        self._output_csv.unlink(missing_ok=True)

    def _run_main_with_mocks(
        self,
        input_xml_path: Path,
        confirm_clipboard: bool,
        confirm_open_file: bool,
    ):
        """Run main() in CSV generator mode with mocked I/O and settings.

        Args:
            input_xml_path: Path to the temporary input XML file.
            confirm_clipboard: Simulated user answer to the clipboard prompt.
            confirm_open_file: Simulated user answer to the open-file prompt.

        Returns:
            Tuple of (return_value, mock_pyperclip_copy).
        """
        mock_settings = _make_mock_settings(input_xml_path, self._output_csv)

        with (
            patch("veryeasyfatt.app.main.settings", mock_settings),
            patch("veryeasyfatt.app.process_csv.settings", mock_settings),
            patch(
                "veryeasyfatt.app.main.Confirm.ask",
                side_effect=[confirm_clipboard, confirm_open_file],
            ),
            patch("veryeasyfatt.app.main.pyperclip.copy") as mock_copy,
            patch("os.startfile", create=True),
        ):
            result = main(goal=ApplicationGoals.CSV_GENERATOR.value)

        return result, mock_copy

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content=_SAMPLE_XML,
    )
    def test_csv_flow_creates_output_file(self, xml_document: Path):
        """Test that the entire CSV flow produces a correctly formatted output file."""
        result, _ = self._run_main_with_mocks(
            input_xml_path=xml_document,
            confirm_clipboard=False,
            confirm_open_file=False,
        )

        self.assertTrue(result)
        self.assertTrue(self._output_csv.exists())
        self.assertEqual(self._output_csv.read_text(), _EXPECTED_CSV_LINE)

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content=_SAMPLE_XML,
    )
    def test_csv_flow_copies_to_clipboard_when_confirmed(self, xml_document: Path):
        """Test that answering Y to the clipboard prompt copies the CSV content."""
        result, mock_copy = self._run_main_with_mocks(
            input_xml_path=xml_document,
            confirm_clipboard=True,
            confirm_open_file=False,
        )

        self.assertTrue(result)
        mock_copy.assert_called_once_with(_EXPECTED_CSV_LINE)

    @with_temporary_file(
        file_prefix="Documenti-",
        file_suffix=".DefXml",
        content=_SAMPLE_XML,
    )
    def test_csv_flow_no_clipboard_when_declined(self, xml_document: Path):
        """Test that answering N to the clipboard prompt does NOT copy anything."""
        result, mock_copy = self._run_main_with_mocks(
            input_xml_path=xml_document,
            confirm_clipboard=False,
            confirm_open_file=False,
        )

        self.assertTrue(result)
        mock_copy.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
