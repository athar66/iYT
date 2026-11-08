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
    $catalogRelease = $null
    try { $catalogRelease = Invoke-RestMethod -Headers $headers "https://api.github.com/repos/$repoName/releases/tags/catalog" }
    catch { if ([int]$_.Exception.Response.StatusCode -ne 404) { throw } }
    if ($catalogRelease -and -not $UpdateCatalog) { throw 'Use -UpdateCatalog to update the existing release while preserving its previous assets' }
    $body = @{
        tag_name='catalog';target_commitish='main';name='iYT 0.4.2';draft=$true;prerelease=$false
        body="iYT 0.4.2 publishes completed audio through a dedicated, randomly named handoff readable by BMW MediaPlayer without exposing the private download cache. Hard links avoid media copies, with bounded ownership manifests and cleanup. A cross-account Linux test reproduces the original file-access denial and verifies the handoff. Diagnostics show selected formats and distinguish BMW MediaPlayer rejection from native decoder failure. This fixes a confirmed permission gap; the reported vehicle failure still requires verification. H.264 hardware decoding is unchanged; no software multi-format decoder was added. Update iYT and its playback service. Node22 remains unnecessary. Previous packages remain available for rollback."
    } | ConvertTo-Json
    $release = if ($catalogRelease) { $catalogRelease } else { Invoke-RestMethod -Method Post -Headers $headers -ContentType 'application/json' -Body $body "https://api.github.com/repos/$repoName/releases" }
    $uploadBase = ($release.upload_url -split '\{')[0]
    $assets = @{}
    foreach ($name in @('iyt_app@0.4.2.tgz','iyt-daemon@0.4.2.tgz','iyt_app.png','mgu-store.json')) {
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
    # Match artifact URLs to the repository's current visibility; never change it.
    $catalogPath = Join-Path $releaseDir 'catalog.json'
    $catalog = Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json
    foreach ($component in $catalog.components) { $component.artifact.url = if ($repo.private) { $assets[$component.artifact.name].url } else { $assets[$component.artifact.name].browser_download_url } }
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
        repository=$repoName;private=$repo.private;tag=$published.tag_name;releaseUrl=$published.html_url
        assets=@($published.assets | Select-Object name,size,url);vehicleDeployed=$false
    } | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText((Join-Path $project 'reports/published-release.json'), ($record+"`n"), [Text.UTF8Encoding]::new($false))
    Write-Output "Published catalog release: $($published.html_url)"
} finally {
    Remove-Variable credentialText,fields,headers -ErrorAction SilentlyContinue
}
