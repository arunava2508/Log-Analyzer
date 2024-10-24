import os
import time
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from unittest.mock import patch

# Set up OpenAI API Key (use environment variable in production)
openai_api_key = os.getenv("OPENAI_API_KEY", "sk-WX5PGs_qEwbeZq0BtSWixyHsFz45PAm1fMtb9hN3IgT3BlbkFJA_vEbR_V4HZLKw2PGoVV4qwAVKvbG8wJhoi4LJP5gA")
llm = OpenAI(api_key=openai_api_key)

# Path to the folder containing log files
log_folder_path = "C:\Log"

# Function to read all log files in the folder
def load_logs_from_folder(folder_path):
    logs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".log"):  # Filter only .log files (adjust if needed)
            with open(os.path.join(folder_path, filename), "r") as file:
                logs.append(file.read())
    return logs

# Function for analyzing a chunk of log
def analyze_log_chunk(log_chunk):
    # If testing, use a mock result instead of actual OpenAI API call
    if os.getenv("MOCK_API", "false") == "true":
        return f"Log Analyze: {log_chunk[:50]}..."  # Return a mock result
    
    # Real OpenAI API interaction
    prompt_template = PromptTemplate(template="""
    Analyze the following log data and identify any patterns, anomalies, or critical errors:
    {log_chunk}
    """, input_variables=["log_chunk"])

    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    # Retry logic with exponential backoff in case of rate limits
    retries = 5
    for i in range(retries):
        try:
            result = chain.run({"log_chunk": log_chunk})
            return result
        except openai.error.RateLimitError as e:
            print(f"Rate limit exceeded. Retrying in {2**i} seconds...")
            time.sleep(2**i)  # Exponential backoff
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return "Log analysis failed due to repeated errors."

# Main function to load logs, split them, and analyze each chunk
def analyze_logs_in_folder(folder_path):
    logs = load_logs_from_folder(folder_path)

    # Text splitter to chunk logs into smaller pieces
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    all_analysis_results = []
    for log_data in logs:
        text_chunks = text_splitter.split_text(log_data)
        
        for chunk in text_chunks:
            result = analyze_log_chunk(chunk)
            all_analysis_results.append(result)
            # Add delay to prevent hitting rate limits
            time.sleep(1)  # Adjust as necessary for rate limits
    
    # Aggregate results from all logs and chunks
    final_report = "\n\n".join(all_analysis_results)
    
    # Print or save the final report
    print(final_report)
    with open("log_analysis_report.txt", "w") as report_file:
        report_file.write(final_report)

# --- Testing with Mocking ---

# Mock function to simulate OpenAI API response during testing
def mock_openai_run(data):
    return f"Mock result for chunk: {data['log_chunk'][:50]}..."  # Mock some result

# Testing function to analyze logs with mocking
@patch('langchain.chains.LLMChain.run', side_effect=mock_openai_run)
def analyze_logs_with_mock(mock_run):
    analyze_logs_in_folder(log_folder_path)

# Main execution
if __name__ == "__main__":
    # Set this to True for testing (using mock) or False for production (real API)
    testing_mode = True
    
    if testing_mode:
        os.environ["MOCK_API"] = "true"
        analyze_logs_with_mock()
    else:
        os.environ["MOCK_API"] = "false"
        analyze_logs_in_folder(log_folder_path)
