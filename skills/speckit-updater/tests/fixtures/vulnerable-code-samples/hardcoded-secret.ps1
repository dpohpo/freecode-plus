# Sample file with hardcoded secrets
# This should be detected by GitLeaks

# BAD: Hardcoded API key
$apiKey = "AWS_ACCESS_KEY_EXAMPLE"

# BAD: Hardcoded GitHub token
$githubToken = "github-token-example"

# BAD: Hardcoded password
$password = "SuperSecret123!"

# GOOD: Using environment variables (this should NOT be flagged)
$safeApiKey = $env:API_KEY
