"""Test benchmark result schema objects."""

from unittest import TestCase

import benchtmpl.workflow.benchmark.schema as schema

import benchtmpl.workflow.parameter.declaration as pd


class TestBenchmarkResultSchema(TestCase):
    def test_column_serialization(self):
        """Test serialization of column objects."""
        # Ensure the required default value is set properly
        col = schema.BenchmarkResultColumn(
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER
        )
        self.assertEqual(col.identifier, 'col_1')
        self.assertEqual(col.name, 'Column 1')
        self.assertEqual(col.data_type, pd.DT_INTEGER)
        self.assertTrue(col.required)
        self.assertEqual(type(col.required), bool)
        self.assertFalse(col.is_default)
        self.assertTrue(col.is_desc())
        col = schema.BenchmarkResultColumn.from_dict(col.to_dict())
        self.assertEqual(col.identifier, 'col_1')
        self.assertEqual(col.name, 'Column 1')
        self.assertEqual(col.data_type, pd.DT_INTEGER)
        self.assertTrue(col.required)
        self.assertEqual(type(col.required), bool)
        self.assertFalse(col.is_default)
        self.assertTrue(col.is_desc())
        # Test serialization if required value is given
        col = schema.BenchmarkResultColumn(
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER,
            required=False,
            is_default=True,
            sort_order='ASC'
        )
        self.assertEqual(col.identifier, 'col_1')
        self.assertEqual(col.name, 'Column 1')
        self.assertEqual(col.data_type, pd.DT_INTEGER)
        self.assertFalse(col.required)
        self.assertEqual(type(col.required), bool)
        self.assertTrue(col.is_default)
        self.assertFalse(col.is_desc())
        col = schema.BenchmarkResultColumn.from_dict(col.to_dict())
        self.assertEqual(col.identifier, 'col_1')
        self.assertEqual(col.name, 'Column 1')
        self.assertEqual(col.data_type, pd.DT_INTEGER)
        self.assertFalse(col.required)
        self.assertEqual(type(col.required), bool)
        self.assertTrue(col.is_default)
        self.assertFalse(col.is_desc())

    def test_schema_serialization(self):
        """Test creating schema objects from dictionaries and vice versa."""
        s = schema.BenchmarkResultSchema.from_dict({
            schema.LABEL_RESULT_FILE: 'results.json',
            schema.LABEL_SCHEMA: [
                schema.BenchmarkResultColumn(
                    identifier='col_1',
                    name='Column 1',
                    data_type=pd.DT_INTEGER
                ).to_dict(),
                schema.BenchmarkResultColumn(
                    identifier='col_2',
                    name='Column 2',
                    data_type=pd.DT_DECIMAL,
                    required=True
                ).to_dict(),
                schema.BenchmarkResultColumn(
                    identifier='col_3',
                    name='Column 3',
                    data_type=pd.DT_STRING,
                    required=False
                ).to_dict()
            ]
        })
        self.validate_schema(s)
        # Recreate the object from its serialization
        s = schema.BenchmarkResultSchema.from_dict(s.to_dict())
        self.validate_schema(s)
        # Error cases
        with self.assertRaises(ValueError):
            doc = s.to_dict()
            doc['unknown'] = 'A'
            schema.BenchmarkResultSchema.from_dict(doc)
        with self.assertRaises(ValueError):
            doc = s.to_dict()
            del doc[schema.LABEL_RESULT_FILE]
            schema.BenchmarkResultSchema.from_dict(doc)
        with self.assertRaises(ValueError):
            schema.BenchmarkResultColumn(
                identifier='col_1',
                name='Column 1',
                data_type=pd.DT_LIST
            )

    def validate_column(self, column, identifier, name, data_type, required):
        """Ensure that the given column matches the respective arguments."""
        self.assertEqual(column.identifier, identifier)
        self.assertEqual(column.name, name)
        self.assertEqual(column.data_type, data_type)
        self.assertEqual(column.required, required)

    def validate_schema(self, schema):
        """Validate that the given schema."""
        self.assertEqual(len(schema.columns), 3)
        self.validate_column(
            column=schema.columns[0],
            identifier='col_1',
            name='Column 1',
            data_type=pd.DT_INTEGER,
            required=True
        )
        self.validate_column(
            column=schema.columns[1],
            identifier='col_2',
            name='Column 2',
            data_type=pd.DT_DECIMAL,
            required=True
        )
        self.validate_column(
            column=schema.columns[2],
            identifier='col_3',
            name='Column 3',
            data_type=pd.DT_STRING,
            required=False
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
