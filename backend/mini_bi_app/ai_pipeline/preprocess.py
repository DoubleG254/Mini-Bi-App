def preprocess(df):
    df = df.dropna(how='all')
    df = df.drop_duplicates()
    df.columns = df.columns.str.strip().str.lower()
    return df