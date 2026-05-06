import unittest
from unittest.mock import patch

from veryeasyfatt.app.clienti import get_intervallo_spedizioni


class IntervalloSpedizioniTestCase(unittest.TestCase):
    @patch("veryeasyfatt.app.clienti.get_customers_data")
    def test_get_intervallo_spedizioni_with_extra_column_name(self, mock_customers):
        mock_customers.return_value = [
            {"Cod.": "00001", "Extra 1": "08-16"},
        ]

        result = get_intervallo_spedizioni("unused.xlsx", extra_field_id=1)

        self.assertEqual({"00001": "08:00>>16:00"}, result)

    @patch("veryeasyfatt.app.clienti.get_customers_data")
    def test_get_intervallo_spedizioni_with_libero_column_name(self, mock_customers):
        mock_customers.return_value = [
            {"Cod.": "00001", "Libero 1": "08-16"},
        ]

        result = get_intervallo_spedizioni("unused.xlsx", extra_field_id=1)

        self.assertEqual({"00001": "08:00>>16:00"}, result)

    @patch("veryeasyfatt.app.clienti.get_customers_data")
    def test_get_intervallo_spedizioni_raises_if_expected_column_is_missing(
        self, mock_customers
    ):
        mock_customers.return_value = [
            {"Cod.": "00001", "Campo Personalizzato 1": "08-16"},
        ]

        with self.assertRaisesRegex(
            KeyError, "Nessuna colonna trovata tra 'Extra 1' e 'Libero 1'"
        ):
            get_intervallo_spedizioni("unused.xlsx", extra_field_id=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
