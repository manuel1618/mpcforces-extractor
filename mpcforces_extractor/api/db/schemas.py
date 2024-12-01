from sqlmodel import SQLModel


class RunExtractorRequest(SQLModel, table=False):
    """
    Request model for running the extractor
    """

    fem_filename: str
    mpcf_filename: str
    spcf_filename: str


class DatabaseRequest(SQLModel, table=False):
    """
    Request model for running the extractor
    """

    database_filename: str
