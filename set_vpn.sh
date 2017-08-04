. venv/bin/activate

export AWS_DEFAULT_PROFILE=afdezl

sceptre --var-file=variables.yaml update-stack pers/ew2 recordsets
sceptre --var-file=variables.yaml update-stack pers/ew2 vpn

deactivate
