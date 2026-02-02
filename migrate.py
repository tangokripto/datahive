import json
import os

DEVICE_FILE = 'device_data.json'
BACKUP_FILE = 'device_data_backup.json'

# Updated templates for Chrome 144
OS_TEMPLATES = [
    {
        "platform": "Windows", "os_version": "Windows 19.0.0", "model_ua": "PC x86 - Chrome 144",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Windows"', "device_name": "windows pc"
    },
    {
        "platform": "Windows", "os_version": "Windows 19.0.0", "model_ua": "PC x86 - Edge 144",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
        "sec_ch_ua": '"Microsoft Edge";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Windows"', "device_name": "windows pc"
    },
    {
        "platform": "macOS", "os_version": "macOS 14.2.0", "model_ua": "Macintosh - Chrome 144",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"macOS"', "device_name": "mac"
    },
    {
        "platform": "Linux", "os_version": "Linux x86_64", "model_ua": "Linux - Chrome 144",
        "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="144", "Chromium";v="144", "Not_A Brand";v="24"',
        "sec_ch_ua_platform": '"Linux"', "device_name": "linux"
    }
]

def get_template_by_platform(platform):
    """Get Chrome 144 template based on platform"""
    platform_map = {
        "Windows": ["Windows - Chrome 131", "Windows - Edge 131"],
        "macOS": ["Macintosh - Chrome 131"],
        "Linux": ["Linux - Chrome 131"]
    }
    
    for template in OS_TEMPLATES:
        if template['platform'] == platform:
            return template
    
    return OS_TEMPLATES[0]  # Default to Windows

def migrate_devices():
    """Migrate device profiles from Chrome 131 to Chrome 144"""
    
    if not os.path.exists(DEVICE_FILE):
        print(f"❌ {DEVICE_FILE} not found!")
        return
    
    # Backup original file
    with open(DEVICE_FILE, 'r') as f:
        data = json.load(f)
    
    with open(BACKUP_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Backup created: {BACKUP_FILE}")
    print(f"📊 Total devices: {len(data)}")
    print("\n🔄 Migrating devices...\n")
    
    updated_count = 0
    
    for key, device in data.items():
        old_model = device.get('model', '')
        old_ua = device.get('ua', '')
        old_os = device.get('os_version', '')
        
        # Check if needs migration (contains "131")
        needs_update = "131" in old_model or "131" in old_ua or (
            "Windows 10.0" in old_os or "Windows 11.0" in old_os
        )
        
        if needs_update:
            # Get platform
            platform = device.get('platform', 'Windows')
            template = get_template_by_platform(platform)
            
            # Update only the browser/OS info, KEEP everything else
            device['model'] = template['model_ua']
            device['ua'] = template['ua']
            device['sec_ch_ua'] = template['sec_ch_ua']
            device['sec_ch_ua_platform'] = template['sec_ch_ua_platform']
            device['os_version'] = template['os_version']
            device['device_name'] = template['device_name']
            
            # Keep UUID, CPU info, etc unchanged!
            # device['uuid'] - UNCHANGED
            # device['cpu_model'] - UNCHANGED
            # device['cpu_cores'] - UNCHANGED
            # device['cpu_arch'] - UNCHANGED
            
            print(f"✅ {key}")
            print(f"   Old: {old_model}")
            print(f"   New: {device['model']}")
            print(f"   UUID: {device['uuid'][:20]}... (unchanged)")
            print()
            
            updated_count += 1
        else:
            print(f"⏭️  {key} - Already up to date")
    
    # Save migrated data
    with open(DEVICE_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"\n✅ Migration complete!")
    print(f"   Updated: {updated_count}/{len(data)} devices")
    print(f"   Backup: {BACKUP_FILE}")
    print(f"\n🚀 Now you can run the main script!")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 DataHive Device Profile Migration Tool")
    print("   Chrome 131 → Chrome 144")
    print("=" * 60)
    print()
    
    response = input("⚠️  This will update your device_data.json. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_devices()
    else:
        print("❌ Migration cancelled.")