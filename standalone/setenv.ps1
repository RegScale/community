add-type -AssemblyName System.Web

$TEXT_ENCRYPT = @"

The encryption key is used to encrypt all files stored within Atlasity and sensitive data in the database.
It must be a 256-bit key.
Please enter your key now (or press Enter to use the randomly generated key shown)
"@

$TEXT_JWT = @"

The JSON Web Token (JWT) is as an API authentication mechanism within Atlasity and when interactingwith the API directly.
It must be a 256-bit key.
Please enter your key now (or press Enter to use the randomly generated key shown)
"@


$defaultSiteName = "atlasity"
$defaultStoredFilesPath = "c:\atlasity\files"
$defaultFileSizeLimit = "104857600"
$defaultJWTToken = [System.Web.Security.Membership]::GeneratePassword(32, 2)
$defaultEncryptionKey = [System.Web.Security.Membership]::GeneratePassword(32, 2)

$date = (Get-Date).AddDays(30)
$date = $date.ToString("MM/dd/yyyy")

$siteName = Read-Host "Enter IIS Site Name [$defaultSiteName]"
if ($siteName -eq "") {
    $siteName = $defaultSiteName
}

$storedFilesPath = Read-Host "Enter Atlas Files Location [$defaultStoredFilesPath]"
if ($storedFilesPath -eq "") {
    $storedFilesPath = $defaultStoredFilesPath
}

Write-Host $TEXT_JWT
$jwtToken = ""
while ($jwtToken.length -ne 32) {
    $jwtToken = Read-Host "Enter JWT Token (256-bit) [$defaultJWTToken]"
    if ($jwtToken -eq "") {
        $jwtToken = $defaultJWTToken
    }
    elseif ($jwtToken.length -ne 32) {
        Write-Host "ERROR! Please enter a 256-bit (32 byte) key"
    }
}

Write-Host $TEXT_ENCRYPT
$encryptionKey = ""
while ($encryptionKey.length -ne 32) {
$encryptionKey = Read-Host "Enter Encryption (256-bit) [$defaultEncryptionKey]"
    if ($encryptionKey -eq "") {
        $encryptionKey = $defaultEncryptionKey
    }
    elseif ($encryptionKey.length -ne 32) {
        Write-Host "ERROR! Please enter a 256-bit (32 byte) key"
    }
}

$sqlConnection = Read-Host "Paste in your SQL Connection String []"

Write-Host "Site: $siteName"
Write-Host "Date: $date"
Write-Host "Files Path: $storedFilesPath"
Write-Host "JWT Token: $jwtToken"
Write-Host "Encryption Key: $encryptionKey"
Write-Host "SQL Connection: $sqlConnection"


$envVariables = (
     @{name='StoredFilesPath';value=$storedFilesPath},
     @{name='FileSizeLimit';value=$defaultFileSizeLimit},
     @{name='JWTSecretKey';value=$jwtToken}, 
     @{name='EncryptionKey';value=$encryptionKey}, 
     @{name='LicenseKey';value="Community;$date;5000"}, 
     @{name='SQLConn';value=$sqlConnection}  
)


Set-WebConfigurationProperty -PSPath "IIS:\sites\$siteName" -filter "system.webServer/aspNetCore/environmentVariables" -name "." -value $envVariables 