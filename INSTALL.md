# Installing CommunityBuilder.Models in the API

After pushing this repo to GitHub, you can install it into your API (e.g. CommunityBuilder.API) by providing the repo path.

## In the API's `requirements.txt`

```txt
# Install from GitHub (main branch)
git+https://github.com/YOUR_USERNAME/CommunityBuilder.Models.git

# Or pin to a specific branch
git+https://github.com/YOUR_USERNAME/CommunityBuilder.Models.git@main

# Or pin to a tag (e.g. after you tag v0.1.0)
git+https://github.com/YOUR_USERNAME/CommunityBuilder.Models.git@v0.1.0
```

Replace `YOUR_USERNAME` with your GitHub username (or org) and `CommunityBuilder.Models` with the actual repo name if different.

## From the command line

From your API project directory:

```bash
pip install git+https://github.com/YOUR_USERNAME/CommunityBuilder.Models.git
```

Then in your API code you can use:

```python
from app_models.account.models import User
from app_models.community.models import Community
# etc.
```
