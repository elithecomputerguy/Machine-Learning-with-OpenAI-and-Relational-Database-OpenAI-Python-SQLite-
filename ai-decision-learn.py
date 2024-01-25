import openai
import ai_function
import os
import sqlite3

client = openai.OpenAI(api_key='APIKEY',)

current_directory = os.path.dirname(os.path.abspath(__file__))
db_name = 'ai.db'
db_path = os.path.join(current_directory, db_name)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
create_table = '''
  create table if not exists decision(
    id integer primary key,
    query text,
    response text
  )
'''
cursor.execute(create_table)
conn.commit()

file_name = 'ai_function.py'
file_path = os.path.join(current_directory, file_name)

with open(file_path, 'r') as file_function:
  file_function = file_function.read()

def ai_request(file_function, query):
  response = client.chat.completions.create(
    messages=[
      {"role": "system", "content": "You are assisting in choosing the most suitable Python function for a user request."},
      {"role": "assistant", "content": "You will be provided with available function names for this program."},
      {"role": "assistant", "content": "Please only provide the name of the function, without additional information or responses."},
      {"role": "assistant", "content": "Do not provide any response other than the correct function name."},
      {"role": "assistant", "content": file_function},
      {"role": "user", "content": query}
    ],
    model="gpt-3.5-turbo",
  )
  response = response.choices[0].message.content
  return  response

while True:

  query = input('How can I help?   ')
  query = query.strip()
  query = query.lower()
  os.system('clear')
  print(f'Query:\n\t {query}')      
  if 'exit' in query:
    conn.close()
    break

  try:
    sql_find = 'select * from decision where query = ?'
    cursor.execute(sql_find, (query,))
    result = cursor.fetchone()
  except:
    print('SQL Query for Find Did Not Work')

  if result == None:
    response = ai_request(file_function, query)
    sql = 'insert into decision(query,response) values(?,?)'
    cursor.execute(sql,(query, response))
    conn.commit()
    print('Query Not in Database -- OpenAI Used')
    print(f'OpenAI Response:\n\t {response}')
    print(f'Added to Database:\n\t {query} = {response}')
  else:
    response = result[2]
    print('Query in Database -- SQLite Used')
    print(f'Result:\n\t {result}')
    print(f'Result List:\n\t {result[1]} -- {result[2]}')

  if 'hello' in response:
    answer = ai_function.hello()
  elif 'goodbye' in response:
    answer = ai_function.goodbye()
  elif 'understand' in response:
    answer = ai_function.dont_understand()  
  elif 'time' in response:
    answer = ai_function.get_time()
  elif 'weather' in response:
    answer = ai_function.get_weather()
  elif 'joke' in response:
    answer = ai_function.get_joke(query)

  print(f'Message:\n\t {answer}')