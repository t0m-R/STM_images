import pickle
import pymysql
import sqlalchemy.types
from sqlalchemy import create_engine
import pandas as pd


def fix_columns_types(
        df: pandas.DataFrame) -> dict:
    """ Select the correct types for the MYSQL columns from the DataFrame columns.
        Return a dictionary with column name as keys and column type as values. """
    dtypes_dict = {}
    for column, dtype in zip(df.columns, df.dtypes):
        if "object" in str(dtype):
            dtypes_dict.update({column: sqlalchemy.types.NVARCHAR(length=255)})
        if "datetime" in str(dtype):
            dtypes_dict.update({column: sqlalchemy.types.DateTime()})
        if "float" in str(dtype):
            dtypes_dict.update({column: sqlalchemy.types.Float(precision=3, asdecimal=True)})
        if "int" in str(dtype):
            dtypes_dict.update({column: sqlalchemy.types.INT()})
    return dtypes_dict


def main():
    # Create connection object to MYSQL db
    db_connection_str = 'mysql+pymysql://user:passwd@host/stm_images'
    db_connection = create_engine(db_connection_str)

    # load clean metadata dataframe
    with open('clean_meta.pkl', 'rb') as f:
        clean_meta = pickle.load(f)

    # write dataframe in new table "clean_meta"
    columns_dtype = fix_column_types(clean_meta)
    clean_meta.to_sql('clean_meta', db_connection, index=False, dtype=columns_dtype)


if __name__ == "__main__":
    main()
