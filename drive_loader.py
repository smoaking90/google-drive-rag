from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


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


if __name__ == "__main__":
    folder_id = "1_YvVjpP0KFIJuR8bDFSQaAGL1BscYDmR"

    drive_service = get_drive_service()
    files = list_folder_files(drive_service, folder_id)

    print(f"Found {len(files)} files:")

    for file in files:
        print(
            f"{file['name']} | "
            f"{file['mimeType']} | "
            f"{file['id']}"
        )