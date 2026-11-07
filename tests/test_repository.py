import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('normalize_events', ROOT/'scripts/normalize_events.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.data = (ROOT/'fixtures/synthetic-events.xml').read_bytes()

    def test_named_target_is_not_subject(self):
        record = module.normalize(self.data)[0]
        self.assertEqual(record['fields']['TargetUserName'], 'demo-user')
        self.assertEqual(record['fields']['SubjectUserName'], 'WS1$')
        self.assertEqual(record['event_id'], 4625)

    def test_kerberos_values_preserved_without_inference(self):
        records = module.normalize(self.data)
        self.assertEqual(records[1]['fields']['TicketEncryptionType'], '0x12')
        self.assertEqual(records[1]['fields']['PreAuthType'], '0')
        self.assertEqual(records[2]['fields']['Status'], '0x0')

    def test_utf16_windows_export(self):
        self.assertEqual(module.normalize(self.data.decode().encode('utf-16')), module.normalize(self.data))

    def test_duplicate_fields_retained(self):
        data = self.data.replace(b'<Data Name="PreAuthType">0</Data>', b'<Data Name="PreAuthType">0</Data><Data Name="PreAuthType">2</Data>')
        self.assertEqual(module.normalize(data)[1]['fields']['PreAuthType'], ['0', '2'])

    def test_no_dtd_even_in_utf16(self):
        for data in (b'<!DOCTYPE Events><Events/>', '<!DOCTYPE Events><Events/>'.encode('utf-16')):
            with self.assertRaises(ValueError): module.normalize(data)

    def test_utf16_without_bom_rejected(self):
        with self.assertRaises(ValueError):
            module.normalize('<!DOCTYPE Events><Events/>'.encode('utf-16-le'))

    def test_invalid_xml(self):
        with self.assertRaises(ET.ParseError): module.normalize(b'<Events>')

    def test_size_limit(self):
        with self.assertRaises(ValueError): module.normalize(b'x'*(module.MAX_BYTES+1))

    def test_missing_event_id(self):
        data = self.data.replace(b'<EventID>4625</EventID>', b'')
        with self.assertRaises(ValueError): module.normalize(data)

    def test_unknown_root(self):
        with self.assertRaises(ValueError): module.normalize(b'<Other/>')

    def test_empty_collection(self):
        self.assertEqual(module.normalize(b'<Events/>'), [])


class RepositoryContractTests(unittest.TestCase):
    def test_detection_manifest_complete(self):
        rules = json.loads((ROOT/'detections/catalog.json').read_text())
        self.assertEqual(len({r['id'] for r in rules}), len(rules))
        files = {str(p.relative_to(ROOT)) for p in (ROOT/'detections').rglob('*') if p.suffix in ('.spl','.kql')}
        self.assertEqual(files, {r['path'] for r in rules})
        for rule in rules:
            self.assertTrue(rule['prerequisites'] and rule['false_positives'] and rule['expected'])
            self.assertIn(rule['status'], ('lab-validation-pending','cloud-deployment-pending'))

    def test_spl_search_contract(self):
        # Static checks only: these do not parse or execute SPL in Splunk.
        for p in (ROOT/'detections/splunk').glob('*.spl'):
            text = p.read_text()
            self.assertTrue(text.startswith('index=ad_lab earliest='), p.name)
            self.assertNotRegex(text, r'(?m)^\s*#')
            self.assertIn('source=', text)

    def test_cloud_roles_use_separate_tables(self):
        self.assertIn('AzureActivity', (ROOT/'detections/sentinel/azure-rbac-changes.kql').read_text())
        self.assertIn('AuditLogs', (ROOT/'detections/sentinel/entra-role-assignment.kql').read_text())
        self.assertIn('AADServicePrincipalSignInLogs', (ROOT/'detections/sentinel/service-principal-signins.kql').read_text())

    def test_triage_does_not_execute_containment(self):
        flow = json.loads((ROOT/'playbooks/triage-workflow.json').read_text())
        actions = flow['actions']
        self.assertEqual({a['type'] for a in actions.values()}, {'Compose','Response'})
        self.assertIs(actions['Build_review_record']['inputs']['containmentExecuted'], False)

    def test_sysmon_xml_well_formed(self):
        root = ET.parse(ROOT/'configs/sysmon/lab.xml').getroot()
        self.assertEqual(root.tag, 'Sysmon')
        self.assertIsNotNone(root.find('.//ProcessAccess/TargetImage'))

    def test_documentation_links_resolve(self):
        for p in ROOT.rglob('*.md'):
            if '.git' in p.parts: continue
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                if '://' in link or link.startswith('#'): continue
                target=link.split('#',1)[0]
                if target: self.assertTrue((p.parent/target).exists(), f'{p}: {link}')


if __name__ == '__main__':
    unittest.main()
