### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for testdrive.uri"""

from unittest import TestCase

from testdrive.uri import UriBuilder


class TestUrn(TestCase):
    """Tests for testdrive.uri.UriBuilder building URN"""

    def test_urn_base_errors(self):
        """Test testdrive.uri.UriBuilder base URN errors"""
        with self.assertRaises(ValueError):
            UriBuilder("urn:path?query=not-allowed")
        with self.assertRaises(ValueError):
            UriBuilder("urn:path#fragment-not-allowed")
        with self.assertRaises(ValueError):
            UriBuilder("urn:path#")  # empty fragment not allowed

    def test_urn_path_rel(self):
        """Test testdrive.uri.UriBuilder builds URN from relative path"""
        base = "urn:abc:def"
        path = "foo/bar"
        qargs = {"v": 1}
        for b_suffix in ("", ":"):
            for p_suffix in ("", "/"):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    "urn:abc:def:foo:bar",
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    "urn:abc:def:foo:bar?v=1",
                )

    def test_urn_path_abs(self):
        """Test testdrive.uri.UriBuilder builds URN from absolute path"""
        base = "urn:ghi"
        path = "/quux/corge"
        qargs = {"v": 2}
        for b_suffix in ("", ":"):
            for p_suffix in ("", "/"):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    "urn:ghi:quux:corge",
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    "urn:ghi:quux:corge?v=2",
                )

    def test_urn_rebase_errors(self):
        """Test testdrive.uri.UriBuilder rebase URN errors"""
        base = "urn:jkl"
        path = "/wibble/wobble/"
        qargs = {"x": "y"}
        builder = UriBuilder(base, **qargs)
        urn = builder.build(path)
        other = "https://target/base/"
        self.assertEqual(
            builder.rebase(urn, other),
            "https://target/base/wibble/wobble/",
        )
        with self.assertRaises(ValueError):
            builder.rebase("https://xyz/wibble/wobble/", other)
        with self.assertRaises(ValueError):
            builder.rebase("urn:xyz:wibble:wobble", other)
        with self.assertRaises(ValueError):
            builder.rebase(urn + "#frag", other)
        with self.assertRaises(ValueError):
            builder.rebase(urn + "#", other)

    def test_urn_rebase(self):
        """Test testdrive.uri.UriBuilder rebases URN"""
        base1 = "urn:jkl"
        base2 = "URN:mno:pqr:"
        path = "/wibble/wobble/"
        qargs = {"x": "y"}
        builder = UriBuilder(base1, **qargs)
        urn = builder.build(path)
        self.assertEqual(
            urn,
            "urn:jkl:wibble:wobble?x=y",
        )
        self.assertEqual(
            builder.rebase(urn, base2),
            "urn:mno:pqr:wibble:wobble",
        )


class TestUrl(TestCase):
    """Tests for testdrive.uri.UriBuilder building URL"""

    def test_url_base_errors(self):
        """Test testdrive.uri.UriBuilder base URL errors"""
        with self.assertRaises(ValueError):
            UriBuilder("//authority/path/")  # missing scheme not allowed
        with self.assertRaises(ValueError):
            UriBuilder("scheme://authority/path?query=not-allowed")
        with self.assertRaises(ValueError):
            UriBuilder("scheme://authority/path#fragment-not-allowed")
        with self.assertRaises(ValueError):
            UriBuilder("scheme://authority/path#")  # empty fragment not allowed

    def test_url_path_rel(self):
        """Test testdrive.uri.UriBuilder builds URL from relative path"""
        base = "https://abc.org/def"
        path = "foo/bar"
        qargs = {"v": 3}
        for b_suffix in ("", "/"):
            for p_suffix in ("", "/"):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    "https://abc.org/def/foo/bar/",
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    "https://abc.org/def/foo/bar/?v=3",
                )

    def test_url_path_abs(self):
        """Test testdrive.uri.UriBuilder builds URL from absolute path"""
        base = "https://ghi.org"
        path = "/quux/corge"
        qargs = {"v": "thud"}
        for b_suffix in ("", "/"):
            for p_suffix in ("", "/"):
                self.assertEqual(
                    UriBuilder(base + b_suffix).build(path + p_suffix),
                    "https://ghi.org/quux/corge/",
                )
                self.assertEqual(
                    UriBuilder(base + b_suffix, **qargs).build(path + p_suffix),
                    "https://ghi.org/quux/corge/?v=thud",
                )

    def test_url_rebase_errors(self):
        """Test testdrive.uri.UriBuilder rebase URL errors"""
        base = "https://jkl.co.uk/mno/"
        path = "/wibble/wobble/"
        qargs = {"x": "Y"}
        builder = UriBuilder(base, **qargs)
        url = builder.build(path)
        other = "https://target/base/"
        self.assertEqual(
            builder.rebase(url, other),
            "https://target/base/wibble/wobble/",
        )
        with self.assertRaises(ValueError):
            builder.rebase("ftp://jkl.co.uk/mno/wibble/wobble/", other)
        with self.assertRaises(ValueError):
            builder.rebase("https://mno.co.uk/mno/wibble/wobble/", other)
        with self.assertRaises(ValueError):
            builder.rebase("https://jkl.co.uk/jkl/wibble/wobble/", other)
        with self.assertRaises(ValueError):
            builder.rebase(url + "#frag", other)
        with self.assertRaises(ValueError):
            builder.rebase(url + "#", other)

    def test_url_rebase(self):
        """Test testdrive.uri.UriBuilder rebases URL"""
        base1 = "https://jkl.com/"
        base2 = "ftp://mno.pqr/stu/"
        path = "/wibble/wobble/"
        qargs = {"X": "y"}
        builder = UriBuilder(base1, **qargs)
        url = builder.build(path)
        self.assertEqual(
            url,
            "https://jkl.com/wibble/wobble/?X=y",
        )
        self.assertEqual(
            builder.rebase(url, base2),
            "ftp://mno.pqr/stu/wibble/wobble/",
        )
