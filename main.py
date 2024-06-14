import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import OpenAI


# import openai
# from dotenv import load_dotenv

# load_dotenv()

# # Get the API key from the environment variable
# api_key = os.getenv("OPENAI_API_KEY")

# # Initialize the OpenAI client with the API key
# openai.api_key = api_key

# client = OpenAI(api_key=api_key)

# just put api key here, dont know how to put into env
api_key = ""

client = OpenAI(api_key=api_key)

def talk(prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content.strip()





# connect my local sql database, need mysqlconnector, username:password/database name
db_uri = "mysql+mysqlconnector://root:dennis@localhost:3306/products"
db = SQLDatabase.from_uri(db_uri)



# Load environment variables from .env file
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')  
# print(os.environ['OPENAI_API_KEY'])




template = """
Based on the table schema below, write a SQL query that would answer the user's question.
{schema}
Question: {question}
SQL Query
"""

prompt = ChatPromptTemplate.from_template(template)

prompt.format(schema="my schema", question="how many batteries are there?")

def get_schema(_):
    return db.get_table_info()

# print(get_schema(None))

llm = ChatOpenAI()
sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm.bind(stop='\nSQL Result:')
    | StrOutputParser()
)

# generates a sql query from user question pretty cool
# print(sql_chain.invoke({'question': 'how many batteries are there?'}))


# now we do the same thing but now get the answer

template = """
Based on the table schema below, question, sql query, and sql response, write a natural language response.
{schema}
Question: {question}
SQL Query: {query}
SQL Response: {response}
"""
prompt = ChatPromptTemplate.from_template(template)
def run_query(query):
    return db.run(query)
# example holy shit this actually works
# print(run_query('SELECT COUNT(*) AS total_batteries FROM battery;'))

full_chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
        schema=get_schema,
        # double check the variables are correct
        # response=lambda variables: print(variables)
        response=lambda variables: run_query(variables['query'])
    )
    | prompt
    | llm
    | StrOutputParser()
)

# print(full_chain.invoke({'question': 'how many batteries are there?'}))
# print(full_chain.invoke({'question': 'how many blankets are there?'}))
# print(full_chain.invoke({'question': 'how many scenarios are there?'}))




mode = "chat"  # Initial mode is chat

while True:
    if mode == "chat":
        user_input = input('You: ')
        if user_input.lower() in ['quit', 'exit']:
            break
        if user_input.lower() == 'database':
            mode = "database"
            print("Switching to database mode. Type 'chat' to switch back.")
            continue
        response = talk(user_input)
        print('ChatGPT: ' + response)
    elif mode == "database":
        if user_input.lower() in ['quit', 'exit']:
            break
        sql_input = input('Database Query: ')
        if sql_input.lower() in ['chat']:
            mode = "chat"  # Switch back to chat mode
            continue
        response = full_chain.invoke({'question': sql_input})
        print('SQL Response: ' + response)
