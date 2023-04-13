# RSS Aggregator

Simple aggregator for RSS feeds for my own pleasure \
In my example we use Microsoft tech blogs \
https://techcommunity.microsoft.com/t5/security-compliance-and-identity/ct-p/MicrosoftSecurityandCompliance
<br>
```hitem```

### Howto
1. Create a new GitHub repository and upload files: \
    Create a new public GitHub repository (e.g., "rss-aggregator"). You'll store the Python script, aggregated RSS feed and the workflow file in this repository. \
    Personally, i ran the python script localy to generate the ```aggregated_feed.xml``` file - but the workflow should be able to do that for you, but maybe you dont want to wait. If you do so you have to install:
    > pip install feedparser lxml

    then run 
    > python3 rss_aggregator.py

2. Set up GitHub Pages:\
    Go to the repository settings, scroll down to the GitHub Pages section, and choose the "main" branch as the source. Save the changes, and you'll get a URL for your GitHub Pages site (e.g., https://```<username>```.github.io/rss-aggregator/).
3. Update the 'link' field in the script:
    Replace the 'link' field in the ```rss_aggregator.py``` script with your GitHub Pages URL:
    ```python
    etree.SubElement(channel, "link").text = "https://<username>.github.io/<repo name>/aggregated_feed.xml"
    ```
4. Update the workflow:\
   Change the timer accordingly in ```rss_aggregator.yml```
