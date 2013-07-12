"""
SBtab
=====

Provides:
    1. Automatic tranlations from SBtab to Python objects
    2. Automatic verification of format and files
    2. Easily callable and changeable entries in tables

SBtab is a uniforming spreadsheet format and can be used to describe
biochemical models. Furthermore, it is a useful format to store information
...
bla bla description...

How to use:
Shortly ...

How to load tablib object:

"""

#!/usr/bin/env python
import re
import copy
import tablib
import tablibIO

tables_without_name = []


def oneOrMany(spreadsheet_file):
    """
    Check whether there are one or many SBtabs in an SBtab document.
    Return every SBtab table as single tablib object.

    Parameters
    ----------
    spreadsheet_file : tablib object
        Tablib object containing one or more SBtabs.

    Returns
    -------
    sbtabs : list
        List of tablib objects containing just one SBtab.
    """
    sbtabs = []

    # Copy file, one for iteration, one for cutting
    sbtab_document = copy.deepcopy(spreadsheet_file)
    # Create new tablib object
    sbtab = tablib.Dataset()

    # Cut sbtab_document, write tablib objects in list
    if len(spreadsheet_file) != 0:  # If file not empty
        for row in spreadsheet_file:
            if len(sbtab) == 0:  # If first line, append line w/o checking
                sbtab.rpush(sbtab_document.lpop())
            else:
                for i, entry in enumerate(row):
                    # If header row (!!), write to new tablib object and store the last one
                    if entry.startswith('!!'):
                        sbtabs.append(sbtab)
                        sbtab = tablib.Dataset()
                        sbtab.rpush(sbtab_document.lpop())
                        break
                    # If not header row, append line to tablib object
                    if len(row) == i + 1:
                        sbtab.rpush(sbtab_document.lpop())
        sbtabs.append(sbtab)

    # Return list of tablib objects
    return sbtabs


class SBtabError(Exception):
    """Base class for errors in the SBtab class."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class SBtabTable():
    """
    SBtab Table (version 1.00 07/12/2013)
    """
    def __init__(self, table, filename):
        """
        Create SBtab Python object.

        Parameters
        ----------
        table : tablib object
            Containing one SBtab.
        filename : str
            Filename with extension.

        Notes
        -----
        Raise error if file format is invalid, only 'tsv', 'csv', 'ods' or 'xls' are supported.
        """
        self.filename = filename  # Needed to be able to adress it from outside of the class for writing and reading
        self.table = table

        # Identification of file type (tsv/csv/ods/xls)
        if not (str(filename).endswith('.tsv') or str(filename).endswith('.csv') or str(filename).endswith('.ods') or str(filename).endswith('.xls')):
            raise SBtabError('The given file format is not supported: ' + filename + '. Please use ".tsv", ".csv", ".ods" or ".xls" instead.')

        # Read the header row from table
        self.header_row = self.getHeaderRow(self.table)
        # Read the table information from header row
        self.table_type, self.table_name, self.table_document, self.table_level, self.table_version = self.getTableInformation(self.header_row)
        # Read the columns of the table
        columns, inserted_column = self.getColumns(self.table)
        self.columns = columns.keys()
        self.columns_dict = columns
        # Read data rows
        self.value_rows = self.getRows(table, self.table_type, inserted_column)
        # Create tablib Dataset instance with new SBtab table
        self.sbtab_dataset = self.createSBtabDataset()

    def getHeaderRow(self, table):
        """
        Extract the !!-header row from the SBtab file.

        Parameters
        ----------
        table : tablib object
            Containing one SBtab.

        Returns
        -------
        header_row : str
            !!-headre row of SBtab table.

        Notes
        -----
        Raise error if no header row could be find in the table.
        """
        # Find header row
        for row in table:
            for entry in row:
                if entry.startswith('!!'):
                    header_row = row
                    break

        # save string or return None
        if not header_row:
            raise SBtabError('This is not a valid SBtab table, please use validator to check format!')
        else:
            header_row = ' '.join(header_row)

        # Replace double quotes by single quotes
        header_row = header_row.replace('"', '\'')

        return header_row

    def getTableInformation(self, header_row):
        """
        Read header row and store its information.

        Parameters
        ----------
        header : str
            Header row of the SBtab table.

        Returns
        -------
        table_type : str
            Table type of the SBtab table.
        table_name : str
            Name of the SBtab table.
        table_document : str
            Document type of SBtab table.
        table_level : str
            Level of SBtab table.
        table_version : str
            Version of the SBtab table.

        Notes
        -----
        If no name was set, name equals table_type and number of occurences of unnamed
        tables of same type.
        Raise error if no table type is defined.
        """

        # Initialise variables for unnamed table handling
        global tables_without_name
        no_name_counter = 0

        # Save TableType, otherwise raise Error
        tt = re.search('TableType=\'([^\']*)\'', header_row)
        if tt:
            table_type = tt.group(1)
        else:
            raise SBtabError('The TableType of the SBtab is not defined!')

        # Save TableName, otherwise give name with number of unnamed tables
        tn = re.search('Table=\'([^\']*)\'', header_row)
        if tn:
            table_name = tn.group(1)
        else:
            tables_without_name.append(table_type)
            for table_no_name in tables_without_name:
                if table_type == table_no_name:
                    no_name_counter = no_name_counter + 1
            table_name = table_type.capitalize() + '_' + str(no_name_counter)

        # Save TableDocument, otherwise return None
        td = re.search('Document=\'([^\']*)\'', header_row)
        if td:
            table_document = td.group(1)
        else:
            table_document = None

        # save TableLevel, otherwise return None
        tl = re.search('Level=\'([^\']*)\'', header_row)
        if tl:
            table_level = tl.group(1)
        else:
            table_level = None

        # save TableVersion, otherwise return None
        tv = re.search('Version=\'([^\']*)\'', header_row)
        if tv:
            table_version = tv.group(1)
        else:
            table_version = None

        return table_type, table_name, table_document, table_level, table_version

    def getColumns(self, table):
        """
        Extract the column names of the table, add first column name if necessary.

        Parameters
        ----------
        table : tablib object
            Containing one SBtab.

        Returns
        -------
        columns : dict
            dict of colunm names (str) as key and position (int) as value.
        inserted_column : Boolean
            True, if mandatory first column was set automatically.

        Notes
        -----
        First entry has to be the table type.
        Adds first entry in the list, if it corresponds not with the table type.
        See specification for further informations.
        """
        # Save list of main column
        for row in table:
            for entry in row:
                if entry.startswith('!') and not entry.startswith('!!'):
                    column_names = list(row)
                    break

        # Insert mandatory first column if not existent
        inserted_column = False
        if not column_names[0].title() == '!' + self.table_type.title():
            column_names.insert(0, '!' + self.table_type.title())
            inserted_column = True

        # Get column positions
        columns = {}
        for i, column in enumerate(column_names):
            columns[column] = i

        return columns, inserted_column

    def getRows(self, table, table_type='table', inserted=False):
        """
        Extract the rows of the SBtab, add first column if necessary.

        Parameters
        ----------
        table : tablib object
            Containing one SBtab.
        table_type : str (default 'table')
            Table type of the SBtab table.
        inserted : Boolean
            True, if mandatory first column was set automatically.

        Returns
        -------
        value_rows : list
            List containing the entries of the SBtab table.

        Notes
        -----
        If first column was set automatically, "inserted" is set to True.
        The entries in the first column are then an abbreviation of the table type
        and the number of the current row.
        See specification for further informations.
        """
        # Add row to value_rows if row doesn't contain entries starting with '!'
        value_rows = []
        for row in table:
            for i, entry in enumerate(row):
                if entry.startswith('!'):
                    break
                else:
                    if len(row) == i + 1:
                        value_rows.append(list(row))
        # Insert value column if mandatory column was added
        if inserted:
            if table_type == 'table':
                for i, row in enumerate(value_rows):
                    row.insert(0, 'Table' + str(i + 1))
            else:
                for i, row in enumerate(value_rows):
                    row.insert(0, table_type[0].upper() + table_type[- 1].lower() + str(i + 1))

        return value_rows

    def changeValue(self, row, column, new):
        """
        Change single value in the SBtab table by position in the table.

        Parameters
        ----------
        row : int
            Number of row in the table.
        column : int
            Number of column in the table.
        new : str
            New entry.

        Return
        ------

        Notes
        -----
        Old value will be overwritten.
        """
        self.value_rows[row - 1][column - 1] = new

    def changeValueByName(self, row, column, new):
        """
        Change singe value in the SBtab by name of column and row

        Parameters
        ----------
        row : str
            Name of the first entry in row
        column : str
            Name of the column (without '!')
        new : str
            New entry.
        """
        col = self.columns_dict['!' + column]
        for r in self.value_rows:
            if r[0] == row:
                r[col] = new

    def createSBtabDataset(self):
        """
        Create a tablib object of the SBtab Python object.

        Parameters
        ----------

        Returns
        -------
        sbtab_dataset : tablib object
            Tablib dataset of the SBtab Python object.

        """
        # Initialise variables
        sbtab_temp = []
        sbtab_dataset = tablib.Dataset()
        header = self.header_row.split(' ')

        # Delete spaces in header, main column and data rows
        header = [x.strip(' ') for x in header]
        self.columns = [x.strip(' ') for x in self.columns]
        for row in self.value_rows:
            try:
                for entry in row:
                    entry = entry.strip(' ')
            except:
                continue

        # Add header, main column and data rows to temporary list object
        sbtab_temp.append(header)
        sbtab_temp.append(self.columns)
        for row in self.value_rows:
            sbtab_temp.append(row)

        # Delete all empty entries at the end of the rows
        for row in sbtab_temp:
            while not row[-1]:
                del row[-1]

        # Make all rows the same length
        longest = max([len(x) for x in sbtab_temp])
        for row in sbtab_temp:
            if len(row) < longest:
                for i in range(longest - len(row)):
                    row.append('')
                sbtab_dataset.append(row)
            else:
                sbtab_dataset.append(row)

        sbtab_dataset.header = header

        return sbtab_dataset

    def addRow(self, row_list, position=None):
        """
        Add row to the table, if postion is None at the end of it.

        Parameters
        ----------
        row_list : list
            List of strings, containing the entries of the new row.
        position : int
            Position of new row in the table, 0 is on top.
        """
        # Empty column to fill up sbtab_dataset with ''
        empty_list = []

        # If new row is to small, add empty entries to new row
        if len(row_list) < len(self.sbtab_dataset.dict[0]):
            for i in range(len(self.sbtab_dataset.dict[0]) - len(row_list)):
                row_list.append('')
        # If new row is too long, add empty entries to sbtab_dataset
        elif len(row_list) > len(self.sbtab_dataset.dict[0]):
            for i in range(len(self.sbtab_dataset.dict)):
                empty_list.append('')
            for i in range(len(row_list) - len(self.sbtab_dataset.dict[0])):
                self.sbtab_dataset.rpush_col(empty_list)
        # If no position is set, add new row to the end
        if not position:
            self.sbtab_dataset.rpush(row_list)
        else:
            self.sbtab_dataset.insert(position, row_list)

    def addColumn(self, column_list, position=None):
        """
        Add column to the table, if position is None at the end of it.

        Parameters
        ----------
        column_list : list
            List of strings, containing the entries of the new column.
        position : int
            Positino of new column in the table, 0 is left.
        """
        # Empty column to fill up sbtab_dataset with ''
        empty_list = []

        # If new column is to small, add empty entries to new column
        if len(column_list) < len(self.sbtab_dataset.dict):
            for i in range(len(self.sbtab_dataset.dict) - len(column_list)):
                column_list.append('')
        # If new column is to long, add empty entries to sbtab_dataset
        elif len(column_list) > len(self.sbtab_dataset.dict):
            for i in range(len(self.sbtab_dataset.dict)[0]):
                empty_list.append('')
            for i in range(len(column_list) - len(self.sbtab_dataset.dict[0])):
                self.sbtab_dataset.rpush(empty_list)
        # If no position is set, add new column to the end
        if not position:
            self.sbtab_dataset.rpush_col(column_list)
        else:
            self.sbtab_dataset.insert_col(position, column_list)

    def writeSBtab(self, format_type, filename, sbtab_dataset):
        """
        Write SBtab tablib object to file.

        Parameters
        ----------
        format_type : str
            File extension of the SBtab file. ('tsv', 'csv', 'ods', 'xls')
        filename : str
            Filename of the SBtab file without extension.
        sbtab_dataset : tablib object
            Tablib object of the SBtab table

        Returns
        -------

        Notes
        -----
        Raise error if file format is invalid.
        """
        if format_type == 'tsv':
            tablibIO.writeTSV(sbtab_dataset, self.table_name)
        elif format_type == 'csv':
            tablibIO.writeCSV(sbtab_dataset, self.table_name)
        elif format_type == 'ods':
            tablibIO.writeODS(sbtab_dataset, self.table_name)
        elif format_type == 'xls':
            tablibIO.writeXLS(sbtab_dataset, self.table_name)
        else:
            raise SBtabError('The given file format is not supported: ' + filename + '. Please use ".tsv", ".csv", ".ods" or ".xls" instead.')
