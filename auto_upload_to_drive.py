"""
Automatically upload Shopify CSVs to Google Drive.
Creates public URLs that Matrixify can use to auto-import.
NO SHOPIFY CREDENTIALS NEEDED.
"""
import os
import glob
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_csvs_to_drive():
    """Upload all Shopify CSV files to Google Drive and get public URLs."""
    
    print("=" * 70)
    print("UPLOADING TO GOOGLE DRIVE")
    print("=" * 70)
    
    # Initialize Drive API
    print("\nConnecting to Google Drive...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            'credentials/credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=creds)
        print("✓ Connected to Google Drive")
    except Exception as e:
        print(f"❌ Error connecting to Drive: {e}")
        print("\nMake sure credentials/credentials.json exists")
        return None
    
    # Create/find Shopify folder
    print("\nSetting up folder...")
    folder_name = "Shopify_Auto_Import"
    
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        folder_id = folders[0]['id']
        print(f"✓ Using existing folder: {folder_name}")
    else:
        # Create folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        # Make folder public
        service.permissions().create(
            fileId=folder_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        print(f"✓ Created folder: {folder_name}")
    
    # Get CSV files
    csv_files = glob.glob('shopify_imports/*_shopify.csv')
    csv_files = [f for f in csv_files if os.path.getsize(f) > 100]
    
    if not csv_files:
        print("\n❌ No CSV files found in shopify_imports/")
        return None
    
    print(f"\nUploading {len(csv_files)} files...")
    
    urls = {}
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        print(f"\n  Uploading {filename}...")
        
        try:
            # Check if file exists
            query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
            results = service.files().list(q=query, fields='files(id)').execute()
            existing = results.get('files', [])
            
            if existing:
                # Update existing file
                file_id = existing[0]['id']
                media = MediaFileUpload(csv_file, resumable=True)
                service.files().update(fileId=file_id, media_body=media).execute()
                print(f"    ✓ Updated existing file")
            else:
                # Upload new file
                file_metadata = {
                    'name': filename,
                    'parents': [folder_id]
                }
                media = MediaFileUpload(csv_file, resumable=True)
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                file_id = file.get('id')
                
                # Make file public
                service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'}
                ).execute()
                
                print(f"    ✓ Uploaded new file")
            
            # Get download URL
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            urls[filename] = download_url
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    # Save URLs to file
    print("\n" + "=" * 70)
    print("UPLOAD COMPLETE")
    print("=" * 70)
    
    urls_file = "shopify_imports/MATRIXIFY_URLS.txt"
    with open(urls_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("MATRIXIFY IMPORT URLS\n")
        f.write("=" * 70 + "\n\n")
        f.write("Give these URLs to your client to configure in Matrixify app.\n")
        f.write("Matrixify will auto-import from these URLs weekly.\n\n")
        f.write("=" * 70 + "\n\n")
        
        for filename, url in urls.items():
            scraper_name = filename.replace('_shopify.csv', '')
            f.write(f"{scraper_name}:\n")
            f.write(f"  {url}\n\n")
    
    print(f"\n✓ Uploaded {len(urls)} files to Google Drive")
    print(f"✓ URLs saved to: {urls_file}")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS FOR YOUR CLIENT")
    print("=" * 70)
    print("\n1. Install Matrixify app from Shopify App Store")
    print("   https://apps.shopify.com/excel-export-import")
    print("   Cost: $30/month (7-day free trial)")
    print("\n2. In Matrixify, go to: Import → Schedule")
    print("\n3. For each scraper, create a scheduled import:")
    print("   - Import type: Products")
    print("   - Source: From URL")
    print("   - URL: Copy from MATRIXIFY_URLS.txt")
    print("   - Schedule: Weekly, Sunday at 5:00 AM")
    print("\n4. Done! Products will auto-import weekly")
    print("\n" + "=" * 70)
    
    return urls


if __name__ == "__main__":
    upload_csvs_to_drive()
