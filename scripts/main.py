import os
import praw
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import (AIMessage,HumanMessage,SystemMessage)
from dotenv import load_dotenv
from database.models import Stock
from sqlalchemy.orm import sessionmaker
load_dotenv()
# Assuming the engine is defined in models.py
from database.models import engine
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET= os.getenv('CLIENT_SECRET')
SCRIPT_NAME = os.getenv('SCRIPT_NAME')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD= os.getenv('REDDIT_PASSWORD')
OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')
# Configure your OpenAI API key for Langchain

from langchain.prompts import ChatPromptTemplate
chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model_name="gpt-3.5-turbo")

# Initialize Langchain with OpenAI
langchain = ChatOpenAI(openai_api_key=OPENAI_API_KEY,model_name="gpt-3.5-turbo")

database_password = os.getenv('DATABASE_PASSWORD')

Session = sessionmaker(bind=engine)
session = Session()

# Example usage: adding a new Stock
# new_stock = Stock(ticker="GOOG", name="Google", comment="Tech Giant")
def generate_response(comment):
    try:
        systemMessage="In text check whether it contains stock name or ticker. Answer as shortly as possible, use array of objects with property ticker which holds ticker or name if not possible for ticker return NoData. Example: [{\"ticker\":\"MSFT\"}, {\"ticker\":\"NoData\"}]"
#         prompt = ChatPromptTemplate.from_messages([
#     ("system", "In text before check whether it contains stock name or ticker if no return NoData"),
#     ("user", "{comment_body}")
# ])
        messages = [SystemMessage(content=systemMessage),HumanMessage(content=comment.body)]

        # Generate a response using Langchain
        response = chat(messages)
        dbData = {"response": response.content, "score":comment.score}
        print(f"Response: {dbData}\n")
        return dbData
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error in response."

def main():
    # Initialize the PRAW Reddit instance
    reddit = praw.Reddit(client_id=CLIENT_ID, 
                         client_secret=CLIENT_SECRET, 
                         user_agent=SCRIPT_NAME,
                         username=REDDIT_USERNAME, 
                         password=REDDIT_PASSWORD)

    # Replace 'submission_id' with the actual submission ID
    submission_id = '18kngs6'
    submission = reddit.submission(id=submission_id)

    # Expand the comment tree and iterate through comments
    submission.comments.replace_more(limit=None)
    aggregate_scores = {}
    comment_counter = 0
    num_top_comments = len(submission.comments)

    print(f"Number of top-level comments: {num_top_comments}")


    for top_level_comment in submission.comments.list():
        if comment_counter < 3:
            comment_counter += 1
            # dataForDB = generate_response(top_level_comment)  
            for reply in top_level_comment.replies.list():
                dataForDB = generate_response(reply)  # Your function to generate dataForDB
               
                if dataForDB['response']:
                    try:
                        response = json.loads(dataForDB['response'])
                        score = dataForDB['score']

                        for ticker_info in response:
                            ticker = ticker_info['ticker']
                            aggregate_scores[ticker] = aggregate_scores.get(ticker, 0) + score

                    except json.JSONDecodeError as e:
                      print(f"JSON decoding failed: {e.msg}, in response: {dataForDB['response']}")

    # Convert the aggregated scores to the desired list format
    result = [{"ticker": ticker, "score": score} for ticker, score in aggregate_scores.items()]

    print(result)




if __name__ == "__main__":
    main()