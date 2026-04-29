from parser import run


### Sofware engineer python in Netherlands, past week, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3&f_TPR=r86400&f_WT=3%2C1%2C2&geoId=102890719&keywords=Software%20Engineer%20python&origin=JOB_SEARCH_PAGE_JOB_FILTER"
### Finance business partner in Netherlands, past day, all experience levels
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=3%2C4&f_TPR=r86400&keywords=finance%20business%20partner&origin=JOB_SEARCH_PAGE_JOB_FILTER"
#### Python AND (software OR%20backend OR engineer OR simulation)%20AND%20Netherlands
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Python%20AND%20(software%20OR%20backend%20OR%20engineer%20OR%20simulation)%20AND%20Netherlands&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true"
#### Somilation software engineer in Netherlands, past day, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Simulation%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true"
#### Engineering software engineer in Netherlands, past day, entry associate level
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Engineering%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Research%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Scientific%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Application%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&trk=d_flagship3_salary_explorer"
# JOB_URL = "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Netherlands%20AND%20Python%20AND%20automotive%20AND%20simulation&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20AND%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=traffic%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=traffic%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20modeller%20python&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=transport%20modeller&origin=JOBS_HOME_KEYWORD_HISTORY"
JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=automotive%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation&origin=JOBS_HOME_KEYWORD_HISTORY"
# JOB_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation%20python&origin=JOBS_HOME_KEYWORD_HISTORY"

search_dict = {
    # "search_1": "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r86400&geoId=102890719&keywords=Python%20Engineer&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_2": "https://www.linkedin.com/jobs/search/?distance=25.0&f_E=2%2C3&f_TPR=r86400&geoId=102890719&keywords=software%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "search_3": "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3&f_TPR=r86400&f_WT=3%2C1%2C2&geoId=102890719&keywords=Software%20Engineer%20python&origin=JOB_SEARCH_PAGE_JOB_FILTER",
    "search_4": "https://www.linkedin.com/jobs/search/?f_E=3%2C4&f_TPR=r86400&keywords=finance%20business%20partner&origin=JOB_SEARCH_PAGE_JOB_FILTER",
    "search_5": "https://www.linkedin.com/jobs/search/?f_E=1%2C2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Python%20AND%20(software%20OR%20backend%20OR%20engineer%20OR%20simulation)%20AND%20Netherlands&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true",
    "search_6": "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Simulation%20Software%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true",
    "search_7": "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Engineering%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "search_8": "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Research%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "search_9": "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Scientific%20Software%20Developer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "search_10": "https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Application%20Engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&trk=d_flagship3_salary_explorer",
    "search_11": "https://www.linkedin.com/jobs/search/?distance=25&f_E=2%2C3%2C4&f_TPR=r86400&geoId=102890719&keywords=Netherlands%20AND%20Python%20AND%20automotive%20AND%20simulation&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true",
    "search_12": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20AND%20python&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_13": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_14": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=civil%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_15": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=traffic%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_16": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=traffic%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_17": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20engineer%20python&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_18": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=transport%20modeller%20python&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_19": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=transport%20modeller&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_20": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r604800&geoId=102890719&keywords=automotive%20engineer&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_21": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation&origin=JOBS_HOME_KEYWORD_HISTORY",
    "search_22": "https://www.linkedin.com/jobs/search/?currentJobId=4259503283&distance=25.0&f_TPR=r86400&geoId=102890719&keywords=automotive%20simulation%20python&origin=JOBS_HOME_KEYWORD_HISTORY",

}

def run_looping():
    for search_name, search_url in search_dict.items():
        run(search_url)


if __name__ == "__main__":
    run_looping()