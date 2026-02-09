"""
Automatically upload Shopify CSV files to Google Drive
This enables Matrixify to import from a public URL
"""
import os
import glob
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging


class GoogleDriveUploader:
    """Upload files to Google Drive for Shopify automation."""
    
    def __init__(self, credentials_file: str = 'credentials/credentials.json'):
        """
        Initialize with Google service account credentials.
        
        Args:
            credentials_file: Path to service account JSON file
        """
        self.credentials_file = credentials_file
        self.logger = logging.getLogger('drive_uploader')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Initialize Drive API
        self.service = self._init_drive_service()
    
    def _init_drive_service(self):
        """Initialize Google Drive API service."""
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            service = build('drive', 'v3', credentials=creds)
            self.logger.info("✓ Connected to Google Drive")
            return service
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Drive API: {e}")
            return None
    
    def create_folder(self, folder_name: str, parent_id: str = None) -> str:
        """
        Create a folder in Google Drive.
        
        Returns:
            Folder ID
        """
        if not self.service:
            return None
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            
            # Make folder publicly accessible
            self.make_public(folder_id)
            
            self.logger.info(f"✓ Created folder: {folder_name}")
            self.logger.info(f"  Link: {folder.get('webViewLink')}")
            
            return folder_id
            
        except Exception as e:
            self.logger.error(f"Error creating folder: {e}")
            return None
    
    def upload_file(self, file_path: str, folder_id: str = None) -> dict:
        """
        Upload a file to Google Drive.
        
        Returns:
            Dict with file ID and download URL
        """
        if not self.service:
            return None
        
        try:
            file_name = os.path.basename(file_path)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            file_id = file.get('id')
            
            # Make file publicly accessible
            self.make_public(file_id)
            
            # Get direct download link
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            self.logger.info(f"✓ Uploaded: {file_name}")
            self.logger.info(f"  Download URL: {download_url}")
            
            return {
                'id': file_id,
                'name': file_name,
                'view_url': file.get('webViewLink'),
                'download_url': download_url
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading {file_path}: {e}")
            return None
    
    def make_public(self, file_id: str):
        """Make a file/folder publicly accessible."""
        try:
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except Exception as e:
            self.logger.warning(f"Could not make file public: {e}")
    
    def update_file(self, file_id: str, new_file_path: str) -> bool:
        """Update an existing file with new content."""
        try:
            media = MediaFileUpload(new_file_path, resumable=True)
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            self.logger.info(f"✓ Updated file: {os.path.basename(new_file_path)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating file: {e}")
            return False
    
    def find_file_by_name(self, file_name: str, folder_id: str = None) -> str:
        """Find a file by name. Returns file ID if found."""
        try:
            query = f"name='{file_name}' and trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            if files:
                return files[0]['id']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding file: {e}")
            return None
    
    def upload_shopify_csvs(self, csv_dir: str = 'shopify_imports', folder_name: str = 'Shopify_Imports') -> dict:
        """
        Upload all Shopify CSV files to Drive.
        Creates/updates files as needed.
        
        Returns:
            Dict mapping file names to download URLs
        """
        if not self.service:
            self.logger.error("Drive service not initialized")
            return {}
        
        # Find or create folder
        folder_id = self.find_file_by_name(folder_name)
        if not folder_id:
            folder_id = self.create_folder(folder_name)
        
        if not folder_id:
            self.logger.error("Could not create/find folder")
            return {}
        
        # Find all CSV files
        csv_files = glob.glob(f'{csv_dir}/*_shopify.csv')
        
        if not csv_files:
            self.logger.warning(f"No CSV files found in {csv_dir}/")
            return {}
        
        self.logger.info(f"\nUploading {len(csv_files)} files to Google Drive...")
        
        urls = {}
        
        for csv_file in csv_files:
            file_name = os.path.basename(csv_file)
            
            # Check if file already exists
            existing_id = self.find_file_by_name(file_name, folder_id)
            
            if existing_id:
                # Update existing file
                self.logger.info(f"Updating: {file_name}")
                if self.update_file(existing_id, csv_file):
                    download_url = f"https://drive.google.com/uc?export=download&id={existing_id}"
                    urls[file_name] = download_url
            else:
                # Upload new file
                result = self.upload_file(csv_file, folder_id)
                if result:
                    urls[file_name] = result['download_url']
        
        self.logger.info(f"\n✓ Upload complete! {len(urls)} files uploaded")
        
        # Save URLs to file for Matrixify configuration
        self._save_urls(urls)
        
        return urls
    
    def _save_urls(self, urls: dict):
        """Save download URLs to a file for reference."""
        with open('shopify_imports/drive_urls.txt', 'w') as f:
            f.write("Google Drive Download URLs for Matrixify\n")
            f.write("=" * 60 + "\n\n")
            
            for file_name, url in urls.items():
                scraper_name = file_name.replace('_shopify.csv', '')
                f.write(f"{scraper_name}:\n")
                f.write(f"  {url}\n\n")
        
        self.logger.info("✓ URLs saved to: shopify_imports/drive_urls.txt")


def main():
    """Main execution."""
    uploader = GoogleDriveUploader()
    
    if not uploader.service:
        print("\n❌ Could not connect to Google Drive")
        print("\nMake sure you have:")
        print("1. Service account credentials in credentials/credentials.json")
        print("2. Google Drive API enabled")
        print("\nSee: https://developers.google.com/drive/api/v3/quickstart/python")
        return
    
    # Upload all Shopify CSVs
    urls = uploader.upload_shopify_csvs()
    
    if urls:
        print("\n" + "=" * 60)
        print("✓ Files uploaded successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Open shopify_imports/drive_urls.txt")
        print("2. Copy the download URLs")
        print("3. Configure Matrixify to import from these URLs")
        print("4. Set schedule: Weekly on Sunday at 2 AM")
        print("\nDone! Your Shopify store will auto-update weekly.")


if __name__ == "__main__":
    main()
