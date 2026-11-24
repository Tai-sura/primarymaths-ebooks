# Build a clean, publishable copy of the reader for one or more books.
#   .\tools\build_deploy.ps1 -Books phy11,phy06-force2
#   .\tools\build_deploy.ps1 -Books phy11 -Dst C:\some\other\clone
# The output keeps .git so the published history survives a rebuild. Source PDFs and the teacher's
# reference crops are never copied; only what the reader needs at runtime.
param(
  [string[]]$Books = @("phy11"),
  [string]$Src = "C:\Users\surat\.dsh\bot\workspace\ebook-engine",
  [string]$Dst = "C:\Users\surat\.dsh\bot\workspace\deploy-phy11",
  # site branding for a deploy clone; empty keeps the physics wording baked into index.html
  [string]$SiteName = "",
  [string]$SiteShort = "",
  # physics explainer pages: skip them for a non-physics site
  [switch]$SkipExplainers
)
$ErrorActionPreference = "Stop"

# the CACHE version the deploy clone is carrying right now, so the build can report the change
$cacheOld = $null
$swDst = Join-Path $Dst "sw.js"
if (Test-Path $swDst) {
  $m = Select-String -Path $swDst -Pattern 'const CACHE = "([^"]+)"'
  if ($m) { $cacheOld = $m.Matches[0].Groups[1].Value }
}

if (Test-Path $Dst) {
  Get-ChildItem $Dst -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force
} else {
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
}

# root files the web app needs
# NOTE: `ebook-engine/sw.js` is the ONE place the CACHE version is set — this script copies it over
# the deploy clone verbatim, so never edit `sw.js` in the deploy clone (a build would overwrite it).
# Bump `const CACHE` in ebook-engine/sw.js before a build that changes anything iPads cache, and keep
# the file UTF-8 without a BOM.
foreach ($f in @("index.html", "reader.html", "manifest.webmanifest", "sw.js", ".nojekyll")) {
  Copy-Item (Join-Path $Src $f) (Join-Path $Dst $f)
}
# optional per-site branding: only the deploy copy is rewritten, the engine stays generic
if ($SiteName) {
  foreach ($f in @("index.html", "manifest.webmanifest")) {
    $fp = Join-Path $Dst $f
    $t = [IO.File]::ReadAllText($fp)
    $t = $t.Replace("Physics Solution Ebooks", $SiteName)
    if ($SiteShort) { $t = $t.Replace("Physics Ebooks", $SiteShort) }
    [IO.File]::WriteAllText($fp, $t, [Text.UTF8Encoding]::new($false))
  }
}

# engine, vendor libs, icons
foreach ($d in @("engine", "vendor", "assets")) {
  Copy-Item (Join-Path $Src $d) (Join-Path $Dst $d) -Recurse
}

# every requested book, without source PDFs or teacher reference crops
foreach ($id in $Books) {
  $from = Join-Path $Src "books\$id"
  if (-not (Test-Path $from)) { throw "no such book: $id" }
  $bd = Join-Path $Dst "books\$id"
  New-Item -ItemType Directory -Force -Path $bd | Out-Null
  foreach ($f in @("book.json", "layout.json", "solutions.js", "widgets.js")) {
    $p = Join-Path $from $f
    if (Test-Path $p) { Copy-Item $p (Join-Path $bd $f) }
  }
  foreach ($d in @("pages", "media", "answers")) {
    $p = Join-Path $from $d
    if (Test-Path $p) { Copy-Item $p (Join-Path $bd $d) -Recurse }
  }
}

# interactive explainers: standalone pages published under /explainers/
# Only topics listed here go out — add one after Chief has verified it.
$ExplSrc = "C:\Users\surat\.dsh\bot\workspace\explainers"
$ExplTopics = @("moment-balance", "equilibrium-beam", "couple", "centroid-hang")
if ((Test-Path $ExplSrc) -and (-not $SkipExplainers)) {
  $dstExpl = Join-Path $Dst "explainers"
  New-Item -ItemType Directory -Force -Path $dstExpl | Out-Null
  if (Test-Path (Join-Path $ExplSrc "index.html")) { Copy-Item (Join-Path $ExplSrc "index.html") $dstExpl }
  if (Test-Path (Join-Path $ExplSrc "p5.min.js")) { Copy-Item (Join-Path $ExplSrc "p5.min.js") $dstExpl }
  foreach ($topic in $ExplTopics) {
    $from = Join-Path $ExplSrc $topic
    if (-not (Test-Path $from)) { Write-Warning "explainer missing: $topic"; continue }
    $td = Join-Path $dstExpl $topic
    New-Item -ItemType Directory -Force -Path $td | Out-Null
    foreach ($f in Get-ChildItem $from -File -Filter *.html) { Copy-Item $f.FullName $td }
  }
}

# catalog with exactly these books (the library page reads this list, then each book.json)
New-Item -ItemType Directory -Force -Path (Join-Path $Dst "books") | Out-Null
$json = '{ "books": [ ' + (($Books | ForEach-Object { '"' + $_ + '"' }) -join ", ") + ' ] }'
# UTF-8 without a BOM: Set-Content -Encoding UTF8 writes a BOM on Windows PowerShell 5.1
[IO.File]::WriteAllText((Join-Path $Dst "books\catalog.json"), $json, [Text.UTF8Encoding]::new($false))

$files = Get-ChildItem $Dst -Recurse -File
"books: $($Books -join ', ')"
"files: $($files.Count)"
"size:  $([math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 2)) MB"

$cacheNew = $null
$m = Select-String -Path $swDst -Pattern 'const CACHE = "([^"]+)"'
if ($m) { $cacheNew = $m.Matches[0].Groups[1].Value }
if ($cacheOld -and $cacheOld -eq $cacheNew) {
  "cache: $cacheNew (unchanged — bump const CACHE in ebook-engine/sw.js if the content changed)"
} elseif ($cacheOld) {
  "cache: $cacheOld -> $cacheNew"
} else {
  "cache: $cacheNew"
}
