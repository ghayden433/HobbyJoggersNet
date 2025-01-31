import pandas as pd
from sqlalchemy import create_engine, text, inspect, delete, MetaData, Table

#parameters 
#   data - dataframe
#   the following are used for the mysql query, all strings
#      Season
#      Gender
#      Level
#      Event
#      Year
#converts to pandas dataframe and sends to mysql db
def df_to_MySQL(newData, Season, Gender, Level, Event, Year):
    #connect to database
    engine = create_engine('<PlaceHolder>')
    metadata = MetaData()
    inspector = inspect(engine)

    # query database for the current information to be added
    with engine.connect() as connection:
        if f'year{Year}' in inspector.get_table_names():
            #get old data
            query = (f'''
                Select DISTINCT * FROM year{Year}
                WHERE Season="{Season}"
                AND Gender="{Gender}"
                AND Level="{Level}"
                AND Event="{Event}"''')
            currentData = pd.read_sql(query, engine)
            # remove old data so that it doesn't get duplicated
            with connection.begin():
                deleteQuery = (f'''
                    DELETE FROM year{Year}
                    WHERE Season="{Season}"
                    AND Gender="{Gender}"
                    AND Level="{Level}"
                    AND Event="{Event}"''')
                connection.execute(text(deleteQuery))
        else: 
            createQuery = (f'''
                CREATE TABLE year{Year} (
                Season VARCHAR(255),
                Gender VARCHAR(255),
                Level VARCHAR(255),
                Event VARCHAR(255),
                Name VARCHAR(255),
                Grade VARCHAR(255),
                Mark VARCHAR(255),
                PerformanceDate VARCHAR(255),
                Results VARCHAR(255)
                ) COMMENT = 'YEAR'
                ''')
            connection.execute(text(createQuery))
            currentData = pd.DataFrame()

    # concatenate the data, sort, and keep the top 1000 times
    if not currentData.empty:
        data = pd.concat([newData, currentData], axis=0, ignore_index=True)

        #data['Time'] = pd.to_datetime(data['Mark'], format=f'%H:%M:%S.%f')
        data.sort_values(by='Mark', ascending=True, inplace=True) 
        data.drop(data[data['Mark'] == ''].index, inplace=True) 
        data = data.head(1000)
        #data = data.drop('Time', axis=1)

    else:
        data = newData    

    try:
        with engine.connect() as connection:
            data.to_sql(
                name=f'year{Year}',      # Name of the table
                con=connection,          # SQLAlchemy engine
                if_exists='append',      # append new values
                index=False              # Don't write the df indicies as a row
            )

    except Exception as error:
        print(f"Connection failed: {error}")