import unittest

import veryeasyfatt.shared.formatter as simpleformatter

class FormatterCommandsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = simpleformatter.SimpleFormatter()
        return super().setUp()
    
    def test_lowercase(self):
        self.assertEqual(
            self.formatter.format('{var:s->lowercase}', var="HeLlO WOrLD!"),
            "hello world!"
        )

    def test_uppercase(self):
        self.assertEqual(
            self.formatter.format('{var:s->uppercase}', var="HeLlO WOrLD!"),
            "HELLO WORLD!"
        )
    
    def test_title(self):
        self.assertEqual(
            self.formatter.format('{var:s->title}', var="HeLlO WOrLD!"),
            "Hello World!"
        )
    
    def test_capitalize(self):
        self.assertEqual(
            self.formatter.format('{var:s->capitalize}', var="HeLlO WOrLD!"),
            "Hello world!"
        )
        
    def test_substring(self):
        self.assertEqual(
            self.formatter.format('{var:s->substring(-2)}', var="HeLlO WOrLD!"),
            "D!"
        )
        self.assertEqual(
            self.formatter.format('{var:s->substring(6, -1)}', var="HeLlO WOrLD!"),
            "WOrLD"
        )
        self.assertEqual(
            self.formatter.format('{var:s->substring(0, 100)}', var="HeLlO WOrLD!"),
            "HeLlO WOrLD!"
        )

    def test_replace(self):
        self.assertEqual(
            self.formatter.format('{var:s->replace(HeLlO, GooDByE)}', var="HeLlO WOrLD!"),
            "GooDByE WOrLD!",
            "Should be able to do a simple replace"
        )
        self.assertEqual(
            self.formatter.format('{var:s->replace(O, *)}', var="HeLlO WOrLD!"),
            "HeLl* W*rLD!",
            "Should be able to use special characters in replace command"
        )
        self.assertEqual(
            self.formatter.format('{var:s->replace("HeLlO ", " GooDByE mY beLovED ")}', var="HeLlO WOrLD!"),
            " GooDByE mY beLovED WOrLD!",
            "Should be able to use spaces in replace command (if quoted)"
        )
        self.assertEqual(
            self.formatter.format('{var:s->replace("\'WOrLD\'!", "my \'Friend\'!")}', var="HeLlO 'WOrLD'!"),
            "HeLlO my 'Friend'!",
            "Should be able to replace quotes too (if properly escaped)"
        )
    
    def test_legacy(self):
        """ Ensure that backward compatibility is maintained """
        self.assertEqual(
            self.formatter.format('{var:.5}', var="HeLlO WOrLD!"),
            "HeLlO",
        )
        self.assertEqual(
            self.formatter.format('{var:*>20}', var="HeLlO WOrLD!"),
            "********HeLlO WOrLD!",
        )
        self.assertEqual(
            self.formatter.format('{var!r}', var="HeLlO WOrLD!"),
            "'HeLlO WOrLD!'",
        )
        self.assertEqual(
            self.formatter.format('{var!s}', var="HeLlO WOrLD!"),
            "HeLlO WOrLD!",
        )
        self.assertEqual(
            self.formatter.format('{var!a}', var="HeLlO WOrLD!"),
            "'HeLlO WOrLD!'",
        )