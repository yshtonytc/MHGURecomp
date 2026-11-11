"""A library ID is accepted only for identical ABI sources/flags and matching stock programs."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('custom_identity',ROOT/'custom/align_gamelib.py')
identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)

class IdentityTests(unittest.TestCase):
    def test_lf_official_build(self):
        source=[b'one\ntwo\n',b'three\n'];flags='-O1 -DTEST'
        value=hashlib.sha256(b''.join(source)+(flags+'\n').encode()).hexdigest()[:16]
        binary=b'program'+value.encode()+b'\0'
        result=identity.choose_identity(source,flags,binary,binary)
        self.assertEqual(result['identity'],value);self.assertEqual(result['line_endings'],'LF')

    def test_crlf_official_build_with_lf_checkout(self):
        source=[b'one\ntwo\n',b'three\n'];flags='-O1 -DTEST'
        value=hashlib.sha256(b''.join(s.replace(b'\n',b'\r\n') for s in source)+(flags+'\n').encode()).hexdigest()[:16]
        binary=value.encode()+b'\0'
        result=identity.choose_identity(source,flags,binary,binary)
        self.assertEqual(result['identity'],value);self.assertEqual(result['line_endings'],'CRLF')

    def test_source_or_flag_changes_are_not_accepted(self):
        source=[b'unchanged\n'];flags='-O1'
        value=hashlib.sha256(source[0]+b'-O1\n').hexdigest()[:16].encode()+b'\0'
        with self.assertRaises(ValueError):identity.choose_identity([b'changed\n'],flags,value,value)
        with self.assertRaises(ValueError):identity.choose_identity(source,'-O2',value,value)

    def test_official_host_and_library_must_agree(self):
        source=[b'unchanged\n'];value=hashlib.sha256(source[0]+b'-O1\n').hexdigest()[:16].encode()+b'\0'
        with self.assertRaises(ValueError):identity.choose_identity(source,'-O1',value,b'different library')

if __name__=='__main__':unittest.main()
