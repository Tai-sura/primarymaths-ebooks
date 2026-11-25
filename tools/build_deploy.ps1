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
  # The deploy clone is the published copy of this repo. Keep only its git history:
  # every tracked folder is rebuilt from the source below. Keeping tools/ and docs/
  # here (the rule until 2026-11-25) left the deploy clone on a stale copy of the
  # scripts - its extract_pages.py was 17 KB while the source one was 34 KB.
  $keep = @(".git", ".gitignore")
  Get-ChildItem $Dst -Force | Where-Object { $keep -notcontains $_.Name } | Remove-Item -Recurse -Force
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

# the authoring side that also lives in the published repo: the scripts and docs
# readers of the repo see. Copied fresh every build, then the QA sandbox and the
# python caches are dropped - they are never published.
foreach ($d in @("tools", "docs", ".cursor")) {
  $from = Join-Path $Src $d
  if (Test-Path $from) { Copy-Item $from (Join-Path $Dst $d) -Recurse }
}
foreach ($junk in @("tools\qa\node_modules", "tools\__pycache__", "tools\qa\__pycache__")) {
  $p = Join-Path $Dst $junk
  if (Test-Path $p) { Remove-Item $p -Recurse -Force }
}
# A `_`-prefixed script is a scratch harness someone ran once for a screenshot or
# a pixel probe; it must never reach the public repo (one such file shipped the
# source of a diagnostic that only made sense on the author's machine).
Get-ChildItem (Join-Path $Dst "tools") -Recurse -File -Include "_*.py", "_*.mjs", "_*.html" -ErrorAction SilentlyContinue |
  Remove-Item -Force -ErrorAction SilentlyContinue

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
  # `extract_pages.py` rewrites layout.json without the stamps; `answer_stamps.py`
  # puts them back. Shipping the one without them leaves every fill-in answer
  # invisible, which is exactly what a reader never notices until it is too late.
  # Counted with a plain match: PowerShell 5.1's ConvertFrom-Json rejects this file.
  $bookPath = Join-Path $bd "book.json"
  $layoutPath = Join-Path $bd "layout.json"
  if ((Test-Path $bookPath) -and (Test-Path $layoutPath)) {
    $bookText = [IO.File]::ReadAllText($bookPath)
    if ($bookText -match '"answerStamps"\s*:\s*\[') {
      $layoutText = [IO.File]::ReadAllText($layoutPath)
      $stamped = ([regex]::Matches($layoutText, '"stamps"\s*:\s*\[')).Count
      if ($stamped -lt 1) {
        throw "books/${id}: layout.json has no stamps but book.json lists answerStamps - run tools/answer_stamps.py ${id} before building"
      }
      Write-Output "  ${id}: $stamped stamped answer(s) in the layout"
    }
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
