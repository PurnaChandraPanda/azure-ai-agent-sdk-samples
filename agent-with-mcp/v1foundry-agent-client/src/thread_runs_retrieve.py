import time
import json
import os
import concurrent.futures

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageTextContent, ListSortOrder
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.environ["AZURE_EXISTING_AIPROJECT_ENDPOINT"]

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def thread_details():
    # Create the AI Project Client
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )

    # # Retrieve the agent definition based on the `agent_id`
    # agent = project_client.agents.get_agent(
    #                     agent_id=os.environ["AZURE_AI_AGENT_AGENT_ID"]  # Ensure this environment variable is set            
    #                     )
    # print(f"Retrieved agent, agent ID: {agent.id}")

    thread_id = "thread_LshNvWGKlsrqxCEb3QESIcSq"
    run_id = "run_xIAJ7ZXPM9CsIJAU5sYlBHem"

    # Retrieve the thread runs for the specific thread id
    run = project_client.agents.runs.get(thread_id=thread_id, run_id=run_id)
    # print(thread_id, run_id, run.status, run.usage)

def main():
    # Loop to retrieve thread runs for 1000 times, and show time taken for each retrieval
    for i in range(1):
        start_time = time.time()
        thread_details()
        end_time = time.time()
        print(f"Time taken for retrieval {i+1}: {end_time - start_time} seconds")

def parallel_main():
    MAX_WORKERS = 4
    # Loop to retrieve thread runs for 1000 times in parallel, and show time taken for each retrieval
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(thread_details) for _ in range(1000)]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            start_time = time.time()
            future.result()
            end_time = time.time()
            print(f"Time taken for retrieval {i+1}: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
    # parallel_main()