from dotenv import load_dotenv
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
# from langchain import OpenAI, SQLDatabase

load_dotenv()
db_uri = "mysql+mysqlconnector://root:dennis@localhost:3306/products"
db = SQLDatabase.from_uri(db_uri)
llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
db_chain = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
# print(db_chain.invoke('how many rows are there in this db'))
print(db_chain.invoke('list all the tables in this db'))


