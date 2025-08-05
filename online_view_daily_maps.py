import streamlit as st
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import tempfile
import os

def main():
    load_dotenv(override=True)  # Load environment variables from .env file

    # C:\Users\zli0003\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\streamlit.exe run C:/Users/zli0003/PycharmProjects/ID4/id4-data-processing/daily_map/online_view_daily_maps.py
    # pipreqs . --encoding=utf8 --force

    # Azure Blob configuration
    connection_string = os.environ.get("connection_string")
    container_name = os.environ.get("container_name")
    folder_name =  os.environ.get("folder_name")

    # initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # get list of blobs in the specified folder
    # Note: This function filters for HTML files only
    def get_blob_list(folder_name):
        blob_list = []
        for blob in container_client.list_blobs(name_starts_with = folder_name):
            if blob.name.endswith('.html'):
                blob_list.append(blob.name)
        return blob_list

    # download blob to a temporary file
    def download_blob_to_temp(blob_name):
        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        
        # create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, os.path.basename(blob_name))
        
        # make sure the directory exists
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, "wb") as file:
            file.write(download_stream.readall())
        
        return temp_path

    # Streamlit app setup
    st.set_page_config(layout="wide")
    st.title("Daily Report Map Preview")

    # get the list of blobs in the specified folder
    blob_list = get_blob_list(folder_name)
    selected_file = st.selectbox("Select a file to preview", blob_list)

    if 'downloaded_files' not in st.session_state:
        st.session_state['downloaded_files'] = {}

    if selected_file:
        st.write(f"Selected file: {selected_file}")
        
        # add a button to preview the selected file
        if st.button("Preview"):
            with st.spinner("Loading..."):
                try:
                    # Check if file already downloaded
                    if selected_file in st.session_state['downloaded_files']:
                        temp_file_path = st.session_state['downloaded_files'][selected_file]
                    else:
                        # Download the file to a temporary location
                        temp_file_path = download_blob_to_temp(selected_file)
                        st.session_state['downloaded_files'][selected_file] = temp_file_path

                    st.success("File Downloaded.")
                    # read the HTML content and display it
                    with open(temp_file_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    # You can adjust the height and width parameters to change the preview size
                    st.components.v1.html(html_content, height=900, width=2000, scrolling=True)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
