import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
from google.auth.transport.requests import Request

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class YouTube:
    def __init__(self):
        # Path to store the token
        self.token_path = "youtube_upload_token.pickle"

        # OAuth 2.0 credentials setup
        client_secrets = {
            "installed": {
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "auth_uri": os.getenv("AUTH_URI"),
                "token_uri": os.getenv("TOKEN_URI"),
                "redirect_uris": ["http://localhost"],
            }
        }

        credentials = self._get_credentials(client_secrets)

        # Build YouTube API client
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials
        )

    def _get_credentials(self, client_secrets):
        credentials = None

        # Check if token exists
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                credentials = pickle.load(token)

        # Refresh or re-authenticate if needed
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                # Create OAuth 2.0 flow
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                    client_secrets,
                    scopes=["https://www.googleapis.com/auth/youtube.upload"],
                )

                # Run local server to authorize
                credentials = flow.run_local_server(port=0)

            # Save the credentials for next run
            with open(self.token_path, "wb") as token:
                pickle.dump(credentials, token)

        return credentials

    def upload_video(
        self,
        file_path,
        title,
        description,
        category_id="24",
        privacy_status="public",
        made_for_kids=False,
        tags=[],
    ):
        """
        Upload a video to YouTube

        :param file_path: Path to the video file
        :param title: Video title
        :param description: Video description
        :param category_id: YouTube video category ID (default: 24 - Entertainment)
        # https://developers.google.com/youtube/v3/docs/videoCategories/list
        :param privacy_status: Video privacy status (private, public, or unlisted)
        :return: Uploaded video details
        """
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id,
                "tags": tags,
            },
            "status": {
                "privacyStatus": privacy_status,
                "madeForKids": made_for_kids,
                "selfDeclaredMadeForKids": made_for_kids,
            },
        }

        # Create a MediaFileUpload object
        media = googleapiclient.http.MediaFileUpload(
            file_path, resumable=True, chunksize=1024 * 1024 * 5  # 5MB chunks
        )

        # Call the API's videos.insert method to create and upload the video
        request = self.youtube.videos().insert(
            part=",".join(body.keys()), body=body, media_body=media
        )

        # Execute and get response
        response = request.execute()
        return response
