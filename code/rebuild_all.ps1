$ErrorActionPreference = 'Continue'
$d = $PSScriptRoot
Set-Location $d
$log = Join-Path $d 'out\_rebuild_log.txt'
"=== rebuild start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding utf8

function Run($script, $tag) {
    "--- $tag start $(Get-Date -Format 'HH:mm:ss')" | Out-File $log -Append -Encoding utf8
    python "$d\$script" *> "$d\out\_log_$tag.txt"
    $rc = $LASTEXITCODE
    "--- $tag end rc=$rc $(Get-Date -Format 'HH:mm:ss')" | Out-File $log -Append -Encoding utf8
}

Run 'build_ext.py' 'b_ext'
Run 'build_ext_cyc.py' 'b_cyc'
Run 'run_ext.py' 'run'
Run 'run_ext_extra.py' 'extra'
Run 'run_ext_tail2.py' 'tail2'
Run 'build_ext10.py' 'b_ext10'
Run 'build_ext_cyc10.py' 'b_cyc10'
Run 'run_x10.py' 'run10'
"=== all done $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
