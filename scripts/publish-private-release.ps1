$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$releaseDir = Join-Path $project 'dist/release'
$repoName = 'athar66/iYT'
# Obtain GitHub's existing Git credential in memory only. Never log or persist it.
$credentialText = @('protocol=https','host=github.com','path=athar66/iYT.git','') | git -c credential.interactive=never credential fill
if ($LASTEXITCODE -ne 0) { throw 'GitHub authentication is unavailable' }
$fields = @{}
foreach ($line in $credentialText) {
    $parts = $line -split '=',2
    if ($parts.Count -eq 2) { $fields[$parts[0]] = $parts[1] }
}
$headers = @{Authorization=('Bearer '+$fields['password']);Accept='application/vnd.github+json';'X-GitHub-Api-Version'='2022-11-28'}
try {
    $repo = Invoke-RestMethod -Headers $headers "https://api.github.com/repos/$repoName"
    if (-not $repo.private) { throw 'This publisher is restricted to the private repository requested by the owner' }
    $existing = @(Invoke-RestMethod -Headers $headers "https://api.github.com/repos/$repoName/releases")
    if (@($existing | Where-Object tag_name -eq 'catalog').Count) { throw 'A catalog release already exists; inspect it before updating' }
    $body = @{
        tag_name='catalog';target_commitish='main';name='iYT 0.4.0';draft=$true;prerelease=$false
        body="iYT for BMW MGU iDrive 7. SDK-free native app and target-ABI-checked playback service. MGU Store supplies the BMW SDK from a stock donor on the head unit. Add athar66/iYT with GitHub access and select Releases. Requires the JustAnotherPU/mgu-apps source for jap-node22 if unavailable. Host/native UI tests, Store discovery/packing/linking and live public-video metadata extraction passed. Actual car installation and sustained playback remain untested. Real cluster video is disabled. Full corresponding source and licences are in this repository."
    } | ConvertTo-Json
    $release = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Body $body "https://api.github.com/repos/$repoName/releases"
    $uploadBase = ($release.upload_url -split '\{')[0]
    $assets = @{}
    foreach ($name in @('iyt_app@0.4.0.tgz','iyt-daemon@0.4.0.tgz','iyt_app.png','mgu-store.json')) {
        $file = Join-Path $releaseDir $name
        $asset = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/octet-stream' -InFile $file ($uploadBase+'?name='+[uri]::EscapeDataString($name))
        $assets[$name] = $asset
    }
    # Private catalog artifacts must use the authenticated asset API URL.
    $catalogPath = Join-Path $releaseDir 'catalog.json'
    $catalog = Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json
    foreach ($component in $catalog.components) { $component.artifact.url = $assets[$component.artifact.name].url }
    [IO.File]::WriteAllText($catalogPath, (($catalog | ConvertTo-Json -Depth 16)+"`n"), [Text.UTF8Encoding]::new($false))
    $hashLines = foreach ($file in Get-ChildItem -LiteralPath $releaseDir -File | Where-Object Name -ne 'SHA256SUMS' | Sort-Object Name) {
        (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()+'  '+$file.Name
    }
    [IO.File]::WriteAllText((Join-Path $releaseDir 'SHA256SUMS'), (($hashLines -join "`n")+"`n"), [Text.UTF8Encoding]::new($false))
    foreach ($name in @('catalog.json','SHA256SUMS')) {
        $assets[$name] = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/octet-stream' -InFile (Join-Path $releaseDir $name) ($uploadBase+'?name='+[uri]::EscapeDataString($name))
    }
    $published = Invoke-RestMethod -Method Patch -Headers $headers -ContentType 'application/json' -Body '{"draft":false}' $release.url
    $record = @{
        repository=$repoName;private=$true;tag=$published.tag_name;releaseUrl=$published.html_url
        assets=@($published.assets | Select-Object name,size,url);vehicleDeployed=$false
    } | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText((Join-Path $project 'reports/published-release.json'), ($record+"`n"), [Text.UTF8Encoding]::new($false))
    Write-Output "Published private catalog release: $($published.html_url)"
} finally {
    Remove-Variable credentialText,fields,headers -ErrorAction SilentlyContinue
}
