# Build a clean, publishable copy of the reader with only the phy11 book.
$ErrorActionPreference = "Stop"
$src = "C:\Users\surat\.dsh\bot\workspace\ebook-engine"
$dst = "C:\Users\surat\.dsh\bot\workspace\deploy-phy11"

if (Test-Path $dst) {
  # keep .git so the published history survives a rebuild
  Get-ChildItem $dst -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force
} else {
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
}

# root files the web app needs
foreach ($f in @("index.html", "reader.html", "manifest.webmanifest", "sw.js", ".nojekyll")) {
  Copy-Item (Join-Path $src $f) (Join-Path $dst $f)
}
# engine, vendor libs, icons
foreach ($d in @("engine", "vendor", "assets")) {
  Copy-Item (Join-Path $src $d) (Join-Path $dst $d) -Recurse
}
# the book, without source PDFs or teacher reference crops
$bd = Join-Path $dst "books\phy11"
New-Item -ItemType Directory -Force -Path $bd | Out-Null
foreach ($f in @("book.json", "layout.json", "solutions.js", "widgets.js")) {
  Copy-Item (Join-Path $src "books\phy11\$f") (Join-Path $bd $f)
}
Copy-Item (Join-Path $src "books\phy11\pages") (Join-Path $bd "pages") -Recurse
if (Test-Path (Join-Path $src "books\phy11\media")) { Copy-Item (Join-Path $src "books\phy11\media") (Join-Path $bd "media") -Recurse }

# catalog with this book only
New-Item -ItemType Directory -Force -Path (Join-Path $dst "books") | Out-Null
'{ "books": [ "phy11" ] }' | Set-Content -Path (Join-Path $dst "books\catalog.json") -Encoding UTF8

$files = Get-ChildItem $dst -Recurse -File
"files: $($files.Count)"
"size:  $([math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 2)) MB"

