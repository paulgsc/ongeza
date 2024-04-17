import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import datetime


class GoogleSheetsClient:
    instance = None  # Use a single underscore

    def __init__(self, user_email) -> None:
        if GoogleSheetsClient.instance is not None:
            raise Exception('This class is a singleton')

        GoogleSheetsClient.user_email = user_email

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls._create_service()
        return cls.instance

    @classmethod
    def release_instance(cls):
        cls.instance = None

    @classmethod
    def _create_service(cls):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        GOOGLE_API_SERVICE_NAME = 'sheets'
        GOOGLE_API_VERSION = 'v4'
        SCOPES = scopes

        cred = None

        # Specify the directory path where you want to store the pickle file
        pickle_dir = os.path.join('app', 'gsheets_pickle')

        # Create the directory if it doesn't exist
        os.makedirs(pickle_dir, exist_ok=True)

        pickle_file = os.path.join(
            pickle_dir, f'{cls.user_email}_token_{GOOGLE_API_SERVICE_NAME}_{GOOGLE_API_VERSION}.pickle')

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                cred = pickle.load(token)

        if not cred or not cred.valid:
            if cred and cred.expired and cred.refresh_token:
                cred.refresh(Request())
            else:
                CLIENT_SECRET_FILE = 'client_secret_file.json'
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server()

            with open(pickle_file, 'wb') as token:
                pickle.dump(cred, token)

        try:
            service = build(GOOGLE_API_SERVICE_NAME,
                            GOOGLE_API_VERSION, credentials=cred)
            return service
        except Exception as e:
            print('Unable to connect.')
            print(e)
            return None

    @staticmethod
    def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
        dt = datetime.datetime(year, month, day, hour,
                               minute, 0).isoformat() + 'Z'
        return dt


class ReadSheets(GoogleSheetsClient):
    def __init__(self, user_email):
        super().__init__(user_email=user_email)

    def retrieve_metadata(self, spreadsheet_id):
        service = self.get_instance()
        if service:
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
            return spreadsheet
        raise Exception('service creation failed')

    def read_data(self, spreadsheet_id, range_name):
        # format for range_name:  SAMPLE_RANGE_NAME="'Orders With Mismatch Total'!A:D"

        service = self.get_instance()
        if service:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            return values
        return None

    def validate_range(self, spreadsheet_id, range_name):
        # format for range_name:  SAMPLE_RANGE_NAME="'Orders With Mismatch Total'!A:D"

        service = self.get_instance()
        if service:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            return True
        return None


class WriteToGoogleSheet(GoogleSheetsClient):
    def __init__(self, user_email) -> None:
        super().__init__(user_email=user_email)
        self.service = self.get_instance()

    def write_data_to_sheet_df(self, worksheet_name, gsheet_id, df):

        # Replace NaN values with empty strings
        df = df.fillna('')

        # Convert date columns to string type
        date_columns = df.select_dtypes(
            include=['datetime64']).columns.tolist()
        df[date_columns] = df[date_columns].astype(str)

        # Prepare the data for insertion
        values_to_insert = df.values.tolist()

        # Construct the request body
        request_body = {
            'majorDimension': 'ROWS',
            'values': values_to_insert
        }

        # Execute the request to append data to the spreadsheet
        response = self.service.spreadsheets().values().append(
            spreadsheetId=gsheet_id,
            valueInputOption='RAW',
            range=worksheet_name,
            body=request_body
        ).execute()

        return response

    def create_new_spreadsheet(self, sheet_name='default'):
        sheet_body = {
            'properties': {
                'title': sheet_name,
                'locale': 'en_US',  # optional
                'timeZone': 'America/Los_Angeles'
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'default'
                    }
                }
            ]
        }

        sheets_file2 = self.service.spreadsheets().create(body=sheet_body).execute()
        return {'url': sheets_file2['spreadsheetUrl'], 'gsheet_id': sheets_file2['spreadsheetId'], 'sheet_names': sheets_file2['sheets']}

# Example usage:
# write_data_to_sheet_df('Sheet1', 'your_gsheet_id', your_dataframe, your_service_instance)
