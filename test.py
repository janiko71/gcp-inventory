from google.oauth2 import service_account
import googleapiclient.discovery

f_cred = "C:\\Users\\jean\\OneDrive\\Dev\\gcp-inventory\\cred\\secu-si-175c9ca0ad9e.json"
credentials = service_account.Credentials.from_service_account_file(f_cred)

#gac = googleapiclient.discovery.build('sqladmin', 'v1beta4', credentials=credentials)
#svc = googleapiclient.discovery.build('accesscontextmanager', 'v1', credentials=credentials)
svc = googleapiclient.discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
