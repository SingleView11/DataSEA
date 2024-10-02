import os
import requests
import json, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from utils import LLMApi, clamp_prompt, clean_llm_json_res

# Get the OpenAI API key from environment variable
API_KEY = os.getenv('OPENAI_API_KEY')

# Function to split the input into chunks based on token limit
def split_into_chunks(text, max_char_len = 8888):
    chunks = []
    
    # Split the text into chunks of the given max_char_len
    for i in range(0, len(text), max_char_len):
        chunks.append(text[i:i + max_char_len])
    
    return chunks

# Function to process text of any length with chunking
def call_llm_with_chunks(instruction, text, max_tokens_per_chunk=8888, max_chunk_number = 50, model="gpt-4o-mini"):
    chunks = split_into_chunks(text, max_tokens_per_chunk)
    
    full_response = []

    for i, chunk in enumerate(chunks):
        if i > max_chunk_number:
            break
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        prompt = generate_chunk_prompt(instruction, chunk, i)
        response = LLMApi(prompt, model=model)
        # print(f"the {i} res: {response}")
        if response:
            full_response.append(response)
    
    # Combine all chunk responses into a final cohesive output
    return full_response

def generate_chunk_prompt(instruction, chunk, number):
    prompt = f"""
    Task: You are required to perform the following action on the provided text.

    Instruction:
    {instruction}

    Context:
    The text provided below is a portion(portion number: {number}) of a larger document. The text might include multiple ideas, important details, and some redundant information. You are expected to carefully read the entire chunk and execute the instruction provided above.

    Important Notes:
    - Pay close attention to the instruction and ensure that the output reflects exactly what is being asked.
    - If the instruction requires summarizing, ensure the result is concise while retaining key information.
    - If the instruction asks for rewriting, rephrase without altering the original meaning.
    - If the instruction requires generating questions or analyzing, focus on extracting important elements.
    - If there are ambiguous parts, maintain the general sense without introducing assumptions.

    Below is the text chunk that you should work on:

    [Start of Text Chunk]
    {chunk}
    [End of Text Chunk]

    Please follow the instruction precisely and produce the corresponding output.
    """
    return prompt

def generate_combination_prompt(instruction, chunk_responses):
    prompt = f"""
    Task: You are required to combine multiple responses generated from different chunks of a larger text. 
    The individual chunk responses may contain overlapping information, separate ideas, or fragmented content. 
    Your task is to combine these responses into a single cohesive and comprehensive output.

    The responses are results of such task: {instruction}, so merge them based on the task description to make sure usefuul info is not lost.

    Below are the responses generated from different chunks. Please combine them into a single well-structured and cohesive result:

    """
    
    # Adding each chunk response into the prompt
    for i, response in enumerate(chunk_responses):
        prompt += f"[Response {i+1}]\n{response}\n\n"
    
    prompt += "Please combine the above responses into a single cohesive output, following the instructions provided."
    
    return prompt

def LLM_long_api(instruction, input_text, max_chunk = 100, model="gpt-4o-mini"):
    res = call_llm_with_chunks(instruction, input_text, max_chunk_number = max_chunk, model=model)
    cb_pp = generate_combination_prompt(instruction, res)
    
    return clean_llm_json_res( LLMApi(cb_pp))

if __name__ == "__main__":
    res = LLM_long_api("you need to give me a story with some input info", "the story takes place in ancient China and is about a love storry with good ending")
    print(res)
