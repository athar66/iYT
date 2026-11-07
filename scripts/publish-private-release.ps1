param([switch]$UpdateCatalog)
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
    if (-not $repo.private) { throw 'This publisher supports private repositories only' }
    $existing = @(Invoke-RestMethod -Headers $headers "https://api.github.com/repos/$repoName/releases")
    $catalogRelease = @($existing | Where-Object tag_name -eq 'catalog')
    if ($catalogRelease.Count -and -not $UpdateCatalog) { throw 'Use -UpdateCatalog to update the existing release while preserving its previous assets' }
    $body = @{
        tag_name='catalog';target_commitish='main';name='iYT 0.4.1';draft=$true;prerelease=$false
        body="iYT 0.4.1 fixes the sign-in DNS callback error (Invalid IP address: undefined), restores the platform Node8 bridge for BMW native-addon compatibility, removes the jap-node22 dependency, bundles target-ABI-checked QuickJS for on-demand extraction and disables the idle Python extraction worker. The bridge still uses iDrive's existing Node runtime; this is not a completely Node-free service. DNS regression, platform bridge/account tests, TV-page uplink requests and live QuickJS extraction metadata checks passed. Update both iYT and iYT playback service through MGU Store. Real-vehicle sign-in and playback require verification; real cluster video remains disabled. Previous package assets are retained for rollback. Source and licences are in the repository."
    } | ConvertTo-Json
    $release = if ($catalogRelease.Count) { $catalogRelease[0] } else { Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Body $body "https://api.github.com/repos/$repoName/releases" }
    $uploadBase = ($release.upload_url -split '\{')[0]
    $assets = @{}
    foreach ($name in @('iyt_app@0.4.1.tgz','iyt-daemon@0.4.1.tgz','iyt_app.png','mgu-store.json')) {
        $file = Join-Path $releaseDir $name
        $present = @($release.assets | Where-Object name -eq $name)
        if ($present.Count) {
            $digest = 'sha256:'+(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($present[0].digest -ne $digest) { throw "Existing release asset $name has different bytes; refusing to overwrite it" }
            $assets[$name] = $present[0]
            continue
        }
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
        $prior = @($release.assets | Where-Object name -eq $name)
        if ($prior.Count) {
            $archiveName = if ($name -eq 'catalog.json') { 'catalog-archive-'+$prior[0].id+'.json' } else { 'SHA256SUMS-'+$prior[0].id }
            $renameBody = @{name=$archiveName} | ConvertTo-Json
            $null = Invoke-RestMethod -Method Patch -Headers $headers -ContentType 'application/json' -Body $renameBody $prior[0].url
        }
        try {
        $assets[$name] = Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/octet-stream' -InFile (Join-Path $releaseDir $name) ($uploadBase+'?name='+[uri]::EscapeDataString($name))
        } catch {
            if ($prior.Count) {
                $restoreBody = @{name=$name} | ConvertTo-Json
                $null = Invoke-RestMethod -Method Patch -Headers $headers -ContentType 'application/json' -Body $restoreBody $prior[0].url
            }
            throw
        }
    }
    $published = Invoke-RestMethod -Method Patch -Headers $headers -ContentType 'application/json' -Body (($body | ConvertFrom-Json | Select-Object name,body,@{n='draft';e={$false}}) | ConvertTo-Json) $release.url
    $record = @{
        repository=$repoName;private=$true;tag=$published.tag_name;releaseUrl=$published.html_url
        assets=@($published.assets | Select-Object name,size,url);vehicleDeployed=$false
    } | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText((Join-Path $project 'reports/published-release.json'), ($record+"`n"), [Text.UTF8Encoding]::new($false))
    Write-Output "Published private catalog release: $($published.html_url)"
} finally {
    Remove-Variable credentialText,fields,headers -ErrorAction SilentlyContinue
}
