
import streamlit as st
import openai
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Title
st.title("📚 AnalystDocBot")
st.write("Ask me anything about your clients, docs, or processes.")

# Set up OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Authenticate with Google Drive
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# Helper: Get or create a folder
def get_or_create_folder(folder_name, parent_id=None):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]["id"]
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]
    folder = drive_service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")

# Helper: Get or create a file
def get_or_create_file(file_name, folder_id):
    query = f"name = '{file_name}' and '{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    file_metadata = {
        "name": file_name,
        "parents": [folder_id],
        "mimeType": "application/vnd.google-apps.document"
    }
    file = drive_service.files().create(body=file_metadata, fields="id").execute()
    return file.get("id")

# Chatbot memory
if "history" not in st.session_state:
    st.session_state.history = []

# Input box
user_input = st.text_input("What would you like to do? (e.g., Add note to Client ABC)")

if user_input:
    messages = [{"role": "system", "content": "You are a helpful assistant for maintaining structured documentation in Google Drive."}]
    for msg in st.session_state.history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    # Run GPT
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    answer = response.choices[0].message.content
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": answer})
    st.markdown("**Bot:** " + answer)

    # Example trigger: Add note to client
    if "add note to client" in user_input.lower():
        try:
            parts = user_input.split(" to client ")
            note = parts[0].replace("Add note ", "").strip()
            client_name = parts[1].strip()

            folder_id = get_or_create_folder("Clients")
            client_folder_id = get_or_create_folder(client_name, parent_id=folder_id)
            notes_file_id = get_or_create_file("notes", client_folder_id)

            # Append note to the file (Google Docs append workaround)
            st.success(f"✅ Note added for {client_name} in Drive (simulated).")
        except Exception as e:
            st.error(f"⚠️ Failed to update: {str(e)}")
