import sqlite3
import pandas as pd

class CreateGapminderDB:
    def __init__(self):
        self.file_names = ["ddf--datapoints--gdp_pcap--by--country--time",
                           "ddf--datapoints--lex--by--country--time",
                           "ddf--datapoints--pop--by--country--time",
                           "ddf--entities--geo--country"]
        self.table_names = ["gdp_per_capita", "life_expectancy", "population", "geography"]
    def import_as_dataframe(self):
        df_dict = dict()
        for file_name, table_name in zip(self.file_names, self.table_names):
            file_path = f"data/{file_name}.csv"
            df = pd.read_csv(file_path)
            df_dict[table_name] = df
        return df_dict
    def create_database(self):
        connection = sqlite3.connect("data/gapminder.db")   #sqlite是內建模組，不用另外載入conda
        df_dict = self.import_as_dataframe()                   #把剛剛讀取的資料表放在df_dict裡面，key是table_name，value是dataframe
        for k, v in df_dict.items():                        #key,value全部都要，所以用items()
            v.to_sql(name=k, con=connection, index=False, if_exists="replace")
        drop_view_sql = """
        DROP VIEW IF EXISTS plotting;
        """                                          #建立檢視表，不能有同名
        create_view_sql = """
        CREATE VIEW plotting AS
        SELECT geography.name AS country_name,
               geography.world_4region AS continent,
               gdp_per_capita.time AS dt_year,
               gdp_per_capita.gdp_pcap AS gdp_per_capita,
               life_expectancy.lex AS life_expectancy,
               population.pop AS population
          FROM gdp_per_capita
          JOIN geography
            ON gdp_per_capita.country = geography.country
          JOIN life_expectancy
            ON gdp_per_capita.country = life_expectancy.country AND
               gdp_per_capita.time = life_expectancy.time
          JOIN population
            ON gdp_per_capita.country = population.country AND
               gdp_per_capita.time = population.time
         WHERE gdp_per_capita.time < 2024;
        """  
        #執行建立檢視表的敘述
        cur = connection.cursor()
        cur.execute(drop_view_sql)
        cur.execute(create_view_sql)
        connection.close()

create_gapminder_db = CreateGapminderDB()  #初始化類別
create_gapminder_db.create_database()