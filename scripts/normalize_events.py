#!/usr/bin/env python3
"""Extract named Windows Event XML fields; independent of localized message text.

Input: one Event or an Events wrapper produced by Export-LabEvents.ps1.
Output is sensitive by default: keep it in artifacts/, not in Git.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

MAX_BYTES = 20 * 1024 * 1024
NS = {'e': 'http://schemas.microsoft.com/win/2004/08/events/event'}


def normalize(data):
    if len(data) > MAX_BYTES:
        raise ValueError('XML exceeds the 20 MiB limit')
    # Decode common Windows exports before checking declarations; do not permit
    # DTD/entity expansion, including UTF-16 encoded declarations.
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        text = data.decode('utf-16')
    else:
        text = data.decode('utf-8-sig')
        if '\x00' in text:
            raise ValueError('UTF-16 input must include a byte-order mark')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD/entity declarations are not supported')
    root = ET.fromstring(text)
    tag = '{' + NS['e'] + '}Event'
    if root.tag == tag:
        events = [root]
    elif root.tag == 'Events':
        events = list(root)
    else:
        raise ValueError('Expected a Windows Event or an Events wrapper')
    records = []
    for event in events:
        if event.tag != tag:
            raise ValueError('Unexpected element in Events wrapper')
        system = event.find('e:System', NS)
        if system is None:
            raise ValueError('Missing System element')
        event_id = system.findtext('e:EventID', namespaces=NS)
        if not event_id or not event_id.isdecimal():
            raise ValueError('Missing or invalid EventID')
        clock = system.find('e:TimeCreated', NS)
        provider = system.find('e:Provider', NS)
        fields = {}
        for entry in event.findall('e:EventData/e:Data', NS):
            name = entry.get('Name')
            if not name:
                continue
            value = entry.text or ''
            if name not in fields:
                fields[name] = value
            elif isinstance(fields[name], list):
                fields[name].append(value)
            else:
                fields[name] = [fields[name], value]
        records.append({
            'event_id': int(event_id),
            'timestamp': clock.get('SystemTime') if clock is not None else None,
            'computer': system.findtext('e:Computer', namespaces=NS),
            'channel': system.findtext('e:Channel', namespaces=NS),
            'provider': provider.get('Name') if provider is not None else None,
            'fields': fields,
        })
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    with args.input.open('rb') as source:
        records = normalize(source.read(MAX_BYTES + 1))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Never silently overwrite evidence.
    with args.output.open('x', encoding='utf-8') as target:
        json.dump(records, target, ensure_ascii=False, indent=2)
        target.write('\n')
    print(f'Normalized {len(records)} events. Review before sharing; no redaction is performed.')


if __name__ == '__main__':
    main()
