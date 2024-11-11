# RSS Aggregator - For RSS or HTML feeds

Simple aggregator for **RSS** & **HTML** feeds for my own pleasure \
You can chose to use RSS aggregator to a single RSS feed by using the **rss_aggregator.py**. If you however are working with HTML blog posts (such as Microsoft blogs) you can instead chose to use **html_aggregator.py**.
Note that you have the options to chose between aggregation or appending to a ```aggregated_feed.xml```.
<br>
```hitem```

### Howto
1. Create a new GitHub repository and upload files: \
    Create a new public GitHub repository (e.g., "rss-aggregator"). You'll store the Python script, aggregated RSS feed and the workflow file in this repository.

2. Set up GitHub Pages:\
    Go to the repository settings, scroll down to the GitHub Pages section, and choose the "main" branch as the source. Save the changes, and you'll get a URL for your GitHub Pages site (e.g., https://```<username>```.github.io/rss-aggregator/).

3. Update the 'link' field in the script:
    Replace the 'link' field in the ```rss_aggregator.py``` or ```html_aggregator.py``` script with your GitHub Pages URL:
    ```python
    etree.SubElement(channel, "link").text = "https://<username>.github.io/<repo name>/aggregated_feed.xml"
    ```
4. Change to RSS or HTML feeds accordingly in ```rss_aggregator.yml```

   For HTML:
    ```python
    run: |
        python html_aggregator.py
    ```
    For RSS:
     ```python
    run: |
        python rss_aggregator.py
    ```
5. Change the timer accordingly in ```rss_aggregator.yml``` \
   The Cron job is the main one (how often it runs). But one more such setting is that links are only stored for 365 days under ```name: Update processed links file``` in the yml to prevent ```processed_links.txt``` to grow to big.
6. Chose if you want to aggregate or append ```aggregated_feed.xml``` by settings these values in top of the ```*.py``` script.\
    Aggregated (**default**), this is used to ingest the latest news where the digestion is triggered elsewhere, such as teams or slack).
    ```python
    append_mode = False
    ```
    Persistant, appending to ```aggregated_feed.xml``` (Used for feeds such as feedly to see older entries).\
    How long will the entries in ```aggregated_feed.xml``` persist to avoid growing to big.
    ```python
    append_mode = True
    max_age_days = 365
    ```
8. Then you take the link to `aggregated_feed.xml` and paste it in to your RSS hook or powerautomate flow (and digest frequenzy to match your cron configuration in `rss_aggregator.yml`) \
Example from teams: \
![image](https://github.com/hitem/rss-aggregator/assets/8977898/cb0fbc33-57a7-4012-8cf7-4f9d36a3c1e0) \
Example from powerautomate flows: \
 ![image](https://github.com/user-attachments/assets/6752ac0c-a4c9-4e63-8d83-6214b8710d47)

**Note:** You also need to set up github access token for the repo in question. Else the github action workflow will not be allowed to checkout and make pullrequests (and merge). By default it uses GITHUB_TOKEN that can be configured on your repository project: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#setting-the-permissions-of-the-github_token-for-your-repository \
I set these permissions in the workflow yml file:
```python
permissions:
 contents: write
 pages: write
 id-token: write
```
Include as few permissions as possible needed for your project.


# Current Behavior
- **Script Execution:** The cron job triggers the script every hour. The script fetches and processes RSS or HTML feed entries from the last 2 hours.
- **Link Processing:** The script writes new links to `processed_links.txt` and skips links that are already present in `processed_links.txt`.


## Customizing Timing and Frequency

This script is set up to collect links from Microsoft blog pages based on specific timing configurations. Follow these guidelines to avoid duplicates and ensure complete coverage.

### Timing Configuration

- **Collection Window (`time_threshold`)**: Collects entries from the past 2 hours.
  ```python
  time_threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
  ```
- **Cron Job Interval**: Runs every hour (`'0 */1 * * *'`), ensuring regular updates, set up in the *.yml.
- **Ingestion Frequency**: Runs every hour, aligning with the cron job to process collected entries.

### Recommended Settings

- **Standard (Hourly Updates)**:
```python
time_threshold: 2 hours 
Cron Job Interval: 1 hour 
Ingestion Frequency: 1 hour
```
- **Extended (Monthly Updates)**:
```python
time_threshold: 60 days 
Cron Job Interval: 30 days
Ingestion Frequency: 30 days
```
```Note```: First run will actually gather 60 days worth of news (or what you set time_treshold to), but every subsquent run there is filters for links that are not already present. Time_treshold need to overlap the cron job and ingestion so you dont miss anything.
```python
if pub_date >= time_threshold and link not in processed_links:
```

By following these configurations, you ensure that your aggregator captures all updates efficiently and without duplication.

