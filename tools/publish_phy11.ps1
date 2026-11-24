# Create the GitHub repo and push the clean phy11 deploy copy.
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$t = $env:DSH_SECRET_GITHUB_TOKEN
if (-not $t) { Write-Output "NO TOKEN"; exit 1 }

$h = @{
  Authorization         = "token $t"
  Accept                = "application/vnd.github+json"
  "User-Agent"          = "dsh-ebook-bot"
  "X-GitHub-Api-Version" = "2022-11-28"
}

function Scrub([string]$s) { if ($s) { $s.Replace($t, "***") } else { $s } }

try {
  $me = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $h -Method Get
} catch {
  Write-Output "auth failed: $(Scrub $_.Exception.Message)"
  exit 1
}
Write-Output "login: $($me.login)"

$repo = "physics-ebooks"
try {
  $r = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $h -Method Post -Body (@{
    name        = $repo
    description = "S4 Physics interactive e-books - step-by-step solutions on the teacher's notes"
    private     = $false
    has_issues  = $true
    auto_init   = $false
  } | ConvertTo-Json)
  Write-Output "created: $($r.full_name)"
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  Write-Output "create returned $code (may already exist)"
}

# ---- git ----
$dst = "C:\Users\surat\.dsh\bot\workspace\deploy-phy11"
Push-Location $dst
if (-not (Test-Path ".git")) { git init -q -b main 2>&1 | Out-Null }
git add -A 2>&1 | Out-Null
git -c user.name="Uni+ Education" -c user.email="noreply@uniplus.example" commit -q -m "phy11: Projectile Motion e-book (10 pages, 20 questions with worked solutions)" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Output "commit: nothing to commit or failed (continuing)" }

$url = "https://x-access-token:$t@github.com/$($me.login)/$repo.git"
git remote remove origin 2>&1 | Out-Null
git remote add origin $url
$out = (git push -u origin main --force 2>&1) -join "`n"
Write-Output (Scrub $out)
$pushCode = $LASTEXITCODE
git remote set-url origin "https://github.com/$($me.login)/$repo.git"
Pop-Location
Write-Output "push exit: $pushCode"
Write-Output "pages: https://$($me.login).github.io/$repo/reader.html?book=phy11"
