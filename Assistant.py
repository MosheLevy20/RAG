import os
import openai
from openai import OpenAI
import time

# Initialize the OpenAI client
client = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")

validFormats = ['c', 'cpp', 'csv', 'docx', 'html', 'java', 'json', 'md', 'pdf', 'php', 'pptx', 'py', 'rb', 'tex', 'txt', 'css', 'jpeg', 'jpg', 'js', 'gif', 'png', 'tar', 'ts', 'xlsx', 'xml', 'zip']
def getFiles(folder):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        if "." in dirpath:
            continue
        for filename in filenames:
            if filename[0] != "." and filename.split(".")[-1] in validFormats:
                files.append(os.path.join(dirpath, filename))
    return files

def upload_files(folder_path):
    files = getFiles(folder_path)
    file_ids = []
    for file_path in files:
        print(f"Uploading {file_path}...")
        with open(file_path, 'rb') as f:
            #check if file is empty
            if os.path.getsize(file_path) == 0:
                continue
            response = client.files.create(file=f, purpose='assistants')
            file_ids.append(response.id)
    return file_ids

def create_assistant(file_ids):
    assistant = client.beta.assistants.create(
        model="gpt-4-1106-preview",
        instructions="You are an assistant that helps users understand their documents.",
        tools=[{"type": "retrieval"}],
        file_ids=file_ids
    )
    return assistant.id

def main():
    folder_path = input("Enter the path to the folder containing files for upload: ")

    file_ids = upload_files(folder_path)
    assistant_id = create_assistant(file_ids)

    thread = client.beta.threads.create()
    thread_id = thread.id

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

      
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == 'completed':
                break
            time.sleep(1)
   
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for message in messages.data:
            if message.role == 'assistant':
                print("Assistant's response:", message.content[0].text.value)
                break

if __name__ == "__main__":
    main()