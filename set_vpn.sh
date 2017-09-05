. venv/bin/activate

export AWS_DEFAULT_PROFILE=<YOUR_PROFILE>

sceptre --var-file=variables.yaml update-stack prod/ew2 vpn

deactivate
