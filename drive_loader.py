from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from googleapiclient.errors import HttpError
from pprint import pprint



BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

GOOGLE_DOC_TYPE = "application/vnd.google-apps.document"
PDF_TYPE = "application/pdf"


def get_drive_service():
    credentials = None

    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_PATH),
            SCOPES,
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return build("drive", "v3", credentials=credentials)


def list_folder_files(service, folder_id):
    response = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and trashed = false",
            spaces="drive",
            pageSize=100,
            orderBy="name_natural",
            fields=(
                "files("
                "id, name, mimeType, modifiedTime, webViewLink"
                ")"
            ),
        )
        .execute()
    )

    return response.get("files", [])



def export_google_doc(service, file_id):
    request = service.files().export_media(
        fileId=file_id,
        mimeType="text/plain",
    )

    content = execute_download(request)

    return content.decode("utf-8")


def execute_download(request):
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False

    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%")

    return buffer.getvalue()


def download_pdf(service, file_id):
    request = service.files().get_media(fileId=file_id)

    return execute_download(request)


def export_google_doc(service, file_id):
    request = service.files().export_media(
        fileId=file_id,
        mimeType="text/plain",
    )

    content = execute_download(request)

    return content.decode("utf-8")



def retrieve_file_content(service, file):
    if file["mimeType"] == GOOGLE_DOC_TYPE:
        return export_google_doc(
            service=service,
            file_id=file["id"],
        )

    if file["mimeType"] == PDF_TYPE:
        return download_pdf(
            service=service,
            file_id=file["id"],
        )

    print(f"Unsupported file type: {file['name']}")
    return None


def save_file_content(file, content):
    if file["mimeType"] == GOOGLE_DOC_TYPE:
        output_path = DATA_DIR / f"{file['name']}.txt"
        output_path.write_text(content, encoding="utf-8")

    elif file["mimeType"] == PDF_TYPE:
        output_path = DATA_DIR / file["name"]
        output_path.write_bytes(content)

    else:
        return None

    print(f"Saved: {output_path}")

    return output_path


if __name__ == "__main__":
    folder_id = "1_YvVjpP0KFIJuR8bDFSQaAGL1BscYDmR"

    drive_service = get_drive_service()
    files = list_folder_files(drive_service, folder_id)
    
    for file in files:
        content = retrieve_file_content(drive_service, file)
        
        if content is not None:
            save_file_content(file, content)