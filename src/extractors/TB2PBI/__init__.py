"""
Tableau to Power BI Converter Module

A Python module for converting Tableau workbooks (.twbx) to Power BI templates (.pbit).

Classes:
    TableauToPowerBIConverter: Main converter class
    TableauExtractor: Handles Tableau file extraction and parsing
    PowerBIConverter: Handles conversion to Power BI formats  
    PowerBIProjectWriter: Writes Power BI project files
    PBIToolsCompiler: Compiles projects using pbi-tools

Functions:
    convert_tableau_to_powerbi: Convenience function for conversion
    analyze_tableau_workbook: Analyze Tableau workbook structure

Example:
    from tableau_to_powerbi import convert_tableau_to_powerbi
    
    success = convert_tableau_to_powerbi('workbook.twbx', 'output.pbit')
    if success:
        print("Conversion completed successfully!")
"""

from .tableau_to_powerbi import (
    TableauToPowerBIConverter,
    TableauExtractor,
    PowerBIConverter,
    PowerBIProjectWriter,
    PBIToolsCompiler,
    TableauToPowerBIError,
    convert_tableau_to_powerbi,
    analyze_tableau_workbook
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'TableauToPowerBIConverter',  
    'TableauExtractor',
    'PowerBIConverter',
    'PowerBIProjectWriter',
    'PBIToolsCompiler',
    'TableauToPowerBIError',
    'convert_tableau_to_powerbi',
    'analyze_tableau_workbook'
]
