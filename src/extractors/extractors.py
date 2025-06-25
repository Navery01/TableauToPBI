import os
from typing import Dict, Any
import json
import yaml

import xml.etree.ElementTree as ET

class TableauDashboardExtractor:
    """
    Extracts relevant contents from a Tableau dashboard (.twb or .twbx file).
    """

    def __init__(self, tableau_file: str):
        self.tableau_file = tableau_file
        self.dashboard_data = {}

    def extract(self) -> Dict[str, Any]:
        """
        Extracts sheets, datasources, calculations, parameters, and dashboard layouts.
        """
        if self.tableau_file.endswith('.twb'):
            tree = ET.parse(self.tableau_file)
            root = tree.getroot()
        elif self.tableau_file.endswith('.twbx'):
            # For .twbx, extract .twb first (not implemented here)
            raise NotImplementedError("TWbx extraction not implemented.")
        else:
            raise ValueError("Unsupported file type.")

        self.dashboard_data['datasources'] = self._extract_datasources(root)
        self.dashboard_data['worksheets'] = self._extract_worksheets(root)
        self.dashboard_data['dashboards'] = self._extract_dashboards(root)
        self.dashboard_data['calculations'] = self._extract_calculations(root)
        self.dashboard_data['parameters'] = self._extract_parameters(root)
        return self.dashboard_data

    def _extract_datasources(self, root) -> list:
        datasources = []
        for ds in root.findall('.//datasource'):
            datasources.append({
                'name': ds.get('name'),
                'caption': ds.get('caption'),
                'connections': [conn.attrib for conn in ds.findall('.//connection')]
            })
        return datasources

    def _extract_worksheets(self, root) -> list:
        worksheets = []
        for ws in root.findall('.//worksheet'):
            worksheets.append({
                'name': ws.get('name'),
                'caption': ws.get('caption')
            })
        return worksheets

    def _extract_dashboards(self, root) -> list:
        dashboards = []
        for db in root.findall('.//dashboard'):
            dashboards.append({
                'name': db.get('name'),
                'caption': db.get('caption'),
                'worksheets': [ws.get('name') for ws in db.findall('.//worksheet')]
            })
        return dashboards

    def _extract_calculations(self, root) -> list:
        calculations = []
        for calc in root.findall('.//calculation'):
            calculations.append({
                'formula': calc.get('formula'),
                'name': calc.get('name')
            })
        return calculations

    def _extract_parameters(self, root) -> list:
        parameters = []
        for param in root.findall('.//parameter'):
            parameters.append({
                'name': param.get('name'),
                'dataType': param.get('dataType'),
                'currentValue': param.get('currentValue')
            })
        return parameters

    def export(self, format: str = 'json', output_path: str = None):
        """
        Exports the extracted dashboard data to the specified format.
        Supported formats: json, yaml, xml
        """

        if not self.dashboard_data:
            raise RuntimeError("No data extracted. Run extract() first.")

        if format == 'json':
            content = json.dumps(self.dashboard_data, indent=2)
        elif format == 'yaml':
            content = yaml.dump(self.dashboard_data)
        elif format == 'xml':
            # Simple XML export (not full fidelity)
            root = ET.Element('dashboard')
            for key, items in self.dashboard_data.items():
                section = ET.SubElement(root, key)
                for item in items:
                    entry = ET.SubElement(section, 'item')
                    for k, v in item.items():
                        ET.SubElement(entry, k).text = str(v)
            content = ET.tostring(root, encoding='unicode')
        else:
            raise ValueError("Unsupported export format.")

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content